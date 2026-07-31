---
title: "如何“发布 DKIM 记录”让收件方验签？选择器(selector)怎么选？"
source: "https://ztpop.net/kb/email-dkim-record-howto.html"
license: CC-BY 4.0
---

# 如何“发布 DKIM 记录”让收件方验签？选择器(selector)怎么选？

1
如何“发布 DKIM 记录”让收件方验签？选择器(selector)怎么选？
▼

**两步**

① 生成密钥对，私钥配到签名服务（MTA/ESP），公钥放到 DNS：<选择器>.\_domainkey 的 TXT（v=DKIM1; k=rsa; p=<公钥>）；② 发信时信头带对应 DKIM-Signature。

**选择器**

选择器是“同一域可多套密钥”的索引（如 2026q3、sel1），便于轮换与多服务并存；更换密钥时新增选择器而非覆盖，避免验签中断。

**注意**

公钥需完整（RSA 2048+ 或 Ed25519）；TXT 长度受限时可拆多段；DNS 改后等 TTL 再生效。

**实践**

与 SPF/DMARC 同属“认证三件套”；发布后用验签工具/DMARC 报告确认“对齐通过”（见 DKIM 签名头篇）。

参考：RFC 6376（DKIM 记录与选择器）；RFC 8463（Ed25519 密钥）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-dkim-record-howto.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
