---
title: "_dmarc、_domainkey 这类下划线名字是怎么回事？配置时有哪些坑？"
source: "https://ztpop.net/kb/rfc8552-underscored-dns-node-names-email-scoping.html"
license: CC-BY 4.0
---

# _dmarc、_domainkey 这类下划线名字是怎么回事？配置时有哪些坑？

1
\_dmarc、\_domainkey 这类下划线名字是怎么回事？配置时有哪些坑？
▼

**为什么需要下划线名：给资源记录划定用途范围**

邮件相关的 DNS 配置里到处是下划线开头的名字：DKIM 用 `_domainkey`，DMARC 用 `_dmarc`，MTA-STS 与 TLS 报告各有自己的前缀。这些名字不是随意约定的风格，而是有正式规范的机制。

RFC 8552 说明了这一做法要解决的问题。**TXT 这类通用记录类型没有内部语法可以区分不同用途**：如果把 SPF 策略、DKIM 公钥、域名验证令牌、以及其他各种用途的文本都放在同一个域名下的 TXT 记录集里，查询方拿到的是一堆混杂的字符串，只能靠猜测内容格式来分辨。

解决办法是**把不同用途的记录放到不同的子节点下**。RFC 8552 §1.2 指出，这样做的收益是：直接查询该从属叶节点**只会返回所需的记录类型，成本不高于一次典型的 DNS 查询**。以 DKIM 为例，它用 `_domainkey` 定义了一个存放 TXT 记录的位置，`_domainkey.example.` 这个域名扮演的是「属性」的角色。

**全局下划线名与 IANA 注册表**

RFC 8552 §1.3 给出了一个关键定义。一个域名下可能有多个以下划线开头的节点名，**全局下划线名（global underscored node name）指的是其中最靠近 DNS 根、也即层级最高的那一个**；在常规的书写约定下，就是**最右边那个以下划线开头的名字**。规范用「全局」这一限定词来回避不同书写环境下的位置差异。

以 TLS 报告使用的 `_smtp._tls.example.com` 为例，`_tls` 比 `_smtp` 更靠近根，因此 `_tls` 是全局下划线名。

RFC 8552 §2 据此建立了「Underscored and Globally Scoped DNS Node Names」注册表，目的是**避免不同用途争抢同一个下划线名而产生冲突**。注册表的结构与规则要点包括：

* 它是一张以 RR 类型为索引的扁平表，登记的是「RR 类型 + 全局下划线名」的组合。
* **只有全局下划线名进入注册表。**从属的下划线名（如上例中的 `_smtp`）只在其父级全局下划线名的范围内有意义，因此不被该注册表登记。
* 若某个方案在全局下划线名之下还有从属的下划线名，其定义与含义由该方案自己的规范负责说明。

RFC 8553 是配套文档，它系统性地修订了此前已在使用下划线名却未做登记的各项规范，把它们纳入这套统一框架。**两份文档同属 BCP 222，应当一起看。**

**与通配符的交互：两个方向都是坑**

RFC 8552 §1.4 明确指出：**DNS 通配符与下划线名在两个方向上都配合得很差。**这一节是本主题下最具实操价值的部分。

**方向一：无法为带前缀的名字创建通配。**通配符只在叶名位置被解释，因此 `label.*.example.com` 这样的形式**不是通配符**。这意味着无法用一条记录覆盖「所有子域的 `_dmarc`」或「所有子域的 `_domainkey`」。

**工程后果：邮件认证记录不会被通配继承。**想要为每个子域都提供 DKIM 公钥或独立的 DMARC 策略，只能逐个发布，或者依赖协议本身提供的继承机制（例如 DMARC 的子域策略标签）。**「我配了通配符所以子域都有了」是一个相当普遍的误解，其后果是子域认证静默失效。**

**方向二：通配符会意外命中下划线名。**反过来，`*.example.com` 这样的通配符**可以匹配任何名字，包括下划线名**。于是它可能返回一条「类型上正好是该下划线名所控制的类型、但并非为该下划线语境准备、也不符合其规则」的记录。

