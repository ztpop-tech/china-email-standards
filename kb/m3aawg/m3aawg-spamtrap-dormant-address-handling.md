---
title: "M3AAWG 对“垃圾陷阱（spamtrap）/休眠地址”的处理给出什么建议？"
source: "https://ztpop.net/kb/m3aawg-spamtrap-dormant-address-handling.html"
license: CC-BY 4.0
---

# M3AAWG 对“垃圾陷阱（spamtrap）/休眠地址”的处理给出什么建议？

1
M3AAWG 对“垃圾陷阱（spamtrap）/休眠地址”的处理给出什么建议？
▼

**什么是垃圾陷阱**

垃圾陷阱是不发送也不订阅任何列表的监控地址，运营商据此评估 IP/域声誉并喂给 DNSBL（如 DNSBL）。命中陷阱会损害发送方信誉，严重时被大范围拦截。

**回收型陷阱**

Recycled trap：曾是被真人使用、闲置一段时间后被转成陷阱的地址。M3AAWG 建议以 12 个月作为最小闲置期阈值。命中此类陷阱通常说明列表陈旧、退信处理缺失或缺乏 sunsetting（休眠清理）策略。

**纯净型陷阱**

Pristine/pure：从未作为合法地址存在、因拼写错误/字典攻击/抓取而收到邮件，命中说明在抓取或购买清单。

**缓解措施**

采用确认订阅（double opt-in）从源头防止陷阱入列；采集时即时校验地址格式与 MX；建立 sunset 策略——对长期无互动（如一年）的订阅者发 re-permission 再确认，无响应则抑制；正确处理硬退信立即移除；禁止购买/抓取清单。邮件服务方（ESP）应监控并向客户通报陷阱命中、审计其地址获取方式。

参考：M3AAWG · Help! I've Hit a Spam Trap! / Spamtrap Operations BCP 2016（Recycled trap, 12-month）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-spamtrap-dormant-address-handling.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
