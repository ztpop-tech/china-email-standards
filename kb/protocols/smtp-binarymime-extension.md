---
title: "SMTP 的 BINARYMIME 扩展（RFC 3030）是什么？与 8BITMIME 有何区别，为何需要 BDAT？"
source: "https://ztpop.net/kb/smtp-binarymime-extension.html"
license: CC-BY 4.0
---

# SMTP 的 BINARYMIME 扩展（RFC 3030）是什么？与 8BITMIME 有何区别，为何需要 BDAT？

1
SMTP 的 BINARYMIME 扩展（RFC 3030）是什么？与 8BITMIME 有何区别，为何需要 BDAT？
▼

**定义**

BINARYMIME 允许在 SMTP 中传输“8 位二进制且含 NUL 字节”的内容（普通 8BITMIME 不允许 NUL），需配合 CHUNKING（BDAT）使用（RFC 3030）。

**与 8BITMIME 区别**

8BITMIME 提升为 8 位文本（仍禁 NUL、需 CTE 处理二进制）；BINARYMIME 真正支持任意二进制（含 NUL），靠 BDAT 分块发送、不用 DATA 的“.”终止约定，避免二进制中误现结束符。

**价值**

对“直接传输已编码的二进制 MIME 体”更安全高效，常见于网关/MTA 间中继、与 LMTP 配合投递，减少重编码损耗。

**部署**

需双方都声明支持 BINARYMIME+CHUNKING（EHLO 可见）；单边不支持则降级 8BITMIME 或 7BIT base64；注意 BINARYMIME 不能用于传统 DATA 命令。

参考：RFC 3030（BINARYMIME 与 CHUNKING / BDAT）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-binarymime-extension.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
