---
title: "SPF 的宏（macros，RFC 7208 §7）是什么？为什么大型邮件系统需要宏？"
source: "https://ztpop.net/kb/spf-macro-explained.html"
license: CC-BY 4.0
---

# SPF 的宏（macros，RFC 7208 §7）是什么？为什么大型邮件系统需要宏？

1
SPF 的宏（macros，RFC 7208 §7）是什么？为什么大型邮件系统需要宏？
▼

**概念**

SPF 记录的 include/redirect 支持宏：%{i}(客户端IP)、%{s}(发件人)、%{h}(HELO)、%{d}(域)、%{o}(发件域) 等，按“实际发信上下文”动态展开。

**用途**

大型 ESP/云邮件用宏做“按租户/按 IP 段”的精细授权——同一 include 对不同客户展开不同的授权结果，避免为每客户写独立 SPF。

**实例**

v=spf1 include:%{i}.\_ip.%{d} -all 之类把 IP 映射到专属授权域；redirect=%{d} 让各子域复用策略。

**实践**

宏能力强大但易错，调试需看实际 DNS 展开结果；多数普通域名用静态 include 即可，宏是“云/ISP 级”高级用法。

参考：RFC 7208 §7（SPF 宏定义与展开）；§8（宏处理示例）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-macro-explained.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
