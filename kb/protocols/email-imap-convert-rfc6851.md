---
title: "IMAP 的 CONVERT 扩展（RFC 6851）能做什么？为何与“附件转格式”相关？"
source: "https://ztpop.net/kb/email-imap-convert-rfc6851.html"
license: CC-BY 4.0
---

# IMAP 的 CONVERT 扩展（RFC 6851）能做什么？为何与“附件转格式”相关？

1
IMAP 的 CONVERT 扩展（RFC 6851）能做什么？为何与“附件转格式”相关？
▼

**机制**

CONVERT 让客户端请求服务器“把某邮件/附件转成另一种格式再返回”，如把大图转小尺寸、把文档转 PDF，省客户端算力与下载量。

**场景**

移动端预览大附件前先让服务器转小；或统一格式便于归档/检索；转换在服务器端完成，客户端只拿结果。

**限制**

转换类型受服务器能力约束（并非任意格式都行）；结果通常作为“临时数据”返回，不改变原信。

**实践**

邮件系统若支持 CONVERT 可优化移动体验（缩略图/轻量预览）；需防范“转换即放大攻击面”，限制类型与资源。

参考：RFC 6851（IMAP CONVERT 扩展）；服务器侧转换实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-imap-convert-rfc6851.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
