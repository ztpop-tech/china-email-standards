---
title: "现有 STARTTLS 链路怎么平滑过渡到国密传输？"
source: "https://ztpop.net/kb/xc-starttls-to-guomi-transport-migration.html"
license: CC-BY 4.0
---

# 现有 STARTTLS 链路怎么平滑过渡到国密传输？

**先认清 STARTTLS 的固有弱点**

RFC 3207 SMTP Service Extension for Secure SMTP over Transport Layer Security 定义的 STARTTLS 是**机会式加密**：客户端先以明文建立连接，看到服务端通告 STARTTLS 能力后再升级为加密。这一设计存在两个结构性弱点：

* **能力通告可被剥离**：中间人删掉通告行，双方就会以明文继续通信，且通常不会告警。
* **是否加密取决于对端**：对端不支持时，多数实现会静默降级为明文投递。

正因如此，RFC 8314 Cleartext Considered Obsolete: Use of TLS for Email Submission and Access 明确主张邮件提交与访问应使用隐式 TLS，把明文视为过时做法。**过渡到国密的同时，正好一并解决这个历史问题。**

**第一步：让现状可观测，不要先动配置**

改造前必须知道当前真实状况，否则一旦强制就会出现不可预期的投递失败。

**可操作做法：**

1. 在日志中为每次连接记录：是否建立 TLS、协议版本、协商套件、证书校验结果、失败原因。
2. 按对端域聚合，得出「哪些域始终加密、哪些域偶发失败、哪些域从不加密」。
3. 部署 RFC 8460 SMTP TLS Reporting 定义的 TLS 报告接收能力，获取**对端视角**的加密失败数据——这是本端日志看不到的部分。
4. 观察至少一个完整业务周期后再进入下一步。

**第二步：分段推进，从两端都可控的链路开始**

按「可控程度」排序推进，每段的目标状态不同：

1. **客户端接入段**（提交/IMAP/POP/Web）：改为隐式 TLS 端口，禁用明文认证；具备条件时启用国密协商。两端可控，可强制。
2. **内部服务器间段**（网关↔MTA↔存储↔目录↔日志）：全部启用加密并强制对端校验，可直接上国密。**这一段最常被以「都在内网」为由跳过，但它同时是等保与密评的必查项。**
3. **已确认支持国密的伙伴域**：配置为强制国密，并设置协商失败告警。
4. **互联网通用域**：保持算法可协商，但设定加密下限。

**跨域段的现实约束与底线**

跨域投递的对端不受控，绝大多数外部域不支持国密套件。若强制国密，结果只有一个：邮件发不出去。

**底线原则：回退的允许范围是「换算法」，绝不包括「不加密」。**具体配置为：

* 优先尝试国密套件（RFC 8998 ShangMi (SM) Cipher Suites for TLS 1.3 注册的套件可在 TLS 1.3 框架内协商）。
* 协商不成则回退到符合要求的国际算法与协议版本。
* **禁止回退到明文**；对已知应加密的对端，加密失败应当排队重试并告警，而不是转为明文投递。
* 用 RFC 8461 SMTP MTA Strict Transport Security (MTA-STS) 发布本域策略，防止入站方向被剥离降级。

**降级检测：把「悄悄变差」变成可告警事件**

传输加密最危险的失效形式不是报错，而是**无声降级**：一次证书更换、一次组件升级、一次配置回滚，都可能让协商结果悄然退化，而业务毫无感知。

**可操作的检测机制：**

* 建立**协商结果基线**：记录每个端口、每个主要对端域的期望协议版本与套件。
* 周期性主动握手探测，结果与基线比对，出现降级立即告警。
* 把「明文投递计数」作为独立监控指标，其期望值应为零；任何非零都需查明原因。
* 结合 TLS 报告数据，识别对端视角的失败。

**过渡完成的判定条件**

不要以「配置改完了」作为完成标志。可验证的判定条件：

* 客户端接入段无任何明文可达路径（外部扫描验证）。
* 内部服务器间链路抓包确认全部加密，且证书校验实际生效（用错误证书测试应被拒绝，而非放行）。
* 目标国密链路的协商结果实测符合预期，并已纳入基线监控。
* 明文投递计数连续一个业务周期为零。
* 本域策略与报告接收记录已发布并验证可解析。

TLS 配置的通用建议可参考 NIST SP 800-52 Rev.2 Guidelines for TLS Implementations。

参考：[RFC 3207 SMTP Service Extension for Secure SMTP over Transport Layer Security](https://www.rfc-editor.org/rfc/rfc3207.html) ｜ [RFC 8314 Cleartext Considered Obsolete: Use of TLS for Email Submission and Access](https://www.rfc-editor.org/rfc/rfc8314.html) ｜ [RFC 8998 ShangMi (SM) Cipher Suites for TLS 1.3](https://www.rfc-editor.org/rfc/rfc8998.html) ｜ [RFC 8461 SMTP MTA Strict Transport Security (MTA-STS)](https://www.rfc-editor.org/rfc/rfc8461.html) ｜ [RFC 8460 SMTP TLS Reporting](https://www.rfc-editor.org/rfc/rfc8460.html) ｜ [NIST SP 800-52 Rev.2 Guidelines for TLS Implementations](https://csrc.nist.gov/pubs/sp/800/52/r2/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/xc-starttls-to-guomi-transport-migration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
