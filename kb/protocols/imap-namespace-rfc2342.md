---
title: "IMAP 的 NAMESPACE 扩展（RFC 2342）解决什么？它如何支持“共享/公共文件夹”？"
source: "https://ztpop.net/kb/imap-namespace-rfc2342.html"
license: CC-BY 4.0
---

# IMAP 的 NAMESPACE 扩展（RFC 2342）解决什么？它如何支持“共享/公共文件夹”？

1
IMAP 的 NAMESPACE 扩展（RFC 2342）解决什么？它如何支持“共享/公共文件夹”？
▼

**问题**

不同邮件系统对“用户前缀（如 INBOX.）”“共享文件夹”“公共文件夹”的命名层级不同，客户端难统一呈现；RFC 2342 的 NAMESPACE 让服务器“自报层级结构”。

**机制**

NAMESPACE 命令返回三类命名空间：个人（#private）、其他用户共享（#shared/#user）、公共（#public），各带分隔符与前缀，客户端据此正确定位与展示。

**价值**

跨系统兼容的关键——让用户“看到别人的共享箱/公共文件夹”而不必硬编码路径；是集团邮箱、委托访问的呈现基础。

**实践**

邮件系统开启 NAMESPACE 扩展后，客户端（如 Thunderbird/Outlook）能自动发现并挂载共享与公共文件夹，提升协作体验。

参考：RFC 2342（IMAP4 NAMESPACE 扩展）；RFC 3501

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-namespace-rfc2342.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
