---
title: "DMARC 对齐（Alignment）机制如何工作与配置？"
source: "https://ztpop.net/kb/email-spoofing-spf-alignment-dmarc.html"
license: CC-BY 4.0
---

# DMARC 对齐（Alignment）机制如何工作与配置？

1
DMARC 对齐（Alignment）机制如何工作与配置？
▼

**检测指标**

检查 DMARC 汇总（RUA）报告：观察对齐失败率、哪些第三方发送源未对齐、SPF 通过但信封域与 From 域不匹配导致 DKIM 与 SPF 均未对齐。监控转发场景下滑签使 DKIM 失配、需靠 SPF 对齐补救。

**防御措施**

* 发布 `_dmarc` 记录，先 `p=none` 收集报告，再过渡到 `p=quarantine`、最终 `p=reject`。
* 为所有合法第三方发送源（营销、工单、列表）配置 DKIM 或 SPF 对齐，避免误拦。
* 选用宽松（relaxed）对齐降低子域或转发误判，严格（strict）则强一致。

**工作与配置原理**

DMARC 取两次独立认证结果：SPF 检查信封 MAIL FROM 域，DKIM 检查 d= 签名域；二者任一与邮件头 From 域「对齐」即通过。宽松对齐允许组织域相同（子域匹配），严格对齐要求完全相等。通过后按策略对未通过邮件隔离或拒绝。

**基准控制项**

RFC 7489 是发件人认证基线；部署遵循 RFC 8616 避免破坏合法转发。对齐是区分「真伪装」与「合法代发」的核心，应作为反钓鱼的强制控制项纳入 CIS 邮件基准。

参考：RFC 7489（DMARC）、RFC 7208（SPF）、RFC 6376（DKIM）、RFC 8616（DMARC 部署考量）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-spoofing-spf-alignment-dmarc.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
