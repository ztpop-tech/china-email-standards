---
title: "如何追溯一封邮件的真实来源 IP 与中转跳数？"
source: "https://ztpop.net/kb/header-faq-05.html"
license: CC-BY 4.0
---

# 如何追溯一封邮件的真实来源 IP 与中转跳数？

1
如何追溯一封邮件的真实来源 IP 与中转跳数？
▼

**从底向上找第一个真实 IP**

Received 链中每一跳的 from 括号里常带对端 IP。最底部（最初发出）的 Received 的 IP 最接近原始发送主机；但需注意：若发送方通过 Web 邮箱或受管中继发出，最底 IP 可能是其服务商出口，而非最终用户。

**核对 HELO/EHLO 名**

有时 Received 里还会出现 HELO/EHLO 自报的 hostname，应与连接 IP 的反向解析（PTR）相互印证；不一致可作为可疑信号。

**统计跳数与时间线**

数 Received 头个数即为中转跳数（含起点与终点）；对比各跳 date 时间戳，若出现时间倒流、跳数异常多（如 10+ 跳）或被篡改痕迹，需警惕路由伪造。

**结合外部情报**

将定位到的源 IP 与威胁情报、SPF 记录中的授权网段、已知合法中继比对，判断是否属于该发件域的正常发送基础设施。

参考：RFC 5321（Received 头与源 IP）；邮件溯源实务

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/header-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
