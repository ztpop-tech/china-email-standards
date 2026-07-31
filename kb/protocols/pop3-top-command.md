---
title: "POP3 的 TOP 命令（RFC 1939）如何“只取头部+前几行”而不下载整信？"
source: "https://ztpop.net/kb/pop3-top-command.html"
license: CC-BY 4.0
---

# POP3 的 TOP 命令（RFC 1939）如何“只取头部+前几行”而不下载整信？

1
POP3 的 TOP 命令（RFC 1939）如何“只取头部+前几行”而不下载整信？
▼

**用途**

TOP msg n 返回“指定邮件的信头 + 正文前 n 行”，不下载全信体；常用于预览/索引，省带宽（尤其大附件信）。

**场景**

移动/慢网客户端先 TOP 看主题与发件人决定是否下载整信；或服务器侧做“头同步”再按需 RETR。

**限制**

TOP 拿不到完整正文，无法全文搜索/判定；要读全信仍需 RETR。部分老旧实现 TOP 行为不一致需兼容。

**对比**

IMAP 的 BODYSTRUCTURE/部分获取更精细；POP3 仅 TOP 这一“头+少量行”的轻量预览手段，是其有限能力下的实用优化。

参考：RFC 1939 §7.6（POP3 TOP 命令）；RFC 3501（IMAP 部分获取对比）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/pop3-top-command.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
