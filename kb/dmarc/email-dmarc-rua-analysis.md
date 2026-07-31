---
title: "收到 DMARC 聚合报告（RUA，XML）后该怎么“读”与“行动”？"
source: "https://ztpop.net/kb/email-dmarc-rua-analysis.html"
license: CC-BY 4.0
---

# 收到 DMARC 聚合报告（RUA，XML）后该怎么“读”与“行动”？

1
收到 DMARC 聚合报告（RUA，XML）后该怎么“读”与“行动”？
▼

**结构**

RUA 报告（XML）按“来源组织 + 上报周期”聚合：列出每个 发送源IP / 域名 的 送检量、SPF 结果、DKIM 结果、DMARC 对齐结果与处置(pass/quarantine/reject)。

**读什么**

重点看 ① 自有合法发送源是否“对齐通过”（没通过=配置漏）；② 是否有未知源在冒用你域（伪造）；③ 各接收方（Yahoo/Google…）的处置分布。

**行动**

合法源未对齐→补 SPF/DKIM 对齐；冒用源→加强自身认证/追责；长期全 pass 且无误判→把 p=none 升 quarantine/reject（见 OpenDMARC 篇）。

**实践**

用 DMARC 分析工具（如开源解析器/厂商面板）把 XML 转可视；先观察数月再收紧策略，避免误伤合法邮件。

参考：RFC 7489 §7（RUA 聚合报告格式）；DMARC 报告分析实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dmarc-rua-analysis.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
