---
title: "邮件客户端怎么「只填账号密码」就自动配好收发？SRV 自动发现的原理是什么？"
source: "https://ztpop.net/kb/email-client-autoconfig-rfc6186.html"
license: CC-BY 4.0
---

# 邮件客户端怎么「只填账号密码」就自动配好收发？SRV 自动发现的原理是什么？

1
邮件客户端怎么「只填账号密码」就自动配好收发？SRV 自动发现的原理是什么？
▼

**用 SRV 记录做客户端自动配置**

RFC 6186 标题即「Use of SRV Records for Locating Email Submission/Access Services」，它规定如何用 DNS SRV 资源记录定位邮件提交与访问服务，从而让邮件用户代理（MUA）自动完成配置（RFC 6186 第 3 节开头）。SRV 记录的优先级（priority）字段同样可用于在多个服务器间选择。

**提交服务 \_submission.\_tcp**

RFC 6186 第 3.1 节新增一个提交（submission）SRV 服务标签，标识遵循 RFC 4409 的邮件提交代理（MSA）。规范示例为 `_submission._tcp SRV 0 1 587 mail.example.com.`，即提交端口 587。MUA 预期把外发邮件提交给 MSA（587）而非直接使用 SMTP 端口 25。

**IMAP 与 POP3 访问服务**

RFC 6186 第 3.2、3.3 节分别定义 IMAP 与 POP3 的 SRV 标签：IMAP 用 `_imaps._tcp`（隐式 TLS，端口 993）与 `_imap._tcp`（STARTTLS，端口 143）；POP3 用 `_pop3s._tcp`（端口 995）与 `_pop3._tcp`（端口 110）。客户端据此自动得知该用哪个协议、哪个端口、是否加密。

**与 Microsoft Autodiscover 的互补**

在 Exchange 场景，Microsoft 的 Autodiscover 服务进一步最小化用户配置：域加截客户端先查 Active Directory 中的 SCP 对象（两类 GUID 分别为 67661d7F-8FC4-4fa7-BFAC-E1D7794C1F68 的 SCP 指针与 77378F46-2C66-4aa9-A6A6-3E7A48B19596 的 SCP URL，提供权威 Autodiscover URL）；外部客户端则用 DNS CNAME/SRV 或基于用户 SMTP 域推导的 `https://autodiscover.<域>/autodiscover/autodiscover.xml` 拉取 XML 配置文件，自动获得显示名、内外网连接设置、邮箱位置与各功能 URL。

**落地建议**

自建邮件域可同时发布 \_submission/\_imap(s)/\_pop3(s) 的 SRV 记录，让用户免去手动填端口；Exchange 环境另配 Autodiscover 的 CNAME 与 SCP，实现 Outlook 等客户端的零配置。两者并不冲突，SRV 面向标准协议客户端，Autodiscover 面向 Exchange 生态。

参考：https://www.rfc-editor.org/rfc/rfc6186.txt 与 https://learn.microsoft.com/en-us/exchange/architecture/client-access/autodiscover

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-client-autoconfig-rfc6186.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
