---
title: "DKIM 密钥应该怎么轮转？旧密钥要不要撤销、密钥长度用多少？"
source: "https://ztpop.net/kb/dkim-key-rotation-practice.html"
license: CC-BY 4.0
---

# DKIM 密钥应该怎么轮转？旧密钥要不要撤销、密钥长度用多少？

1
DKIM 密钥应该怎么轮转？旧密钥要不要撤销、密钥长度用多少？
▼

**轮转靠选择器，而不是改一条记录**

RFC 6376 第 3.1 节（Selectors）说明了选择器的设计意图：它使签名方能够按常规节奏无缝更换公钥，文中给出的示例即以时间命名选择器（如 january2005 到 february2005），并说明过渡期内新旧选择器可并存。DNS 侧的命名规则在第 3.6.2.1 节（Namespace）：所有 DKIM 密钥都存放在名为 \_domainkey 的子域下，查询名形如 selector.\_domainkey.example.com。**因此轮转的正确动作是：发布新选择器、切换签名、观察、再退役旧选择器，而不是原地覆盖同一条记录。**

**旧密钥怎么退役与撤销**

RFC 6376 第 3.6.1 节（Textual Representation）在 p= 标签的定义处写明：**p= 取空值表示该公钥已被撤销**。同节进一步说明其用途——若私钥已泄露，签名方可能希望明确表示自己知道这个选择器存在，但使用该选择器的所有邮件都应验证失败。这与直接删除记录不同：删除得到的是无记录的语义，置空则是明确的撤销声明。第 8.7 节（Limits on Revoking Keys）另有对撤销局限性的讨论。

**算法：rsa-sha1 已被禁止**

RFC 8301（Cryptographic Algorithm and Key Usage Update to DomainKeys Identified Mail (DKIM)，2018 年 1 月，更新 RFC 6376）第 3.1 节规定：签名方必须使用 rsa-sha256，验证方必须能够使用 rsa-sha256 验证，**rsa-sha1 不得用于签名或验证**。被识别为使用历史算法（当前即 rsa-sha1）签名的 DKIM 签名，按 RFC 6376 第 3.9 节的规定属于永久性评估失败。IANA 已将 DKIM 哈希算法注册表中 sha1 的状态更新为 historic。

**密钥长度的硬性下限**

RFC 8301 第 3.2 节（Key Sizes）给出明确要求：签名方对所有密钥**必须**使用至少 1024 位的 RSA 密钥，**应当**使用至少 2048 位；验证方必须能够验证 1024 位至 4096 位密钥的签名，并可支持更大密钥；**验证方不得将使用小于 1024 位 RSA 密钥的签名视为有效签名**。该节同时指出，密钥长度选择是成本、性能与风险之间的权衡，而短密钥更易被离线攻击攻破。

**一个现实约束**

RFC 8301 引言中提到一个常被忽略的工程约束：广泛使用的 DNS 配置软件只处理 TXT 记录中的单个 256 字节字符串，而显著长于 1024 位的 RSA 密钥放不进 256 字节。**规划 2048 位密钥时，必须确认 DNS 侧支持多字符串拼接的 TXT 记录发布方式**，否则记录会被截断而导致验证失败。

参考：https://www.rfc-editor.org/rfc/rfc6376.txt 与 https://www.rfc-editor.org/rfc/rfc8301.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-key-rotation-practice.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
