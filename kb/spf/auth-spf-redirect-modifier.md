---
title: "SPF 的 redirect 修饰符和 include 有什么本质区别？什么时候该用哪个？"
source: "https://ztpop.net/kb/auth-spf-redirect-modifier.html"
license: CC-BY 4.0
---

# SPF 的 redirect 修饰符和 include 有什么本质区别？什么时候该用哪个？

1
SPF 的 redirect 修饰符和 include 有什么本质区别？什么时候该用哪个？
▼

**一句话区分：一个是「替换」，一个是「引用」**

RFC 7208 第 6.1 节（redirect: Redirected Query）与第 5.2 节（"include"）分别定义了这两项。核心差异：

* **`redirect` 是修饰符，语义近似「本域的策略以那个域为准」**——把整条策略连同最终结论一起交出去。
* **`include` 是机制，语义是「去那个域问一下，只取『是否 pass』这一个信息」**——问完回来继续走本域后面的项。

这个区别决定了后续所有行为差异。

**结果处理：include 只认 pass，redirect 全盘接收**

**include 的判定（第 5.2 节）：**递归评估被引用域，**只有得到 `pass` 才算该机制匹配**；得到 fail、softfail、neutral 等结果时，该机制**不匹配**，评估继续走本记录后续项。若递归中出现 `temperror`/`permerror`，则相应向外传递错误。

**redirect 的判定（第 6.1 节）：**整个评估转到目标域，**目标域的最终结果就是本次评估的最终结果**，包括 fail。若目标域没有有效 SPF 记录，结果为 `permerror`。

**实践含义：**用 include 引用第三方，对方 fail 不会连累你；用 redirect 指向某域，对方 fail 就是你 fail。**redirect 是把裁决权完全让渡出去。**

**与 all 的交互：这是最容易出错的地方**

第 6.1 节明确：**`redirect` 只在记录中没有任何 `all` 机制匹配时才被使用**；换言之，**只要记录里有 `all`，`redirect` 就会被忽略**。

所以下面这条记录里的 redirect 是**无效**的：

```
v=spf1 ip4:192.0.2.0/24 -all redirect=_spf.example.net   ← redirect 永远不会生效
```

正确写法是**不写 all**，让 redirect 承担收尾：

```
v=spf1 ip4:192.0.2.0/24 redirect=_spf.example.net
```

而 include 是机制、按顺序参与匹配，与 `all` 并存是正常且必要的：

```
v=spf1 ip4:192.0.2.0/24 include:_spf.example.net -all
```

**数量与位置：修饰符只能有一个**

* `redirect` 作为修饰符，一条记录中**至多出现一次**；`include` 作为机制可以出现多次。
* 机制按**从左到右**顺序求值，首个匹配即决定结果；修饰符与位置无关，在机制都不匹配后才考虑。
* **两者都计入** RFC 7208 第 4.6.4 节的 10 次 DNS 查询上限，且被引用域内部的查询同样累加。

**选型判据：按「谁说了算」来决定**

1. **多个域共用同一套策略、且完全信任该策略 → 用 redirect。**典型场景是一家机构持有多个域名，全部指向同一条集中维护的 SPF 记录，改一处即全域生效。
2. **本域有自己的出口，只是额外授权某些第三方 → 用 include。**这是绝大多数业务场景的正确选择。
3. **不确定时用 include。**它的失败影响面更小、语义更可控，不会因对方记录变化而让本域整体结论翻转。

**补充提醒：**使用 redirect 时，目标域的 SPF 记录一旦被删除或写错，本域立刻变成 `permerror`。**跨组织边界时应避免使用 redirect**，把它限制在自己完全掌控的域之间。

参考：[RFC 7208 Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1](https://www.rfc-editor.org/rfc/rfc7208.txt)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/auth-spf-redirect-modifier.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
