---
title: "SMTP AUTH 认证失败（535）该怎么定位和处置？"
source: "https://ztpop.net/kb/gw-smtp-auth-failure-triage.html"
license: CC-BY 4.0
---

# SMTP AUTH 认证失败（535）该怎么定位和处置？

**先读响应码，不要一律当成密码错**

RFC 4954 第 6 节区分了几类不同含义的应答：`535 5.7.8` 认证凭据无效；`534 5.7.9` 认证机制过弱；`538 5.7.11` 要求先加密再认证；`454 4.7.0` 临时性认证失败（后端不可用）。前两类是客户端问题，第三类是策略问题，第四类是服务端故障。

把 454 误判为 535 是最常见的误诊——它意味着 SASL 后端（LDAP/数据库/saslauthd）连不上，此时改密码毫无意义。

**第一层：机制协商是否匹配**

客户端只能使用 EHLO 响应中 `250-AUTH` 列出的机制。若服务端只宣告 PLAIN/LOGIN 而客户端配置了 CRAM-MD5，就会在协商阶段直接失败。用 `openssl s_client -starttls smtp -connect host:587` 连上后发 EHLO，核对实际宣告的机制列表。

注意 Postfix 默认在未加密连接上不宣告 AUTH（`smtpd_tls_auth_only = yes` 时），所以明文抓包看不到 AUTH 行是正常现象，不是配置丢失。

**第二层：TLS 与端口是否走对**

RFC 6409 规定邮件提交应走 587 端口并要求认证。若客户端仍在 25 端口尝试 AUTH，而网关按 MX 语义未开放认证，就会得到 538 或直接没有 AUTH 能力。排查时先确认端口，再确认 STARTTLS 是否成功——TLS 握手失败会让后续 AUTH 一并失败，但日志里往往只留下认证报错。

**第三层：SASL 后端链路**

Postfix 自身不做密码校验，它把认证交给 Cyrus SASL 或 Dovecot SASL。SASL\_README 说明了两条路径的配置差异。定位方法是绕过 Postfix 直接测后端：Dovecot 路径检查 `smtpd_sasl_type = dovecot` 指向的 socket 是否存在、权限是否允许 postfix 用户读写（chroot 环境下路径需相对 `/var/spool/postfix`）；Cyrus 路径检查 `saslauthd` 进程与 `testsaslauthd` 结果。

把 `smtpd_sasl_local_domain` 配错会导致用户名被拼上域名后查不到账号，表现为「密码明明对却 535」。

**第四层：区分故障与攻击**

运维上要把「单账号反复失败」和「大量账号各试几次」分开。前者多为客户端配置漂移（改密码后未同步的移动端、定时任务）；后者是密码喷洒，特征是源 IP 集中、每账号失败次数低于锁定阈值、用户名按字典顺序推进。

可操作判定：以 10 分钟为窗口统计（源 IP，失败次数，去重用户名数）。去重用户名数 ≥ 20 且失败率 > 90% 的源 IP 直接进入临时封禁；单用户名失败 ≥ 10 次但源 IP 固定且历史成功过的，先通知用户而非封禁。封禁必须带自动过期，避免把 NAT 出口后的整个办公网长期锁死。

参考：[RFC 4954 SMTP Service Extension for Authentication](https://www.rfc-editor.org/rfc/rfc4954.html) ｜ [Postfix SASL\_README](https://www.postfix.org/SASL_README.html) ｜ [RFC 6409 Message Submission for Mail](https://www.rfc-editor.org/rfc/rfc6409.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-smtp-auth-failure-triage.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
