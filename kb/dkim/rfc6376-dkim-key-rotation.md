---
title: "DKIM（RFC 6376）密钥如何轮转与撤销？"
source: "https://ztpop.net/kb/rfc6376-dkim-key-rotation.html"
license: CC-BY 4.0
---

# DKIM（RFC 6376）密钥如何轮转与撤销？

1
DKIM（RFC 6376）密钥如何轮转与撤销？
▼

**签名核心标签**

§3.5 定义 `DKIM-Signature` 头字段的 `tag=value`：`v=`（必为 1）、`a=`（签名算法，验证器 MUST 支持 rsa-sha1 与 rsa-sha256，签名者 SHOULD 用 rsa-sha256）、`c=`（规范化，默认 `simple/simple`）、`d=`（SDID）、`s=`（selector）、`t=`（签名时间戳，建议含）、`x=`（过期时间，须大于 t=）、`h=`（签名头字段列表，MUST NOT 为空）、`bh=` 与 `b=`（哈希与签名数据）。

**规范化算法**

§3.4 提供 simple 与 relaxed 两种算法，签名者可对头与正文分别选择；**未指定 `c=` 时头与正文均默认 simple**。relaxed 容忍头字段折行展开、空格归一、行尾空白等常见修改，更适合经过列表网关转发的邮件；验证器 MUST 同时实现两者。

**密钥轮转实践**

§3.1 与 §5.2 给出轮转方法：通过 selector 细分布局，新密钥用**新的 selector** 发布公钥，过渡期内新旧公钥在 DNS 并存；签名应立即用新私钥开始，旧公钥保留一段合理验证窗口后再删除。**不应把新密钥复用旧 selector**，更好的策略是分配新 selector（如从 january2005 换到 february2005）。

**密钥长度与撤销**

§3.3.3 要求长期密钥 MUST 使用至少 1024 位 RSA，验证器须能校验 512–2048 位；Ed25519 由 RFC 8463 另行定义。撤销见 §3.6.1：公钥记录中 `p=` 为空即表示该公钥已撤销，验证器 SHOULD 对引用被撤销密钥的签名返回错误；文档明确“被撤销的密钥与已删除的密钥无语义差异”。

参考：RFC 6376（DKIM Signatures），https://www.rfc-editor.org/rfc/rfc6376 —— 章节 3.5 / 3.4 / 3.1 / 3.3.3 / 3.6.1 / 5.2

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc6376-dkim-key-rotation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
