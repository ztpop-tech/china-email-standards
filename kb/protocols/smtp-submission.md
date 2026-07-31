---
title: "邮件提交（Submission，RFC 6409）是什么？为什么发信要用 587 而非 25 端口？"
source: "https://ztpop.net/kb/smtp-submission.html"
license: CC-BY 4.0
---

# 邮件提交（Submission，RFC 6409）是什么？为什么发信要用 587 而非 25 端口？

1
邮件提交（Submission，RFC 6409）是什么？为什么发信要用 587 而非 25 端口？
▼

**定义**

RFC 6409 定义“邮件提交代理（MSA）”与提交协议：终端用户把邮件交给自己服务商的 MSA，通常使用 TCP 587 端口并强制 STARTTLS + 身份认证，与服务器之间互联的“传输（MTA, 25 端口）”区分开。

**25 端口问题**

25 端口用于 MTA 之间传输，常被宽带运营商封禁以抑制僵尸网络 spam；且不对最终用户做身份认证，不适合个人发信。

**587 优势**

587 专用于“用户→MSA”的提交，要求认证与加密，运营商不封锁，能正确施加速率限制与策略（如 DKIM 签名、SPF 对齐），是现代邮件客户端的标准发信端口。

**465 与 587**

465 原是 SMTPS（隐式 SSL，已废但被沿用），587 是提交+STARTTLS 的推荐端口；现代实践首选 587+STARTTLS。

参考：RFC 6409（Message Submission for Mail）；与 RFC 5321（SMTP 传输）区分

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-submission.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
