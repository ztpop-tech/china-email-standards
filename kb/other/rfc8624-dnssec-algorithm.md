---
title: "DNSSEC（RFC 8624）算法应如何选择？"
source: "https://ztpop.net/kb/rfc8624-dnssec-algorithm.html"
license: CC-BY 4.0
---

# DNSSEC（RFC 8624）算法应如何选择？

1
DNSSEC（RFC 8624）算法应如何选择？
▼

**DNSKEY 算法表**

§3.1 给出 MUST/MUST NOT 矩阵：**RSASHA256=8 与 ECDSAP256SHA256=13 均为 MUST/MUST**（签名与验证强制）；ED25519=15 为 RECOMMENDED/RECOMMENDED（签名与验证均推荐，文档预期其将成为未来默认）；RSASHA1=5、RSASHA1-NSEC3-SHA1=7 为 NOT RECOMMENDED/MUST（不推荐签发但验证必须支持）；RSAMD5=1、DSA=3、DSA-NSEC3-SHA1=6 为 MUST NOT。

**DS 摘要算法表**

§3.3：DS/CDS 摘要算法中 **SHA-256=2 为 MUST/MUST**（委派与验证强制）；SHA-384=4 为 MAY/RECOMMENDED；**SHA-1=1 为 MUST NOT/MUST**——因 DS 中仍广泛存在，验证器 MUST 支持校验，但 MUST NOT 用于生成新 DS/CDS。

**推荐算法**

§3.2 与 §3.4 明确：**ECDSAP256SHA256 是新 DNSSEC 部署的 RECOMMENDED DNSKEY 算法**，使用 RSA 的部署应升级到它；SHA-256 是 RECOMMENDED 的 DS/CDS 算法。ED25519 被预期成为未来推荐默认值。

**废弃与互操作**

§1.2 强调：被降级到 NOT RECOMMENDED 或更低（如 RSASHA1、RSASHA1-NSEC3-SHA1、RSASHA512）的算法，权威服务器与签名者不应再用于创建新 DNSKEY；但递归解析器被鼓励保留所有未标记 MUST NOT 的算法支持，否则未知算法会使区域被当作 insecure，破坏互操作。SHA-1 因其广泛存量仅能逐步退出。

参考：RFC 8624（DNSSEC Algorithm Implementation Requirements），https://www.rfc-editor.org/rfc/rfc8624 —— 章节 3.1 / 3.2 / 3.3 / 3.4 / 1.2

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8624-dnssec-algorithm.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
