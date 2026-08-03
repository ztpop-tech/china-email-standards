---
title: "邮件系统安全加固检查清单应包含哪些项？"
source: "https://ztpop.net/kb/email-security-hardening-checklist.html"
license: CC-BY 4.0
---

# 邮件系统安全加固检查清单应包含哪些项？

1
邮件系统安全加固检查清单应包含哪些项？
▼

**边界与暴露面收敛**

先收缩可被公网直接触达的攻击面，再逐项确认。

* 仅对公网开放 25（入站 SMTP）、465/587（提交）、993/995（IMAP/POP3），其余管理端口（22/80/443 后台）仅限内网或 VPN。
* 在边界防火墙启用连接速率限制与并发连接上限，缓解字典爆破与连接耗尽。
* 禁用开放中继（open relay）：`smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated reject_unauth_destination`。
* 将管理后台、Webmail 置于 WAF 之后并强制 HTTPS，关闭明文 80 端口跳转之外的明文访问。

**认证与加密基线**

认证与传输加密是防止伪造与窃听的基础。

* 提交端口（587）强制 STARTTLS + SASL 登录认证，禁止明文口令。
* 部署 SPF/DKIM/DMARC 三件套并逐步将 DMARC 策略提升到 `p=reject`。
* 全链路 TLS：入站与出站均启用 STARTTLS 强制，禁用 TLS 1.0/1.1 与弱密码套件（RC4、DES、EXPORT）。
* 证书使用受信任 CA 签发，开启 OCSP/CRL 校验与自动续期。

**反钓鱼与内容过滤**

在网关层拦截恶意内容与伪造发件人。

* 启用反病毒与反垃圾引擎（如 SpamAssassin、ClamAV），对附件做沙箱 detonation。
* 对入站邮件做 DMARC 对齐校验，对失败且策略为 reject 的直接拒收。
* 阻断可执行附件（.exe/.scr/.js/.vbs）与宏文档（.docm/.xlsm），对压缩包做二次解压扫描。
* 对呈现「账单/快递/工资」等高风险主题的邮件施加额外权重与用户提示横幅。

**监控、审计与应急**

可观测与可回溯决定事件能否被及时发现与定位。

* 开启发信/收信全量日志并集中到 SIEM，保留不少于 180 天。
* 对异常登录（异地、新设备、高频失败）配置实时告警。
* 定期（季度）执行漏洞扫描与渗透测试，并对照本清单逐项复检、留痕。
* 预置事件响应预案：隔离账号、封堵 IP、取证、通报与复盘的标准动作。

参考：NIST SP 800-45《电子邮箱安全指南》、M3AAWG 发送方最佳实践、RFC 7208/6376/7489。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-security-hardening-checklist.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
