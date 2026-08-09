---
title: "邮件网关入站 TLS 策略怎么配才既安全又不丢信？"
source: "https://ztpop.net/kb/gw-postfix-inbound-tls-policy.html"
license: CC-BY 4.0
---

# 邮件网关入站 TLS 策略怎么配才既安全又不丢信？

**先分清入站与出站是两套完全不同的策略**

很多事故源于把出站的 TLS 要求照搬到入站。RFC 3207 第 4 节明确指出，公网 MX 端口（25）上的 STARTTLS 是机会性的：服务端可以提供，但不能因为对端不支持就拒收邮件，否则会造成合法邮件永久投递失败。入站 25 端口的目标是「尽可能加密」，出站与提交（587）的目标才是「必须加密」。

因此判定逻辑是按端口分层：25 端口机会性 TLS、587 提交端口强制 TLS + 认证、内部中继按对端逐一指定强制策略。

**Postfix 上的档位含义**

`smtpd_tls_security_level` 在 Postfix 中有三个常用取值：`none` 完全不提供 STARTTLS；`may` 提供但不强制，明文连接照常接收；`encrypt` 强制，未加密时拒绝 MAIL FROM。TLS\_README 明确说明 `encrypt` 不得用于公网 MX。

典型配置：main.cf 中 `smtpd_tls_security_level = may`；master.cf 的 submission 服务上用 `-o smtpd_tls_security_level=encrypt` 覆盖，同时配 `-o smtpd_tls_auth_only=yes`，保证认证凭据不会在明文信道上传输。

**协议版本与套件的收敛**

把已被弃用的协议关掉，而不是靠加密套件黑名单去打补丁。Postfix 中用 `smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1` 与 `smtpd_tls_protocols` 同步收敛；NIST SP 800-177 Rev.1 对邮件传输层同样建议使用当前受支持的 TLS 版本并禁用已知弱算法。

需要注意机会性 TLS 下不要把套件收得过窄：对端如果是老旧 MTA，握手失败会退回明文（这是可接受的），但若同时配了强制策略就会变成退信。收窄套件前先用日志确认实际分布。

**证书与 SNI**

入站证书的主体名要覆盖 MX 记录里出现的主机名，而不是邮件域名本身——对端按 MX 主机名做校验。若一台网关承载多个 MX 主机名，使用 Postfix 的 `tls_server_sni_maps` 按名下发对应证书，避免用一张证书堆叠过多 SAN 带来的轮换风险。

证书链要下发完整的中间 CA。缺中间证书在浏览器里常被自动补全，但多数 MTA 不会补，表现为对端间歇性校验失败。

**上线前后的观测**

打开 `smtpd_tls_loglevel = 1` 记录握手结果，统计三项指标：入站连接中 TLS 占比、握手失败的对端分布、协商到的协议版本分布。收敛协议版本前后各观测一个完整周期（含周末批量任务），确认没有出现集中的握手失败源。

判定基线：若某个 IP 段在收敛后握手失败率骤升且该源确有业务邮件，优先回退再排查对端，不要以「对端不合规」为由长期挂起投递。

参考：[RFC 3207 SMTP Service Extension for Secure SMTP over TLS](https://www.rfc-editor.org/rfc/rfc3207.html) ｜ [Postfix TLS\_README](https://www.postfix.org/TLS_README.html) ｜ [NIST SP 800-177 Rev. 1 Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-postfix-inbound-tls-policy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
