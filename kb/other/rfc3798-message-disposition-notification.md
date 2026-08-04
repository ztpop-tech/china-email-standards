---
title: "RFC 3798 邮件处置通知（MDN）：已读回执的协议机制"
source: "https://ztpop.net/kb/rfc3798-message-disposition-notification.html"
license: CC-BY 4.0
---

# RFC 3798 邮件处置通知（MDN）：已读回执的协议机制

## 概述

发件方有时需要知道对方"是否看到了邮件"。RFC 3798 定义的 MDN（Message Disposition Notification，邮件处置通知）就是标准的"已读/处置回执"：收件方 MUA 在处理邮件（显示、打印、删除）后，自动或经用户确认向发件方回一封结构化通知。它补充 DSN（仅报告"是否送达"），报告"是否读过"。

## 工作机制

发件方在邮件中加 `Disposition-Notification-To` 头指明回执接收地址；收件方处理后生成 MDN，典型动作含：

```
Disposition: automatic-action/MDN-sent-automatically; displayed
   (本邮件已被自动显示)
```

动作取值包括 `displayed`（显示）、`deleted`（未读即删）、`dispatched`（转发）、`processed`（处理）。MDN 本身是一封 multipart/report 邮件，发回 Disposition-Notification-To 指定的地址。

## 隐私冲突：Apple MPP 的冲击

MDN 本就依赖收件方"是否真的打开"。但 Apple Mail Privacy Protection（MPP）会在代理层预加载远程内容，使"打开"在用户实际阅读前就触发；同时许多客户端默认禁用 MDN 或要求用户确认。结果：MDN/打开追踪的可靠性大幅下降。RFC 3798 也明确要求尊重用户隐私，不得强制回执。

## 企业与合规用途

在政企与信创邮件场景，MDN 可用于重要通知（如公文、合同）的"已阅"留痕，但应作为可选功能并明确告知用户。更可信的送达证明可结合 DSN（RFC 3461）做送达确认。

## 对信创邮件的启示

信创邮件系统若提供回执，应：① 默认关闭自动 MDN、改为用户确认；② 在隐私开关中允许完全禁用；③ 区分"已送达（DSN）"与"已读（MDN）"，避免把投递成功误报为阅读。这与等保对个人信息保护的要求一致。

### 相关主题

* [SMTP 投递状态通知（DSN）](/kb/smtp-dsn-rfc3461.html)：送达而非已读
* [Apple 邮件隐私保护（MPP）](/kb/apple-mail-privacy-protection.html)：打开追踪为何失效
* [邮件送达追踪](/kb/email-delivery-tracking.html)：多层可观测性

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc3798-message-disposition-notification.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
