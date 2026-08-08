---
title: "Exim 的 ACL 里 acl_smtp_rcpt 与 acl_smtp_data 分别在何时触发，如何拒绝？"
source: "https://ztpop.net/kb/exim-acl-smtp-rcpt-data-reject.html"
license: CC-BY 4.0
---

# Exim 的 ACL 里 acl_smtp_rcpt 与 acl_smtp_data 分别在何时触发，如何拒绝？

1
Exim 的 ACL 里 acl\_smtp\_rcpt 与 acl\_smtp\_data 分别在何时触发，如何拒绝？
▼

**acl\_smtp\_rcpt**

在每个 RCPT 命令时触发（每个收件人一次），适合基于收件人、发件人、连接 IP、HELO 的早期拒绝，如拒绝未授权中继、黑名单 IP、受限收件人。ACL 中 deny 直接返回 550，accept 放行，require 不满足则拒绝。

**acl\_smtp\_data**

在客户端发出 DATA 之后、邮件本体接收完毕（即 "." 结束）时触发，此时能看到完整邮件头与正文，适合基于内容/SPF/DKIM/DMARC 结果、附件、收件人总数等做最终拒绝。

**取舍与写法**

在 DATA 阶段才拒绝会让发送方已付出传输成本，且更易被探测为开放中继，故很多检查（如发件人合法性）放在 rcpt 阶段更早拒绝。拒绝可用 message = ... 给出发件方可读原因；deny 在 rcpt 阶段立即断连接该收件人。

参考：Exim 官方文档（ACL：acl\_smtp\_rcpt / acl\_smtp\_data）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-acl-smtp-rcpt-data-reject.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
