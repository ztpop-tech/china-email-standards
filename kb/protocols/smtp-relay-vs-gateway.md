---
title: "SMTP 中继（relay）与邮件网关（gateway）有什么区别，该怎么选？"
source: "https://ztpop.net/kb/smtp-relay-vs-gateway.html"
license: CC-BY 4.0
---

# SMTP 中继（relay）与邮件网关（gateway）有什么区别，该怎么选？

1
SMTP 中继（relay）与邮件网关（gateway）有什么区别，该怎么选？
▼

**职责边界**

SMTP 中继的核心职责是把邮件「可靠地转发到下一跳」，专注队列、重试、路由与投递保证，通常不含深度安全检测。邮件安全网关则在流量路径上做反垃圾、反病毒、DLP、防钓鱼与认证校验，是安全策略的执行点，往往串接在中继之前或作为边界 MTA。

**典型部署**

常见形态：①边界网关（入站过滤+出站扫描）＋后方中继负责投递；②云中继（如厂商发送服务）只负责 outbound 投递与信誉管理，安全由独立网关承担；③一体化设备同时兼两职。关键看流量是否需在网关处被检测后再决定放行/隔离/拒收。

**选型建议**

若需求只是「把内部应用邮件送到外网且不被拦」，轻量中继＋正确 SPF/DKIM/DMARC 即可；若需合规审计、威胁隔离与入站防护，则必须有安全网关。大型企业常两者叠加：网关做策略与扫描，中继/投递代理做高可用队列。

参考：M3AAWG 发送方最佳实践、RFC 5321《SMTP》中继与转发语义、各厂商邮件安全网关部署指南。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-relay-vs-gateway.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
