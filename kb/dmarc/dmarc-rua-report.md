---
title: "DMARC 聚合报告（RUA）是什么？如何解读 RUA 报告里的 XML 数据？"
source: "https://ztpop.net/kb/dmarc-rua-report.html"
license: CC-BY 4.0
---

# DMARC 聚合报告（RUA）是什么？如何解读 RUA 报告里的 XML 数据？

1
DMARC 聚合报告（RUA）是什么？如何解读 RUA 报告里的 XML 数据？
▼

**定义**

RUA（aggregate report，聚合报告）是接收方依 RFC 7489 §6.2 周期发回的汇总报告：它列出你域内邮件在一段时间内的认证结果（SPF/DKIM 对齐、DMARC 通过或失败），以 XML 格式发往域在 \_report.\_dmarc 子域或 rua 标签指定的邮箱。

**报告结构**

报告含 （起止时间、org\_name）、（你的 DMARC 策略 p=none/quarantine/reject）、 每条含源 IP、count、（spf/dkim 结果）与 （header.from 域）。

**解读要点**

重点看 policy\_evaluated 的 disposition 与 dkim/spf 的 pass/fail。若大量合法邮件 dkim=fail 但 spf=pass，说明转发改写了 DKIM，应改用 ARC 或转发域重签。可借助 dmarcian 等解析器把 XML 转成趋势图。

**行动**

先以 p=none 收报告，确认自身发信无误后再逐步收紧到 quarantine/reject；对持续失败的来源排查其发信基础设施或第三方代发。

参考：RFC 7489 §6.2（聚合报告）；RFC 6591（报告扩展）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-rua-report.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
