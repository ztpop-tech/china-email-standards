---
title: "DMARC 的 sp 标签怎么用？子域没有单独记录时会套用哪条策略？"
source: "https://ztpop.net/kb/auth-dmarc-subdomain-policy-sp.html"
license: CC-BY 4.0
---

# DMARC 的 sp 标签怎么用？子域没有单独记录时会套用哪条策略？

1
DMARC 的 sp 标签怎么用？子域没有单独记录时会套用哪条策略？
▼

**sp 是什么：给子域单独指定的策略**

RFC 7489 第 6.3 节（General Record Format）把 `sp` 定义为「组织域的子域所适用的策略」。它只在**组织域的 DMARC 记录**中有意义，取值与 `p` 相同：`none`、`quarantine`、`reject`。

**关键缺省规则：**若组织域记录中**没有** `sp` 标签，子域直接**继承 `p` 的取值**。也就是说「不写 sp」不等于「子域不受管」，而是「子域和主域一样严」。

**策略发现顺序：先查自身，再回落组织域**

RFC 7489 第 6.6.3 节（Policy Discovery）规定了接收方查找策略的顺序，理解它才能预测子域实际生效的策略：

1. **先查 From 域自身**的 `_dmarc.<From 域>`。查到有效记录即采用，其中的 `p` 生效。
2. **查不到，则求出组织域**，再查 `_dmarc.<组织域>`。若查到，则对该子域适用组织域记录中的 `sp`；`sp` 缺省时适用 `p`。
3. 两处都查不到，则该消息不适用 DMARC。

**推论：**只要子域自己发布了 DMARC 记录，组织域的 `sp` 对它就**不再起作用**——这是「例外放行」的正确实现方式。

**典型用法一：主域宽松过渡、子域直接从严**

组织域尚处观察期、还不敢上 reject，但大量子域根本不发信，完全可以立刻锁死：

```
_dmarc.example.com  TXT  "v=DMARC1; p=none; sp=reject; rua=mailto:..."
```

效果是：主域仅监控、不影响业务；**所有未单独发布记录的子域一律拒收**，直接封堵「随手编个子域冒充」这类攻击面。这是 sp 最有价值的用法。

**典型用法二：主域已 reject、个别子域需要缓冲**

反过来，主域已经收敛到 reject，但某个子域上跑着尚未改造完的老系统，此时**不要**去放宽 `sp`（那会连带放宽所有子域），正确做法是给该子域**单独发布**一条更宽松的记录：

```
_dmarc.legacy.example.com  TXT  "v=DMARC1; p=none; rua=mailto:..."
```

按第 6.6.3 节的查找顺序，该子域命中自身记录，其余子域仍受组织域约束。**把例外限定在最小范围**，是子域策略管理的核心原则。

**落地检查清单**

* **盘点子域。**先弄清哪些子域实际发信、哪些完全不发信。
* **先加 sp 再收 p。**不发信的子域没有误伤风险，可优先从严；主域按流量数据逐步收敛。
* **例外用独立记录实现**，不要靠放宽 sp 全局开口子。
* **确认继承效果。**若你原本只写了 `p=reject` 而没写 `sp`，要意识到全部子域此刻已按 reject 处理，需核对是否存在被误伤的子域发信。

参考：[RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.txt)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/auth-dmarc-subdomain-policy-sp.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
