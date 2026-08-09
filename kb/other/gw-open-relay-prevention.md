---
title: "怎么确认网关没有成为开放中继？中继滥用如何防护？"
source: "https://ztpop.net/kb/gw-open-relay-prevention.html"
license: CC-BY 4.0
---

# 怎么确认网关没有成为开放中继？中继滥用如何防护？

**开放中继的定义要精确**

开放中继指：任意未经授权的客户端，可以让你的服务器把邮件投递到与你无关的第三方域。判定的关键是「收件域不属于本机负责的域」且「客户端未经授权」两个条件同时成立。

RFC 5321 第 7.2 节明确警示了未加限制的中继带来的滥用风险，要求实现提供限制中继的机制。注意：为本机负责的域接收邮件不是中继；已认证用户提交邮件到外部域是被授权的中继，也不算开放中继。

**Postfix 里真正决定中继的三组参数**

`mynetworks` 定义无需认证即可中继的可信网段——这是最常被配错的一项，写成过宽的网段（例如整个内网 B 段甚至 `0.0.0.0/0`）等同于开放中继。

`relay_domains` 定义本机愿意为哪些域做中继转发（典型是下游邮件系统的域）；`mydestination` 与虚拟域相关参数定义本机最终投递的域。三者混淆会导致本该本地投递的域被当作中继目标。

最终裁决在 `smtpd_recipient_restrictions`（或 `smtpd_relay_restrictions`）里。SMTPD\_ACCESS\_README 强调这些限制按列表顺序求值，遇到第一个明确的 permit 或 reject 即终止。

**限制条件的书写顺序**

推荐的基本骨架是：`smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, defer_unauth_destination`。含义是——可信网段放行、已认证放行、其余凡是投向非本机负责域的一律拒绝。

两个常见错误：一是把 `permit` 放在列表末尾之外的位置，导致后面的拒绝规则永远不生效；二是在 `smtpd_recipient_restrictions` 里遗漏了兜底的拒绝项，使默认行为变成放行。任何 permit 类条件之后，必须有明确的拒绝兜底。

**自检怎么做**

外部验证：从一台不在 mynetworks 内的主机连接 25 端口，在不认证的前提下执行 `MAIL FROM:<test@外部域A>` 与 `RCPT TO:<test@外部域B>`，两个域都与你无关。服务器必须在 RCPT 阶段拒绝。若返回 250，即为开放中继。

同时要测几个变形，因为经典漏洞往往出在解析上：带引号的路径、百分号跳转形式（`user%外部域@本域`）、源路由形式（`@本域:user@外部域`）、以及大小写与多余空格。现代 Postfix 默认不接受这些形式，但若曾自定义过地址改写规则就必须逐一验证。

配置侧验证用 `postconf -n` 导出非默认配置，逐项核对 mynetworks 的实际展开值（`postconf mynetworks` 会显示解析后的结果，比读 main.cf 更可靠）。

**认证后的滥用同样要防**

更常见的现实风险不是匿名开放中继，而是账号被盗后的「授权中继滥用」。防护手段是对已认证连接也施加约束：限制单账号的消息与收件人速率、强制 `smtpd_sender_login_maps` 保证 MAIL FROM 与登录账号一致（防止盗号后冒用他人身份）、并对提交端口的异常地理位置与时间分布告警。

被滥用后的排查顺序：从队列中取样，读消息头里的 `Received` 首跳与 `sasl_username` 记录，确定是哪个账号与哪个源 IP；随后 hold 该账号的全部在途消息，改密并吊销会话，最后清理队列并统计已外发量以评估信誉损失。

参考：[RFC 5321 Simple Mail Transfer Protocol](https://www.rfc-editor.org/rfc/rfc5321.html) ｜ [Postfix SMTPD\_ACCESS\_README](https://www.postfix.org/SMTPD_ACCESS_README.html) ｜ [Postfix postconf(5) 配置参数手册](https://www.postfix.org/postconf.5.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-open-relay-prevention.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
