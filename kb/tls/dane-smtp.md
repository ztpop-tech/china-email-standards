---
title: "DANE for SMTP：基于DNSSEC的邮件传输安全"
source: "https://ztpop.net/kb/dane-smtp.html"
license: CC-BY 4.0
---

# DANE for SMTP：基于DNSSEC的邮件传输安全

摘要：邮件在 SMTP 服务器之间传输时，传统上依赖机会性 TLS（Opportunistic TLS），即发送服务器尝试与接收服务器建立 TLS 加密连接，但无法验证接收服务器的证书真实性——任何中间人攻击者（MITM）都可以提供自签名证书并成功完成 TLS 握手，导致传输内容被窃听或篡改。DANE for SMTP（RFC 7672）通过在 DNSSEC 签名的 DNS 区域中发布 TLSA 记录，解决了这一安全漏洞，使发送服务器能够强制验证接收服务器的 TLS 证书，从根本上消除基于证书信任链的中间人攻击。

**一、DANE 工作原理：TLSA 记录的魔法**
DANE（DNS-based Authentication of Named Entities）的核心思想是利用 DNSSEC 保障的 DNS 数据完整性，将 TLS 证书的验证信息直接存储在 DNS 中。对于 SMTP，域名所有者在其 DNSSEC 签名的 DNS 区域中发布一条特殊的 TLSA 记录，位于 \_25.\_tcp.mx.example.com 这样的特定名称下（25 是 SMTP 端口号）。这条 TLSA 记录包含：证书使用模式（Usage Field）、选择器（Selector Field）、匹配类型（Matching Type Field）和证书关联数据（Certificate Association Data）。当发送邮件服务器连接到接收服务器（该服务器的名称来自 MX 记录）时，发送服务器查询该 MX 主机名对应的 TLSA 记录，并将 TLSA 记录中的证书关联数据与实际 TLS 握手中收到的证书进行比对，匹配成功才继续邮件传输。

**二、DNSSEC 前置条件**
DANE 的安全性完全依赖于 DNSSEC——如果 DNS 区域没有 DNSSEC 签名，TLSA 记录可以被中间人伪造，DANE 的安全性就无从谈起。因此，部署 DANE for SMTP 的第一步是确保域名（尤其是 MX 记录指向的邮件服务器主机名所在区域）已经正确配置了 DNSSEC。DNSSEC 的部署涉及：在域名注册商处启用 DNSSEC，上传 DS（Delegation Signer）记录；在 DNS 服务器（如 BIND、PowerDNS、Knot DNS）中为区域启用 DNSSEC 签名；定期进行密钥轮换（ZSK 轮换和 KSK 轮换）。只有在 DNSSEC 签名链完整的区域中发布的 TLSA 记录才被 DANE 验证所信任。如果解析器在查询 TLSA 记录时发现 DNSSEC 验证失败（如签名过期、签名不匹配），DANE 验证应视为失败，回退行为取决于具体配置（安全模式 vs 机会模式）。

**三、TLSA 记录详解：四种证书使用模式**
RFC 7672 和 RFC 6698 定义了 TLSA 记录的四个字段。证书使用模式（Certificate Usage）是最关键的字段，决定了如何解释证书关联数据：Usage 0（CA Constraint）——指定了允许签发服务器证书的 CA 证书，发送方验证服务器证书必须由该 CA 或其子 CA 签发，类似于 HTTP 的公钥固定（HPKP）但绑定在 DNS 层面；Usage 1（Service Certificate Constraint）——指定了服务器必须使用的确切终端实体证书（或公钥），验证最严格；Usage 2（Trust Anchor Assertion）——指定了用作信任锚的 CA 证书，由域所有者自建私有 CA 并声明该 CA 为信任锚，不依赖公共 CA；Usage 3（Domain-Issued Certificate）——指定了服务器证书本身或其公钥，仅限域所有者自行签发的证书（如自签名证书），不涉及外部 CA。

对于 SMTP，RFC 7672 要求 DANE 验证必须遵守以下规则：Usage 2（DANE-TA, Trust Anchor Assertion）和 Usage 3（DANE-EE, Domain-Issued Certificate）均可使用。Usage 0 和 Usage 1 在 SMTP DANE 中不被允许，因为它们的语义在 SMTP 场景下存在安全风险。选择器字段（Selector）指示使用完整的 X.509 证书（Selector 0）还是仅使用 SubjectPublicKeyInfo 公钥部分（Selector 1）。匹配类型字段（Matching Type）指示如何匹配——完整值（Type 0）、SHA-256 哈希（Type 1）或 SHA-512 哈希（Type 2）。实际部署中最常见的 TLSA 记录组合是 Usage 3 + Selector 1 + Matching Type 1，即使用域自签发证书的公钥 SHA-256 哈希。

**四、与 MTA-STS 的对比与互补**
DANE 和 MTA-STS（RFC 8461）都是为了解决 SMTP 的 TLS 降级攻击和中间人攻击问题而设计的，但采取了不同的技术路径。DANE 依赖 DNSSEC 保护 TLSA 记录的完整性，信任锚在 DNS 体系内。MTA-STS 依赖 HTTPS 和 Web PKI 保护策略文件的完整性，信任锚在公共 CA 体系内。两者都是可信的邮件传输安全方案，各有优劣。DANE 的优势在于：不依赖任何第三方 CA，域所有者完全自主控制证书验证策略；使用 DNSSEC 签名的 DNS 记录分发，与 DNS 缓存机制良好兼容。DANE 的劣势在于：依赖 DNSSEC 的广泛部署——如果目标域没有 DNSSEC，DANE 完全无法使用，而全球 DNSSEC 部署率至今仍不理想。

