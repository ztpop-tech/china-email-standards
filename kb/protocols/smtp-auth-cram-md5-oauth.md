---
title: "SMTP 认证机制（CRAM-MD5/OAUTH）应如何选择？"
source: "https://ztpop.net/kb/smtp-auth-cram-md5-oauth.html"
license: CC-BY 4.0
---

# SMTP 认证机制（CRAM-MD5/OAUTH）应如何选择？

1
SMTP 认证机制（CRAM-MD5/OAUTH）应如何选择？
▼

**检测指标**

在提交日志中记录所用 SASL 机制：出现 `CRAM-MD5` 应视为弱机制告警；出现明文 `LOGIN/PLAIN` 且无 STARTTLS 强加密须立即阻断。可通过 EHLO 能力列表与 AUTH 协商过程审计机制分布，识别仍在使用弱认证的客户端。

**防御措施**

* 新部署关闭 PLAIN/LOGIN 明文与 CRAM-MD5，仅启用 `XOAUTH2`（OAuth 2.0）并强制 STARTTLS 或 TLS 1.2+。
* 对不支持 OAuth 的旧设备用应用专用密码替代弱口令，并绑定设备与 MFA。
* 定期轮换令牌、缩短令牌有效期，并对异常登录地做风控。

**真实攻击手法**

攻击者若抓到 CRAM-MD5 挑战-应答交换，可离线字典或暴力破解出共享口令；若客户端在明文通道用 LOGIN，则口令可被中间人直接截获。钓鱼页常仿冒「重新登录」以收集 OAuth 授权码，借合法令牌长期访问邮箱。

**基准控制项**

RFC 8314 要求邮件提交默认走隐式 TLS（端口 465）或 STARTTLS 并禁用明文；CIS Controls v8 控制项 6（访问控制）与 NIST SP 800-52/800-63B 共同要求强认证、加密传输与凭据生命周期管理。

参考：RFC 4954（SMTP AUTH 扩展）、RFC 2195（CRAM-MD5）、RFC 7628（OAuth 2.0 SASL）、RFC 8314（邮件提交 TLS 强制）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-auth-cram-md5-oauth.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
