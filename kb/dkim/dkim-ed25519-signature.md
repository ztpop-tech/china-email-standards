---
title: "DKIM 能用 Ed25519 密钥签名吗（RFC 8463）？为什么“算法升级”很重要？"
source: "https://ztpop.net/kb/dkim-ed25519-signature.html"
license: CC-BY 4.0
---

# DKIM 能用 Ed25519 密钥签名吗（RFC 8463）？为什么“算法升级”很重要？

1
DKIM 能用 Ed25519 密钥签名吗（RFC 8463）？为什么“算法升级”很重要？
▼

**背景**

早期 DKIM（RFC 6376）默认用 RSA-SHA256，密钥长度大（1024/2048 位），DNS 记录体积大；RFC 8463 引入 Ed25519（椭圆曲线）签名，密钥与签名更短、验证更快。

**机制**

签名头写 a=ed25519-sha256，公钥以 k=ed25519 存于 TXT；同一封邮件可同时附 RSA 与 Ed25519 双签，兼顾“老验证器兼容”与“新验证器高效”。

**价值**

Ed25519 在同等安全下密钥仅 32 字节，减小 DNS 负载、加速验证；是 DKIM 现代化方向。

**实践**

部署时建议“RSA+Ed25519 双签”，待对端普遍支持后再逐步弃用 RSA；注意 DNS 记录长度与 TTL 规划。

参考：RFC 8463（DKIM 的 Ed25519 签名，更新 RFC 6376）；RFC 6376（DKIM 基础）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-ed25519-signature.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