MTA-STS 的优势在于：不依赖 DNSSEC，方便域所有者快速部署（只需添加 DNS TXT 记录和在 Web 服务器上放置策略文件）；利用公共 CA 体系，与现有 PKI 基础设施良好兼容。MTA-STS 的劣势在于：依赖公共 CA 体系，如果某个 CA 被攻破或恶意签发证书，MTA-STS 验证可能被绕过。在实际部署中，DANE 和 MTA-STS 可以同时配置，提供双重保护——邮件发送方如果同时支持两者，可以先用 DANE 验证（如果在 DNSSEC 区域发现了 TLSA 记录），否则回退到 MTA-STS 验证，最后才尝试传统的无验证 TLS。Postfix 的 smtp\_tls\_security\_level = dane 配置实现了完整的 DANE 支持。

**五、Postfix DANE 配置实践**
在 Postfix 中启用 DANE 出站验证（作为发送方）需要以下配置：smtp\_tls\_security\_level = dane（启用出站 DANE 验证）；smtp\_dns\_support\_level = dnssec（确保 DNS 查询通过支持 DNSSEC 的解析器进行）；smtp\_tls\_CAfile = /etc/ssl/certs/ca-certificates.crt（需要系统 CA 证书包，用于验证 Usage 2 场景下的 CA 证书）。配置完成后，Postfix 在向支持 DANE 的接收邮件服务器发送邮件时，会自动查询 TLSA 记录并验证服务器证书。如果 DANE 验证失败，Postfix 会拒绝发送并返回延迟错误，管理员可以从邮件日志中看到类似 "TLSA lookup error" 或 "certificate does not match TLSA record" 的信息。

作为接收方，需要在自己的 DNS 区域中发布 TLSA 记录。Dovecot/Postfix 接收端本身不需要特殊配置——只要邮件服务器正确配置了 TLS 证书（可以是 Let's Encrypt 签发的，也可是自签名的），并在 DNS 中正确设置了 TLSA 记录即可。生成 TLSA 记录的工具包括：swaks 的 --tls-get-peer-cert 获取服务器证书后使用 openssl x509 -pubkey 提取公钥并计算 SHA-256 哈希；或使用专门工具如 hash-slinger 的 tlsa 命令：tlsa --create --certificate /path/to/cert.pem \_25.\_tcp.mx.example.com。生成的 TLSA 记录格式如：\_25.\_tcp.mail.example.com. IN TLSA 3 1 1 ( AB12CD34... )。

**六、DANE 部署现状与展望**
全球 DANE for SMTP 的部署率正在稳步增长。根据瑞典互联网基金会（Internetstiftelsen）的统计数据，截至 2025 年，全球前 100 万域名的入站邮件 DANE 部署率约为 5%-8%，以德国（.de 域名）和荷兰（.nl 域名）为代表的欧洲国家部署率最高（超过 15%）。大型邮件服务商中，德国的 mailbox.org、Posteo.de、Tutanota 以及荷兰的许多政府和教育机构的邮件服务器均已部署 DANE。美国的 Google Gmail 和 Microsoft Exchange Online 尚未全面部署 DANE（它们使用 MTA-STS 等其他机制），但由于 DANE 是出站验证为主，只要发送方支持 DANE，就能在向已部署 DANE 的接收方发送邮件时获得保护。

DANE 的未来发展受到 DNSSEC 推广的直接影响。随着 ICANN 和各国家顶级域名注册局持续推广 DNSSEC，以及 Let's Encrypt 等免费证书颁发机构降低了 TLS 证书获取门槛，DANE 的门槛也在同步降低。对于自主管理邮件服务器的组织，部署 DANE 是提升邮件传输安全性的最具性价比的措施之一——不需要购买昂贵的证书，不需要依赖第三方 CA，只需确保 DNSSEC 正确配置并发布 TLSA 记录即可获得证书固定级别的中间人攻击防护。

总结：DANE for SMTP 通过将 TLS 证书验证锚定在 DNSSEC 保护的 DNS 中，消除了 SMTP 传输中对公共 CA 的信任依赖。与 MTA-STS 互补部署可以构建完整的邮件传输安全策略。虽然 DNSSEC 的部署率限制了大范围采用，但对于有能力管理 DNSSEC 的组织，DANE 是提升邮件传输安全性的强有力工具。

对于有能力管理 DNSSEC 的组织，部署 DANE 的最简路径是在邮件系统的 TLS 配置面板中启用 DANE 验证。以为例，管理员在
**TLS 安全配置**
界面中开启 DANE 出站验证后，系统会自动对所有启用 DNSSEC 的接收域执行 TLSA 记录查询和证书绑定验证，无需手动配置每个域的验证策略。系统还提供了 DANE 验证成功率统计面板，帮助管理员评估 DANE 对整体邮件安全性的提升效果。

**参考来源**
RFC 7672 - SMTP Security via Opportunistic DANE TLS; RFC 6698 - The DNS-Based Authentication of Named Entities (DANE) Transport Layer Security (TLS) Protocol: TLSA; RFC 8461 - SMTP MTA Strict Transport Security (MTA-STS); Postfix TLS 文档 (http://www.postfix.org/TLS\_README.html); Internetstiftelsen DANE 统计数据 (https://stats.dns.se/dane/)。

了解更多邮件技术实践，请访问知识库或联系

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-smtp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
