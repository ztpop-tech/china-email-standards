---
title: "DKIM 密钥应如何轮换？密钥长度有什么要求？"
source: "https://ztpop.net/kb/dkim-key-rotation.html"
license: CC-BY 4.0
---

# DKIM 密钥应如何轮换？密钥长度有什么要求？

1
DKIM 密钥应如何轮换？密钥长度有什么要求？
▼

**长度要求**

RFC 6376 允许 1024 位 RSA，但 RFC 8301 §3.1 已弃用 SHA-1 并将最小推荐提升至 2048 位；新部署应使用 2048 位（或 Ed25519）RSA，避免 1024 位以下或 SHA-1。

**轮换方式**

生成新密钥对，先把新公钥以“新 selector”（如 sel2026）发布到 DNS，发信逐步切到新 selector 签名；观察无问题后再撤销旧 selector 公钥，实现零中断轮换。

**频率**

建议每年或在密钥暴露风险升高时轮换；selector 命名带日期便于管理。撤销旧密钥前需确认所有发信系统已切到新 selector。

**安全**

私钥存于 HSM / 受限文件，绝不入版本库；DNS 公钥为公开文本，但仍建议启用 DNSSEC 防篡改。

参考：RFC 6376（DKIM）；RFC 8301 §3.1（密钥长度）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-key-rotation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
