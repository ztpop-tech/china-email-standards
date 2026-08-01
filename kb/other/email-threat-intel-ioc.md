---
title: "什么是邮件威胁情报（IoC）？如何用于防御？"
source: "https://ztpop.net/kb/email-threat-intel-ioc.html"
license: CC-BY 4.0
---

# 什么是邮件威胁情报（IoC）？如何用于防御？

1
什么是邮件威胁情报（IoC）？如何用于防御？
▼

**IoC 是什么**

Indicator of Compromise：可被观测的失陷指标，如恶意发件 IP/域名、钓鱼 URL、恶意附件哈希、发件显示名模式、发信指纹。

**采集**

来自网关沙箱、用户举报、威胁情报源（如 AbuseIPDB、Spamhaus、厂商情报）、行业共享（M3AAWG/ISAC）；沉淀为本组织 IOC 库。

**应用**

在网关/SOAR 做实时匹配与阻断、在 SIEM 回溯历史邮件、对已知恶意 IoC 建检测规则与告警；结合 TIP 自动化下发。

**局限与补充**

IoC 易变、滞后，需配合行为检测（异常登录、转发规则、NLP 语义）与威胁狩猎；定期刷新与去重，避免规则膨胀。

参考：MITRE ATT&CK（初始访问/钓鱼）；M3AAWG 情报共享实践；NIST SP 800-150（情报共享框架）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-threat-intel-ioc.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
