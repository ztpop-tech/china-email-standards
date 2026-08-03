---
title: "Backup MX 与邮件连续性（容灾）如何配置？"
source: "https://ztpop.net/kb/backup-mx-email-continuity.html"
license: CC-BY 4.0
---

# Backup MX 与邮件连续性（容灾）如何配置？

1
Backup MX 与邮件连续性（容灾）如何配置？
▼

**MX 优先级设计**

按 RFC 5321，MX 记录以偏好值（preference）排序，主 MX 取较小值、备 MX 取较大值。正常时邮件投递到主 MX；主不可达时发送方 MTA 依次尝试优先级更高（数值更大）的备 MX，备机缓存后转发给主机，实现容错。

**备 MX 的安全陷阱**

常见错误是备 MX 放松过滤（不查 SPF/不扫毒），成为绕过主网关的「后门」。备 MX 必须执行与主站一致的认证与反垃圾/反恶意软件策略，否则攻击者可直连备机投递被主站拦截的垃圾或恶意邮件；同时备机不得成为开放中继。

**邮件连续性网关**

现代企业用连续性/归档网关（store-and-forward）在主机或网络中断时代为接收并排队，恢复后回投，避免超时退信（典型 SMTP 重试窗口 4–5 天）。可部署为云服务的 secondary MX，平时即参与过滤，中断时兼做缓存。

**切换与回切演练**

明确主备角色与故障判定阈值；定期演练主备切换与回切，验证队列不丢信、不重复。连续性方案应与备份、DNS TTL、证书有效期协同规划，避免恢复时因 TTL 或证书过期造成二次中断。

参考：RFC 5321《SMTP》MX 与排队重试、RFC 974《邮件路由与域名系统》、邮件连续性网关部署最佳实践（Mimecast/Proofpoint 等）。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/backup-mx-email-continuity.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
