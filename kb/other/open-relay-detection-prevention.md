---
title: "开放中继（open relay）是什么？怎么检测自己的邮件服务器有没有被当成垃圾跳板？"
source: "https://ztpop.net/kb/open-relay-detection-prevention.html"
license: CC-BY 4.0
---

# 开放中继（open relay）是什么？怎么检测自己的邮件服务器有没有被当成垃圾跳板？

1
开放中继（open relay）是什么？怎么检测自己的邮件服务器有没有被当成垃圾跳板？
▼

**未授权中继的危害**

RFC 2505 第 2.1 节（Restricting unauthorized Mail Relay usage）指出：未授权地把一台主机当作邮件中继（Mail Relay），属于对该中继资源的窃取，并使其所有者的信誉面临风险；因此 MTA **必须（MUST）**能够控制并拒绝此类中继使用。被当作开放中继的主机，IP 会被各大黑名单（DNSBL/RBL）收录，导致正常邮件也遭拒。

**中继授权的依据**

RFC 2505 第 2.1 节给出授权判定流程：a) 若来自我们信任的网络/客户 IP 段，则接受中继；b) 若目的域是我们应当转发到的（如备用 MX），则接受中继；c) 否则拒绝中继。即中继应只针对「已认证/信任源」或「明确的备用 MX 关系」开放，绝不对互联网任意来源开放。

**怎么检测自己是否中招**

RFC 2505 第 2.4 节要求 MTA 应当（SHOULD）记录所有反中继/反垃圾动作（含「Relaying Denied」等日志），这是发现被探测或被利用的第一手证据。第 2.9 节建议验证 MAIL From 域（用 DNS 或反向检查）、第 2.10 节建议验证外发邮件的 local-part，可暴露伪造信封；第 2.11 节要求控制谁能使用 SMTP VRFY 与 EXPN，防止被借作探测。

**加固清单**

结合 RFC 2505 建议的运维实践：默认拒绝中继，仅对通过身份认证或来自信任网络的连接开放；关闭对外的 VRFY/EXPN（EXPN 默认应关）；记录并监控中继拒绝日志，发现异常高频拒绝即排查；定期用公开开放中继测试工具与 DNSBL 查询核查自身发信 IP 信誉；在边界网关叠加速率限制与内容过滤。

参考：https://www.rfc-editor.org/rfc/rfc2505.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/open-relay-detection-prevention.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
