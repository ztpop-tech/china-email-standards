---
title: "RFC 8617 ARC 认证链的三个头字段与验证算法是什么？"
source: "https://ztpop.net/kb/rfc8617-arc-chain-validation.html"
license: CC-BY 4.0
---

# RFC 8617 ARC 认证链的三个头字段与验证算法是什么？

1
RFC 8617 ARC 认证链的三个头字段与验证算法是什么？
▼

**三个 ARC 头字段（§4.1）**

* **ARC-Authentication-Results（AAR，§4.1.1）**：记录该处理节点对邮件所做的认证评估结果。它与普通 `Authentication-Results` 头的关键差别在于**带有实例标签 `i=`**。
* **ARC-Message-Signature（AMS，§4.1.2）**：对邮件正文与选定头字段签名，语法沿用 DKIM（RFC 6376），但 DKIM 的 `i=` 语义被**实例标签取代**。重要约束：**三个 ARC 相关头字段（AAR、AMS、AS）MUST NOT 出现在 AMS 的签名头列表 `h=` 中**。
* **ARC-Seal（AS，§4.1.3）**：对既有 ARC 链本身加封。同样以实例标签替代 DKIM 的 `i=`，并新增 `cv`（chain validation）标签承载链验证状态。

**ARC Set 与实例标签（§4.2）**

同一节点追加的 AAR、AMS、AS 三者共享**同一个 `i=` 实例值**，合称一个 **ARC Set**。验证器正是依据实例标签还原各中介的处理先后顺序。规范要求：**对给定实例值与签名域，有效的 ARC Set 中三种 ARC 头字段各恰好出现一次**。

**链验证状态的三个取值（§4.4）**

某处理步骤上的链状态称为 Chain Validation Status，通过 AS 的 `cv` 标签，以及 `Authentication-Results` / AAR 头字段对外传达，只有三种取值：

* **`none`**：邮件送达验证时**本来就没有 ARC 链**。典型场景是直接收自原始 MTA/MSA，或收自不参与 ARC 处理的上游邮件处理方。
* **`fail`**：邮件带有 ARC 链，但验证未通过。
* **`pass`**：邮件带有 ARC 链且验证通过。

**加封方的实例值计算（§5.1）**

加封方（Sealer）计算实例值的规则很明确：**若邮件已存在 ARC 链，新实例值 = 链中最大实例号 + 1；若不存在链，则实例值为 1。**随后按 AAR → AMS → AS 的顺序生成并附加三个头字段。此外 §5.1.2 处理「把 `cv=fail` 的无效链封存」的情形；§5.1.3 规定**一封邮件只能有一条 ARC 链**；§5.1.5 给出重要工程结论——**加封总是安全的（Sealing Is Always Safe）**。

**验证器算法逐步拆解（§5.2）**

验证器按顺序执行，规范化、哈希与签名校验方法均沿用 RFC 6376 §5：

1. 收集邮件上现有全部 ARC Set。**一个都没有 → 状态为 `none`，算法终止**；**ARC Set 数量上限为 50，超出 → 状态为 `fail`，算法终止**。记最大实例值为 N。
2. 若**最高实例值**那个 ARC Set 的链状态为 `fail`，则整体 `fail`，终止。
3. 校验链结构，须同时满足三个条件：**(A)** 每个 ARC Set 恰好各含一个 AAR、AMS、AS；**(B)** 各 Set 的实例值构成从 1 到 N 的**连续序列，不得有缺口或重复**；**(C)** 所有 AS 的 `cv` 值 MUST NOT 为 `fail`——实例值 > 1 的必须为 `pass`，实例值 = 1 的必须为 `none`。任一条件不满足即 `fail` 并终止。
4. 校验**实例值最大（最新）的那个 AMS**；校验失败即 `fail` 并终止。
5. 可选步骤：从 ARC Set 推导 `oldest-pass` 值。

§5.2.1 另有一条运维上极重要的原则：**所有 ARC 验证失败都是永久性的**（All Failures Are Permanent），不应作为临时错误反复重试。

参考：RFC 8617《The Authenticated Received Chain (ARC) Protocol》，https://www.rfc-editor.org/rfc/rfc8617 —— 章节 4.1.1–4.1.3 / 4.2.1 / 4.4 / 5.1 / 5.2 / 5.2.1

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8617-arc-chain-validation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
