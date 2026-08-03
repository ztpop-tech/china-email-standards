---
title: "DMARC 策略怎么从 none 一步步升级到 reject（强制拦截伪造）？"
source: "https://ztpop.net/kb/dmarc-policy-enforcement-escalation.html"
license: CC-BY 4.0
---

# DMARC 策略怎么从 none 一步步升级到 reject（强制拦截伪造）？

1
DMARC 策略怎么从 none 一步步升级到 reject（强制拦截伪造）？
▼

**阶段一 none**

仅收集报告不执行。先确认所有合法发送源（主域、子公司、ESP、CRM）都正确做 SPF/DKIM，通过 aggregate 报告（RUA）看清谁在以你域名发信。

**阶段二 quarantine**

对未通过认证的邮件标脏进垃圾箱。观察 quarantine 后是否误伤合法邮件；用子域策略（sp=）覆盖未明子域。

**阶段三 reject**

直接拒收伪造。仅在确认无误伤、关键业务都认证就绪后启用，是防冒充的终极姿态。升级前务必处理第三方发送者认证，否则会误拦自己。

参考：RFC 7489《DMARC》、DMARC.org 部署指南、M3AAWG 发送者最佳实践。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-policy-enforcement-escalation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
