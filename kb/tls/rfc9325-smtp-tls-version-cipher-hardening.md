---
title: "邮件传输的 TLS 版本与密码套件应该怎么配置？"
source: "https://ztpop.net/kb/rfc9325-smtp-tls-version-cipher-hardening.html"
license: CC-BY 4.0
---

# 邮件传输的 TLS 版本与密码套件应该怎么配置？

1
邮件传输的 TLS 版本与密码套件应该怎么配置？
▼

**先分清三个不同的 TLS 场景**

「邮件的 TLS」不是一件事，而是三类语义完全不同的连接，配置基线也不同：

* **MTA 之间的传输（25 端口）**：由 RFC 3207 定义的 STARTTLS 扩展提供。其本质是**机会式加密**——对端支持就加密，不支持就明文投递，且默认不严格校验证书。这是历史兼容性的产物，安全性需靠 MTA-STS（RFC 8461）或 DANE for SMTP（RFC 7672）额外加固。
* **用户提交（Submission）**：RFC 8314 明确主张明文已过时，要求邮件提交与访问使用 TLS。这里是**强制加密且必须校验证书**的场景，与 MTA 之间的机会式加密有本质区别。
* **用户访问（IMAP / POP3）**：同 RFC 8314，同样强制并校验。

把这三类混为一谈是最常见的配置错误来源：在 25 端口上强制要求高版本 TLS 会直接造成对部分外部域投递失败，而在提交端口上沿用机会式的宽松策略则等于把用户凭据暴露在可降级的通道上。

**版本基线：RFC 8996 与 RFC 9325**

两份文档同属 BCP 195，共同构成当前的版本基线：

* **RFC 8996《Deprecating TLS 1.0 and TLS 1.1》**（2021 年 3 月）正式弃用 TLS 1.0 与 TLS 1.1。该文档更新了数量极多的既有 RFC，其中包括邮件相关规范，意味着**这些旧版本在邮件协议中同样不再被认可**。
* **RFC 9325**（2022 年 11 月，取代 RFC 7525）给出当前 TLS 与 DTLS 的安全使用建议：SSL 2.0 与 SSL 3.0 必须不再使用；TLS 1.0 与 TLS 1.1 不得使用；**TLS 1.2 为可接受的最低版本，TLS 1.3 为推荐版本**（TLS 1.3 由 RFC 8446 定义）。

邮件侧的现实约束是：**互联网 MTA 生态的版本分布不由本方决定。**因此在 25 端口的入站方向可以要求 TLS 1.2 起步（本方是服务端，可控），而在出站方向若强行拒绝低版本，结果是邮件投不出去。合理做法是出站保留降级能力但**全量记录协商到的版本与套件**，用数据驱动地识别哪些对端仍在使用旧版本，再逐个推动，而不是一刀切。

**密码套件与密钥交换**

RFC 9325 在算法层面的方向性建议包括：

* **使用 AEAD 类算法**：优先选择提供认证加密的套件，避免仍在使用的 CBC 模式组合。
* **要求前向保密**：密钥交换应使用临时（ephemeral）形式的 Diffie-Hellman，使长期私钥泄露不导致历史会话被解密。这对邮件尤其重要，因为邮件内容长期具有价值。
* **禁用已知弱算法与弱参数**：包括 NULL、导出级、RC4、单/双 DES 等，以及过短的 DH 参数。
* **禁用压缩、谨慎处理会话恢复与重协商**。
* **TLS 1.3 简化了这一层**：其套件集合本身已排除上述弱选项并强制前向保密，这是推荐尽快启用 1.3 的实际理由之一。

NIST SP 800-52 Rev. 2（2019 年 8 月，McKay 与 Cooper）从选型、配置与使用三个角度给出 TLS 实现指南，可作为配置基线的第二参照，尤其适用于需要满足美国联邦相关要求的环境。两份文档在方向上一致：**收敛套件集合、强制前向保密、淘汰旧版本。**

**证书与身份校验：机会式 TLS 的真正短板**

一个必须讲清的事实：**MTA 之间的机会式 STARTTLS 默认只提供「防被动窃听」，不提供「防主动中间人」。**原因是发送方通常不校验对端证书——校验失败就投不出去，而 MX 记录本身也未经认证。攻击者若能操纵网络路径或 DNS 应答，可以：

