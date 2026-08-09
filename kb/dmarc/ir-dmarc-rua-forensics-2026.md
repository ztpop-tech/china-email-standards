---
title: "DMARC 聚合报告（rua）怎么读？如何用它定位认证失败的真实来源？"
source: "https://ztpop.net/kb/ir-dmarc-rua-forensics-2026.html"
license: CC-BY 4.0
---

# DMARC 聚合报告（rua）怎么读？如何用它定位认证失败的真实来源？

1
DMARC 聚合报告（rua）怎么读？如何用它定位认证失败的真实来源？
▼

**聚合报告是什么，由谁产生**

RFC 7489《Domain-based Message Authentication, Reporting, and Conformance (DMARC)》第 7.2 节（Aggregate Reports）规定了聚合报告机制：接收方按周期把以你的域为 From 域的邮件的认证处理结果汇总后回送给域所有者。接收地址由 DMARC 记录中的 rua 标签指定——该标签在第 6.3 节（General Record Format）中定义，含义是聚合反馈的发送目的地址。报告是统计汇总而非邮件原文，不含正文内容。

**先看清报告的三组核心字段**

对每一个发送源 IP，报告给出：该 IP 的发信量；DMARC 处置结果（none/quarantine/reject）；以及 SPF 与 DKIM 各自的评估结果与对齐（alignment）情况。关键在于区分「机制本身通过」与「与 From 域对齐」——SPF 对信封发件人域求值通过，但该域与 From 域不一致时，DMARC 视角下仍算不对齐，这是绝大多数误判的来源。

**判定逻辑：三类来源分开处理**

第一类，认证通过的已知来源：确认在册即可。第二类，认证失败但 IP 可归属于自己或自己委托的发送方（营销平台、工单系统、监控告警、分支机构出口）：这是配置缺口，不是攻击。处置是为其补齐 SPF 授权或部署 DKIM 签名，并确保签名域与 From 域对齐。第三类，认证失败且 IP 无法归属：这才是仿冒或转发导致的失败，需结合是否为已知转发场景再判。

**转发造成的失败要单独识别，避免误伤**

邮件经转发后 SPF 通常失败（信封发件人被中继替换或 IP 变更），但若 DKIM 签名未被改动则仍可通过，DMARC 因而整体通过。所以报告中出现「SPF 失败但 DKIM 通过」的来源，多为正常的间接投递路径，不应据此判定为攻击。反之，SPF 与 DKIM 双双失败且量级稳定的陌生 IP，才是仿冒的典型形态。

**用报告驱动策略收紧**

推进 p=none 到 quarantine 再到 reject 的前提，是聚合报告中「已知合法来源」的认证通过率已接近全量，且剩余失败均已确认为不可归属来源。在存在大量第二类失败时直接收紧策略，会造成自有业务邮件被拒。收紧应分阶段进行，并在每一阶段持续观察报告变化。

参考：[RFC 7489](https://www.rfc-editor.org/rfc/rfc7489.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ir-dmarc-rua-forensics-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
