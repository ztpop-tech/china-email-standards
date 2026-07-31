---
title: "什么是 Yahoo 的投诉反馈环（CFL）？为什么批量发送人需要它？"
source: "https://ztpop.net/kb/yahoo-faq-08.html"
license: CC-BY 4.0
---

# 什么是 Yahoo 的投诉反馈环（CFL）？为什么批量发送人需要它？

1
什么是 Yahoo 的投诉反馈环（CFL）？为什么批量发送人需要它？
▼

**CFL 是什么**

投诉反馈环（Complaint Feedback Loop, CFL）是 Yahoo 的程序：一旦你用 DKIM 签名邮件，当用户点击“举报垃圾”时，你可以拿到一份投诉副本，用于追踪与管理投诉率。

**为何批量发送方必须启用**

所有 DKIM 域都需启用有效的 CFL，以确保快速处理投诉；借助 CFL 可维护干净列表、监控投诉率并确保低于 0.3%（批量发送方的强制指标）。Yahoo 建议签署 DKIM 后即加入 CFL。

参考：Yahoo《Sender Best Practices》— Enroll in the Complaint Feedback Loop (CFL)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/yahoo-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
