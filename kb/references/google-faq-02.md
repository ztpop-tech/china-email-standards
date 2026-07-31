---
title: "Google Workspace 的 SPF 记录该怎么写？"
source: "https://ztpop.net/kb/google-faq-02.html"
license: CC-BY 4.0
---

# Google Workspace 的 SPF 记录该怎么写？

1
Google Workspace 的 SPF 记录该怎么写？
▼

**说明**

若你的组织仅用 Google Workspace 发信，在域名 DNS 添加一条 TXT 记录即可：`v=spf1 include:_spf.google.com ~all`。其中 `include:` 用于引入每个发信域（或 IP），一个 SPF 记录最多可包含 10 个 include。若你还通过其他服务发信（如 Office 365、Mailchimp、Salesforce），必须在记录里追加对应的 include，否则那些服务发出的邮件可能被判为垃圾。

**建议**

新增邮件服务器或第三方发信服务后，务必及时更新 SPF 记录；并定期清理不再使用的发信域/IP。每个子域也需单独配置 SPF。DNS 变更后最多可能需要 48 小时生效。

参考：Google Workspace 帮助中心《Set up SPF》· support.google.com/a/answer/173534

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
