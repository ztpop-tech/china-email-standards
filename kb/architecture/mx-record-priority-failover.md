---
title: "MX 记录优先级与故障转移如何设计？"
source: "https://ztpop.net/kb/mx-record-priority-failover.html"
license: CC-BY 4.0
---

# MX 记录优先级与故障转移如何设计？

1
MX 记录优先级与故障转移如何设计？
▼

**优先级语义**

MX 记录形如 `10 mx1.x.com`、`20 mx2.x.com`，**数值越小优先级越高**。发送方先尝试最小优先级的服务器；若连接失败或返回持久错误，再按数值升序尝试下一台。相同优先级则按轮询分摊流量。该机制由 RFC 974/5321 规定。

**故障转移设计**

* **跨地域部署**：把高、低优先级 MX 放在不同机房/运营商，主节点宕机时流量自动切到备节点；
* **梯度而非并列**：用 10/20 而非 10/10，可明确主备，避免脑裂；若需负载均衡再用相等优先级；
* **容量对等**：备 MX 必须能承接主节点全部队列，否则故障期会丢信。

**TTL 与运维注意**

MX 记录的 TTL 不宜过短（频繁解析增加 DNS 压力），也不宜过长（故障切换迟钝），通常 300–3600 秒。变更优先级时先调低 TTL 再改记录。注意 MX 指向的主机本身需有正确 A/AAAA 与反向解析，且监听 25 端口可达。

参考：RFC 974《Mail Routing and the Domain System》、RFC 5321《SMTP》5 节 MX 处理、RFC 1035 DNS MX 资源记录。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mx-record-priority-failover.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
