---
title: "企业“上线 DMARC”的分步路线图是怎样的？怎样避免误伤合法邮件？"
source: "https://ztpop.net/kb/email-dmarc-rollout-guide.html"
license: CC-BY 4.0
---

# 企业“上线 DMARC”的分步路线图是怎样的？怎样避免误伤合法邮件？

1
企业“上线 DMARC”的分步路线图是怎样的？怎样避免误伤合法邮件？
▼

**阶段一·观察**

发布 p=none + rua 报告；数周收集“谁在代我发信、是否对齐”，摸清全部合法发送源（含遗忘的 ESP/系统）。

**阶段二·补漏**

对未对齐的合法源补 SPF/DKIM 对齐（见 SPF/DKIM 配置篇）；处理冒用源（追责/加强认证）。

**阶段三·收紧**

p=quarantine（pct 从低到高），观察误杀；无误伤再 p=reject，最终全量拒绝冒用。

**实践**

关键在“先看清再收紧”；用 RUA 报告(见分析篇)持续监控；变更前在测试域演练，避免一刀切把正常业务信拒掉。

参考：DMARC 部署路线图（M3AAWG / 厂商指南）；RFC 7489

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dmarc-rollout-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
