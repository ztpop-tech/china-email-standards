---
title: "OpenDMARC 如何落地 DMARC 策略（对齐判定、隔离/拒绝、报告）？"
source: "https://ztpop.net/kb/opendmarc-policy-config.html"
license: CC-BY 4.0
---

# OpenDMARC 如何落地 DMARC 策略（对齐判定、隔离/拒绝、报告）？

1
OpenDMARC 如何落地 DMARC 策略（对齐判定、隔离/拒绝、报告）？
▼

**角色**

OpenDMARC 作为入信 milter，按收件域的 DMARC 策略对“SPF/DKIM 对齐”做最终判定，并执行 quarantine/reject 或仅标记。

**对齐**

DMARC 要求“SPF 或 DKIM 的域与 From 头域对齐（严格/宽松）”；OpenDMARC 计算 spf\_align / dkim\_align 并据 p= 策略动作，写入 Authentication-Results。

**报告**

据 rua/ruf 汇总发送聚合/取证报告给发件域；本地可配置 Auth Failure Reports 与历史库。

**实践**

部署路径常为“先 p=none 观察（用报告调对齐）→ p=quarantine → p=reject”；对外发域自己要 publish 正确 DMARC 记录。

参考：OpenDMARC 文档；RFC 7489（DMARC）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendmarc-policy-config.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
