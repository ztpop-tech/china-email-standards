---
title: "电子邮件子地址（subaddressing，RFC 5233，如 name+tag@example.com）是什么？有什么用？"
source: "https://ztpop.net/kb/email-subaddressing.html"
license: CC-BY 4.0
---

# 电子邮件子地址（subaddressing，RFC 5233，如 name+tag@example.com）是什么？有什么用？

1
电子邮件子地址（subaddressing，RFC 5233，如 name+tag@example.com）是什么？有什么用？
▼

**定义**

子地址（subaddressing，RFC 5233）指在本地部分用分隔符（通常“+”）附加标签：user+tag@example.com 仍投递到 user@example.com 邮箱，但标签可被客户端/服务端用于过滤与分类。

**用途**

注册不同服务用不同 tag（user+shop@example.com、user+news@example.com），便于识别来源、按 tag 建过滤规则、发现地址被泄露（某 tag 只给一家后用该 tag 收垃圾即知泄露源）。

**服务端**

是否支持子地址由接收 MTA 决定（如 Gmail、许多 IMAP 支持“+”；分隔符可配置）；不支持的系统会把 +tag 当不存在而拒收或当不同用户。

**安全注意**

攻击者可用子地址探测；另外“+tag”也常用于临时身份，配合邮件网关做投递路由与策略，是地址运维的常用技巧。

参考：RFC 5233（Sieve 子地址扩展 / 邮件子地址）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-subaddressing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
