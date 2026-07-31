---
title: "邮件客户端的“自动配置/自动发现（RFC 6186）”如何实现？用户为何不用手填服务器？"
source: "https://ztpop.net/kb/email-autoconfig-thunderbird.html"
license: CC-BY 4.0
---

# 邮件客户端的“自动配置/自动发现（RFC 6186）”如何实现？用户为何不用手填服务器？

1
邮件客户端的“自动配置/自动发现（RFC 6186）”如何实现？用户为何不用手填服务器？
▼

**问题**

手动填 IMAP/SMTP 主机、端口、加密易错；自动发现让客户端“输入邮箱+密码”即拿到正确设置。

**机制**

两种主流：① DNS SRV 记录（\_imap.\_tcp / \_submission.\_tcp 指向正确主机端口）；② 域的 https://autoconfig./.well-known/... 或 Thunderbird autoconfig XML 提供设置。

**RFC 6186**

规范了用 SRV + 探测 autoconfig/autodiscover 端点来自动获取“收/发服务器 + 端口 + 加密”，降低用户门槛。

**实践**

邮件系统/域名应发布 SRV 与 autoconfig 文件，使 Outlook/Thunderbird/手机客户端“开箱即配”；否则用户只能手填，易配错导致无法收发。

参考：RFC 6186（邮件自动配置 SRV/autoconfig）；Thunderbird Autoconfig 格式

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-autoconfig-thunderbird.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