* **剥离 STARTTLS**：在明文的 EHLO 响应中抹去 STARTTLS 能力宣告，使会话退回明文；
* **冒充对端**：出示任意证书，因为无人校验。

解决路径有两条，二者可并存：**MTA-STS**（RFC 8461）通过 HTTPS 发布策略，声明本域要求 TLS 且给出可接受的 MX 主机名，发送方据此在 enforce 模式下拒绝降级与不匹配；**DANE for SMTP**（RFC 7672）借助 DNSSEC 在 DNS 中发布 TLSA 记录来锚定证书，其信任来自 DNSSEC 链而非公共 CA。**没有这两者之一，25 端口上的 TLS 只能算加密，不能算认证。**

相比之下，提交与访问端口（Submission / IMAPS）不存在这个问题：客户端必须校验服务器证书链与主机名，配置上应确保证书覆盖用户实际使用的所有主机名，并及时轮换。

**可执行的配置与验证清单**

1. **分端口设定不同基线**：入站 25 端口——支持 STARTTLS，服务端侧下限 TLS 1.2；提交与访问端口——强制 TLS，下限 TLS 1.2，禁止明文认证。
2. **启用 TLS 1.3**：与 TLS 1.2 并存，让能用的对端优先用上。
3. **关闭 SSL 3.0 / TLS 1.0 / TLS 1.1**：依据 RFC 8996。
4. **收敛套件列表**：只保留 AEAD 且具备前向保密的套件，服务端按安全性排序并由服务端决定优先级。
5. **出站保留降级但全量记录**：把每次投递协商到的 TLS 版本、套件、对端主机名与证书校验结果写入日志。**没有这份数据，任何加密治理都无法推进。**
6. **部署 MTA-STS 或 DANE**：先以 testing 模式发布 MTA-STS 策略并接收 TLS-RPT 报告，确认无投递损失后再切 enforce。
7. **证书生命周期自动化**：证书过期是邮件 TLS 中断最常见的单一原因，签发与部署必须自动化并配到期告警。
8. **变更后实测**：用 `openssl s_client -starttls smtp -connect host:25` 逐一验证协商结果与证书链，并对提交、IMAP 端口分别复测，不要只测一个端口就宣告完成。

参考：RFC 9325《Recommendations for Secure Use of Transport Layer Security (TLS) and Datagram Transport Layer Security (DTLS)》，Y. Sheffer、P. Saint-Andre、T. Fossati，2022 年 11 月，BCP 195（取代 RFC 7525），DOI 10.17487/RFC9325，https://www.rfc-editor.org/rfc/rfc9325.html ；RFC 8996《Deprecating TLS 1.0 and TLS 1.1》，K. Moriarty、S. Farrell，2021 年 3 月，BCP 195，https://www.rfc-editor.org/rfc/rfc8996.html ；RFC 8446《The Transport Layer Security (TLS) Protocol Version 1.3》，E. Rescorla，2018 年 8 月，https://www.rfc-editor.org/rfc/rfc8446.html ；RFC 3207《SMTP Service Extension for Secure SMTP over Transport Layer Security》，P. Hoffman，2002 年 2 月，https://www.rfc-editor.org/rfc/rfc3207.html ；RFC 8314《Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access》，2018 年 1 月，https://www.rfc-editor.org/rfc/rfc8314.html ；RFC 8461《SMTP MTA Strict Transport Security (MTA-STS)》，2018 年 9 月，https://www.rfc-editor.org/rfc/rfc8461.html ；RFC 7672《SMTP Security via Opportunistic DNS-Based Authentication of Named Entities (DANE) Transport Layer Security (TLS)》，V. Dukhovni、W. Hardaker，2015 年 10 月，https://www.rfc-editor.org/rfc/rfc7672.html ；NIST SP 800-52 Rev. 2《Guidelines for the Selection, Configuration, and Use of Transport Layer Security (TLS) Implementations》，K. McKay、D. Cooper，2019 年 8 月，DOI 10.6028/NIST.SP.800-52r2，https://csrc.nist.gov/pubs/sp/800/52/r2/final

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc9325-smtp-tls-version-cipher-hardening.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
