---
title: "收到 DMARC 聚合（RUA）与失败（RUF）报告后该如何处理（RFC 7489）？"
source: "https://ztpop.net/kb/dmarc-report-handling.html"
license: CC-BY 4.0
---

# 收到 DMARC 聚合（RUA）与失败（RUF）报告后该如何处理（RFC 7489）？

1
收到 DMARC 聚合（RUA）与失败（RUF）报告后该如何处理（RFC 7489）？
▼

**收集**

按自身 DMARC 策略的 rua/ruf 地址接收报告；RUA 为 XML 聚合（展示型，含各源 IP 的认证结果统计），RUF 为失败样本的 forensic 报告（含原始信头，敏感）。

**解析 RUA**

用工具汇总每 IP 的 SPF/DKIM/DMARC 通过率、对齐情况、发送量；识别“本应授权却失败”的合法发送源（如未纳入 SPF include 的邮件网关、未重签的转发）。

**处置**

对失败率高的合法源，补齐 SPF include / DKIM 重签 / 对齐；对未授权源则收紧策略（p=quarantine→reject）。RUF 用于定位具体伪造事件，但注意隐私与 volume，常限采样。

**实践**

先 p=none 收集数周建立基线，再逐步 p=quarantine/reject；把报告接入监控看板，持续发现“影子发信源”。

参考：RFC 7489 §6（DMARC 报告：RUA/RUF）；§7（接收方处理）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-report-handling.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