**工程后果：一条无关的通配 TXT 记录会污染邮件认证查询。**典型场景是域名下配了 `*.example.com IN TXT "..."` 用于某种验证用途，结果对 `_dmarc.sub.example.com` 的查询命中了这条通配记录，返回一段完全不相干的文本。查询方拿到的不是 NXDOMAIN，而是一条格式错误的记录，**报错信息会指向「策略解析失败」而不是「策略不存在」，排错方向因此被带偏。**

**排错清单**

1. **逐个精确查询，不要假设继承。**对每一个实际发信的子域，单独执行 `dig TXT _dmarc.<子域>`、`dig TXT <选择器>._domainkey.<子域>`。**父域配置正确不能证明子域可用。**
2. **先查有没有通配符记录。**用 `dig TXT randomstring-donotexist.example.com` 这类随机名探测：若返回了 TXT 记录而非 NXDOMAIN，说明存在通配，需要立即评估它会污染哪些下划线查询。
3. **区分「没有记录」与「记录格式错误」。**NXDOMAIN 表示确实没配；返回了内容但解析失败，则要怀疑是不是被通配符命中了无关记录。**这两种情况的处置完全不同。**
4. **核对下划线名的层级顺序。**形如 `_smtp._tls.example.com` 的多级名，顺序写反就查不到。以对应协议规范给出的形式为准，不要凭记忆拼。
5. **查注册表确认名字用途。**遇到不认识的下划线名，先到 IANA 的下划线名注册表核对其归属，再决定能否改动或删除。**删掉一个不认识的下划线记录，可能直接中断某项正在生效的服务。**
6. **纳入变更监控。**下划线记录分散在多个子域下，人工巡检容易遗漏。把「各发信子域的认证记录实际解析结果」做成基线并定期比对，是发现静默失效最有效的方式。

**配置实践建议**

* **能不用通配符就不用。**若业务确实需要通配，应当为所有会被邮件认证查询到的下划线名**显式发布更具体的记录**，让精确匹配优先于通配匹配，从而屏蔽污染。
* **为每个实际发信的子域单独规划认证记录。**不发信的子域反而可以用协议自身的机制收敛，而不是依赖通配。
* **把下划线名当作命名空间来治理。**记录每个下划线名的用途、责任人与关联服务，避免出现「没人知道这条记录是干什么的、也没人敢删」的状态。
* **新增用途前先查注册表。**自定义下划线名可能与已登记或将来登记的名字冲突。RFC 8552 建立注册表的初衷正是避免这类碰撞。
* **变更走「先加后删」。**迁移下划线记录时先发布新记录、验证生效、再删除旧记录，中间留足 TTL 时间。**认证类记录的中断会立刻表现为邮件被拒或被判为可疑**，没有缓冲余地。

参考：RFC 8552《Scoped Interpretation of DNS Resource Records through "Underscored" Naming of Attribute Leaves》§1.2、§1.3 Global Underscored Node Names、§1.4 Interaction with DNS Wildcards、§2，D. Crocker，2019 年 3 月，BCP 222，https://www.rfc-editor.org/rfc/rfc8552.html ；RFC 8553《DNS Attrleaf Changes: Fixing Specifications That Use Underscored Node Names》，D. Crocker，2019 年 3 月，BCP 222，https://www.rfc-editor.org/rfc/rfc8553.html ；RFC 1034《Domain names - concepts and facilities》§3.1，P. Mockapetris，1987 年 11 月，STD 13，https://www.rfc-editor.org/rfc/rfc1034.html ；RFC 4592《The Role of Wildcards in the Domain Name System》，E. Lewis，2006 年 7 月，https://www.rfc-editor.org/rfc/rfc4592.html ；IANA「Underscored and Globally Scoped DNS Node Names」注册表，https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8552-underscored-dns-node-names-email-scoping.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
