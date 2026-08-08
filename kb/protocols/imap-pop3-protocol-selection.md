---
title: "现在还应该给用户开 POP3 吗？IMAP 与 POP3 到底怎么选？"
source: "https://ztpop.net/kb/imap-pop3-protocol-selection.html"
license: CC-BY 4.0
---

# 现在还应该给用户开 POP3 吗？IMAP 与 POP3 到底怎么选？

1
现在还应该给用户开 POP3 吗？IMAP 与 POP3 到底怎么选？
▼

**两个协议的基本形态**

RFC 1939 第 3 节（Basic Operation）描述 POP3：服务器在 TCP 110 端口监听，客户端建立 TCP 连接后服务器发出问候，随后双方交换命令与响应直到连接关闭或中止；命令由大小写不敏感的关键字加可选参数构成，以 CRLF 结束。RFC 9051（IMAP4rev2）第 2.1 节（Link Level）说明：IMAP4rev2 连接由客户端发起，连接到**143 端口（明文端口）或 993 端口（隐式 TLS 端口）**上的服务器监听。**端口不同只是表象，真正的差异在于「邮件放在哪里、由谁管理状态」。**

**规范自己承认的 POP3 能力边界**

RFC 1939 第 8 节（Scaling and Operational Considerations）有一段很直接的自述：用户与客户端厂商发现，**组合使用 UIDL 命令并且不发 DELE 命令，可以得到一种「把邮件投递区当作半永久仓库」功能的弱化版本**，而这种功能通常与 IMAP 相关联；但同节紧接着指出，**IMAP 的其他能力——例如在已有连接上轮询新到邮件、在服务器上支持多个文件夹——在 POP3 中并不存在**。也就是说，「POP3 保留副本在服务器」并不等于 IMAP，它缺少多文件夹与实时新邮件通知这两项结构性能力。

**把 POP3 当仓库用的运维后果**

同样在第 8 节：当普通用户这样使用时，**已读邮件会在服务器上无节制地累积**，从服务器运营者的角度看这显然是不可取的行为模式；而且这种局面还会被另一事实加剧——**POP3 的有限能力不允许高效处理含有成百上千封邮件的投递区**。因此规范建议大规模多用户服务器（尤其是用户只能通过 POP3 访问投递区的场合）考虑两类措施：对每用户投递区实施存储配额之类的限制（并提醒采用此选项的站点应设法告知用户配额即将耗尽或已耗尽，例如向用户投递区插入一封提示邮件）；以及制定并执行站点级的服务器邮件保留策略。

**选型判据**

把规范文本转成判据：**需要多设备同时访问、需要服务器端文件夹与已读/标记状态同步、需要在已有连接上感知新邮件的场景，选 IMAP**——这三项能力 POP3 按 RFC 1939 第 8 节的自述并不具备。**只有单一终端取信、且明确要求邮件落到本地并从服务器移除的场景，POP3 才是合适的**；一旦允许「保留副本」，就必须同步配好配额与保留策略，否则服务端存储会被无限增长的已读邮件拖垮。

**无论选哪个，传输都必须加密**

NIST SP 800-177 Rev.1《Trustworthy Email》给出的 Security Recommendation 7-1 写明：**IMAP 与 POP3 客户端应当使用 TLS 连接服务器**，并配合该文件第 5.2 节「邮件传输安全」所述的全套保护措施；**使用未加密的 TCP 连接并以用户名口令认证的做法被强烈劝阻**。同文件 Security Recommendation 7-3 补充：用于加密持久化存储（例如邮箱）中数据的密钥，**应当**与用于邮件传输的密钥相区分。

参考：https://www.rfc-editor.org/rfc/rfc1939.txt 、https://www.rfc-editor.org/rfc/rfc9051.txt 与 https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-177r1.pdf

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-pop3-protocol-selection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
