---
title: "与某主机通信时，Exim 在收到并响应 DATA 命令后超时或连接被关闭，怎么回事？"
source: "https://ztpop.net/kb/exim-faq-05.html"
license: CC-BY 4.0
---

# 与某主机通信时，Exim 在收到并响应 DATA 命令后超时或连接被关闭，怎么回事？

1
与某主机通信时，Exim 在收到并响应 DATA 命令后超时或连接被关闭，怎么回事？
▼

**可能原因**

这类问题成因多样：一种情况是网络丢弃了超过特定大小的数据包，导致 SMTP 事务前半段正常、但大邮件正文开始传输时数据始终过不去（参见 Q0017）；另一种情况是主机 TCP 协议栈损坏、无法重组分片数据报。

**其他**

极少数 ISDN 线路在特定数据模式下会失败，更换链路两端路由器仍无效；曾有案例被连续 4 个以上 X 字符触发。可结合 `exim -bh` 与抓包定位是网络层还是对端实现问题。

参考：Exim FAQ Q0014（exim.org/exim-html-4.40/doc/html/FAQ\_0.html）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
