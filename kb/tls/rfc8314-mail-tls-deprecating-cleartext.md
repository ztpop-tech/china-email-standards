---
title: "RFC 8314 为什么主张用隐式 TLS 取代 STARTTLS？明文服务如何退役？"
source: "https://ztpop.net/kb/rfc8314-mail-tls-deprecating-cleartext.html"
license: CC-BY 4.0
---

# RFC 8314 为什么主张用隐式 TLS 取代 STARTTLS？明文服务如何退役？

1
RFC 8314 为什么主张用隐式 TLS 取代 STARTTLS？明文服务如何退役？
▼

**为何转向隐式 TLS**

RFC 8314 §3 指出：早期标准（RFC 2595、RFC 3207、RFC 3501）采用 STARTTLS，客户端先建立**明文**应用会话，再根据服务器能力与自身配置决定是否发出 `STARTTLS` 升级。文档认为「在连接建立瞬间即于独立端口协商 TLS」的替代机制（本文称 **Implicit TLS，隐式 TLS**）在现网部署得更成功；为推广加密并统一用法，该规范转而推荐 MUA 与邮件服务提供方（MSP）之间的 POP、IMAP、SMTP 提交及其他协议一律使用隐式 TLS。

**三种协议的隐式 TLS 端口与握手时序**

* **POP（§3.1）**：`pop3s` 默认端口 **995**，TCP 建连后立即握手；客户端 MUST 实现 RFC 7817 的证书校验；TLS 建立后 POP3 报文作为 TLS 应用数据传输。服务器发出 `+OK` 问候后，**即便握手时已提供客户端证书，双方仍 MUST 进入 AUTHORIZATION 状态**。
* **IMAP（§3.2）**：`imaps` 默认端口 **993**，同样立即握手。若握手中客户端证书被服务器接受，服务器 *MAY* 发出 `PREAUTH` 问候，双方直接进入 AUTHENTICATED 状态；若发 `OK` 问候则进入 NOT AUTHENTICATED 状态。
* **SMTP 提交（§3.3）**：`submissions` 服务默认端口 **465**，握手后按 RFC 6409 交换提交协议数据。服务名遵循「原服务名后加 s」的惯例，由本文 §7.3 完成注册。

**587 与 465 的过渡关系**

§3.3 明确：由于 465 端口的历史原因，`STARTTLS` on 587 目前部署面更广，这与 IMAP/POP 上隐式 TLS 反而比 STARTTLS 更普及的情况相反。文档主张长期迁移到隐式 TLS，但为最大化提交环节的加密覆盖，**在数年过渡期内客户端与服务器 SHOULD 同时实现 587 的 STARTTLS 与 465 的隐式 TLS**。关键结论是：*只要实现正确、且双方都配置为「必须成功协商 TLS 后才允许提交」，587+STARTTLS 与 465+隐式 TLS 的安全属性并无显著差异*。465 提供的是 RFC 6409 定义的 MSA，故 RFC 6409 对 MSA 的要求同样适用。

**明文与低版本 TLS 的退役方法（§4.1）**

退役手段允许各 MSP 依用户群体情况自定，可采取渐进式：逐步扩大「禁止通过明文实例认证」的用户范围，倒逼其迁移到隐式 TLS；明文服务最终应**停用**，或**严格限定给无法升级的遗留系统**。两条硬性要求值得注意：

* 当某用户的明文认证能力被撤销后，服务器**MUST NOT 在明文通道上透露其凭据是否有效**——用错误凭据与正确凭据尝试，必须返回**完全相同**的拒绝提示，防止明文通道沦为口令探测器。
* 此前以明文口令认证的用户，若旧口令可能已泄露，迁移到 TLS 时 SHOULD 强制改密。文档直言：对于任何通过公网明文收发邮件的大型用户群，**应假定其中至少一部分口令已被攻陷**。

SSL/TLS 1.0 的下线可用类似方式：或直接拒绝声明为 SSL/TLS 1.0 的 ClientHello；或先接受握手、在认证阶段再拒绝（提示更友好，但可能让口令暴露在已知不安全的通道上）。文档建议**新用户从一开始就要求 TLS 1.1 及以上**。

**客户端证书与 Received 记录**

§4.2：提交服务器与访问服务器 MAY 在隐式 TLS 端口上启用客户端证书认证，但除非服务器确已配置为接受某些客户端证书作为充分认证、且具备把证书映射到邮件授权身份的能力，否则**MUST NOT 在握手中索要客户端证书**；一旦接受证书作为授权依据，服务器 MUST 启用 SASL `EXTERNAL` 机制（IMAPS 服务器 MAY 改以 `PREAUTH` 问候替代）。§4.3：RFC 3848 的 `ESMTPS` 传输类型只能证明「用过 TLS」，而 TLS 本身并不等同于机密性保障，因此本文进一步为 `Received` 头字段注册了记录 TLS 密码套件的子句（§7.4），使链路安全强度可被追溯审计。

参考：RFC 8314《Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access》，https://www.rfc-editor.org/rfc/rfc8314 —— 章节 3 / 3.1–3.4 / 4.1 / 4.2 / 4.3 / 7.3

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8314-mail-tls-deprecating-cleartext.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
