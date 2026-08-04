---
title: "IMAP4rev2（RFC 9051）相较 rev1 有哪些变化？"
source: "https://ztpop.net/kb/rfc9051-imap4rev2-new.html"
license: CC-BY 4.0
---

# IMAP4rev2（RFC 9051）相较 rev1 有哪些变化？

1
IMAP4rev2（RFC 9051）相较 rev1 有哪些变化？
▼

**概览与兼容**

§1.3：IMAP4rev2 Obsoletes RFC 3501，整体向上兼容 IMAP4rev1，仅移除/替换了少数 proven problematic 的设施；支持 63-bit 的报文与正文大小。废弃命令、响应与数据格式在附录 A/E 描述。

**邮箱名与 UTF-8**

§5.1：IMAP4rev2 中邮箱名编码为 **Net-Unicode**（区别于 rev1），客户端 MAY 创建 Net-Unicode 名、MUST 把 LIST 返回的 8-bit 名解释为 Net-Unicode，服务器可把非规范化 UTF-8 转为 NFC。§4.3.1：实现 MUST 接受并 MAY 发送 quoted-string 中的 UTF-8 文本（不含 NUL/CR/LF）。

**LITERAL+ 与废弃项**

§4.3：非同步 literal（`{n+}`）语义已入基础，服务器 MUST NOT 向客户端发送、且非同步 literal MUST NOT 超过 4096 字节，更大 literal 须用同步形式。§2.3.2/6.3.2：**\Recent 系统标志与 RECENT 响应在 rev2 中已废弃**，纯 rev2 客户端应忽略未标记的 RECENT 响应。

**命令与能力变化**

§6：`ENABLE` 命令（§6.3.1）纳入基础规范，用于客户端显式启用扩展；`MOVE` 列为 Selected 状态基础命令（§6.4.8）。§6.1.1：服务器 CAPABILITY 响应 MUST 含 `IMAP4rev2`，MUST 实现 STARTTLS 与 LOGINDISABLED（明文端口）、AUTH=PLAIN（明文与隐式 TLS 端口）；§2.2 强化了严格语法规则——多余/缺失空格为语法错误，BAD 响应不改变连接状态。

参考：RFC 9051（IMAP4rev2），https://www.rfc-editor.org/rfc/rfc9051 —— 章节 1.3 / 5.1 / 4.3 / 4.3.1 / 2.3.2 / 6.3.2 / 6.3.1 / 6.4.8 / 6.1.1 / 2.2

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc9051-imap4rev2-new.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
