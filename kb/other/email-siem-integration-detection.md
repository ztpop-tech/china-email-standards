---
title: "邮件安全事件如何与 SIEM 集成实现集中检测？"
source: "https://ztpop.net/kb/email-siem-integration-detection.html"
license: CC-BY 4.0
---

# 邮件安全事件如何与 SIEM 集成实现集中检测？

1
邮件安全事件如何与 SIEM 集成实现集中检测？
▼

**日志源梳理**

向 SIEM 汇聚多类邮件遥测：MTA/邮件网关的 SMTP 事务与拒绝日志、投递/邮件追踪（message trace）、认证结果头（Authentication-Results：SPF/DKIM/DMARC）、DLP 命中、反垃圾与反恶意软件 verdict、登录与转发规则变更，覆盖发、收、存储、访问全链路。

**标准化接入**

以 Syslog（RFC 5424）、CEF 或 LEEF 等通用格式，或以 JSON 经 API/消息队列（如 Kafka）推送。统一时间戳（NTP）、时区与字段命名，保留 Message-ID、队列 ID、发件/收件域、客户端 IP，便于跨源关联。

**关联规则**

* 异常外发：单账号短时大量外发或被拒，疑似被控/垃圾；
* 伪造检测：入站邮件 DMARC=fail 却声称来自本域或重要合作域；
* 退信激增：退信率突增预示列表被投毒或欺诈；
* 可疑转发规则：自动转发到外部地址（数据外泄前兆）。

**检测闭环**

SIEM 对规则命中生成告警并富化（资产、用户、威胁情报），与工单/SOAR 联动；保留原始日志满足审计与取证（NIST SP 800-92 的留存与完整性要求）。告警需降噪、分级，避免淹没真实事件。

参考：NIST SP 800-92《计算机安全日志管理指南》、NIST SP 800-61《事件处理指南》、RFC 5424《Syslog》、CEF/LEEF 格式规范、MITRE ATT&CK 检测映射。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-siem-integration-detection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
