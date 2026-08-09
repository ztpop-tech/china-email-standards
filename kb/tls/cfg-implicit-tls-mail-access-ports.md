---
title: "邮件收发端口为什么建议用隐式 TLS？465/993/995 与 STARTTLS 端口该怎么选？"
source: "https://ztpop.net/kb/cfg-implicit-tls-mail-access-ports.html"
license: CC-BY 4.0
---

# 邮件收发端口为什么建议用隐式 TLS？465/993/995 与 STARTTLS 端口该怎么选？

**RFC 8314 的核心主张**

RFC 8314 的标题已经表明立场：邮件传输中的明文应被视为过时。该文档针对的是用户与自家邮件服务之间的两段链路——邮件提交（Submission）与邮件访问（IMAP/POP），建议这两段一律使用隐式 TLS，并停止使用明文，同时明确它讨论的不是 MTA 之间的中继链路。

**隐式 TLS 与 STARTTLS 的区别**

隐式 TLS 指连接建立后立即开始 TLS 握手，整个会话从第一个字节起就是加密的；STARTTLS 则先明文连接、通过命令升级。二者最终都是 TLS，区别在于 STARTTLS 存在一段明文窗口，能力通告可被剥离，因而具备被降级的可能。隐式 TLS 没有这段窗口——降级尝试只会表现为握手直接失败，而不是无声回落到明文。

**端口对应关系**

RFC 8314 为隐式 TLS 的邮件提交指定了 465 端口并给出服务名 submissions；邮件访问方面对应 993（IMAP over TLS）与 995（POP3 over TLS）。587 端口配合 STARTTLS 的提交方式仍然可用，但文档的建议是优先采用隐式 TLS，并且要求邮件客户端默认就使用 TLS、而不是把加密做成一个需要用户手动打开的选项。

**迁移顺序**

建议按「先加、后关」的顺序推进：第一步在 465/993/995 上把隐式 TLS 服务开起来，与现有端口并行；第二步把客户端默认配置与自动配置文件（如各类账户自动发现机制）改为指向隐式 TLS 端口；第三步观测明文端口（110/143 及未加密提交）的残余连接来源；第四步在残余连接归零或已逐一改造后，再关闭明文端口。跳过第三步直接关端口，是最常见的中断原因。

**容易被漏掉的存量连接**

残余明文连接往往不来自人，而来自各类自动化调用方——监控告警、定时任务、打印与扫描一类的嵌入式设备、以及历史遗留的内部集成。这些调用方通常没有界面、也无人认领，需要靠服务端连接日志按源 IP 反查责任方，并预留足够的改造窗口。把它们统计清楚，是能否安全关闭明文端口的实际判定依据。

**别忘了身份校验**

端口切换只解决了「是否加密」，不解决「加密给了谁」。客户端必须校验服务器证书，RFC 7817 给出了邮件场景下更新后的身份核对流程。若客户端配置为忽略证书错误，即便用了 465/993/995，防护效果也会被显著削弱。

参考：[RFC 8314 Cleartext Considered Obsolete: Use of TLS for Email](https://www.rfc-editor.org/rfc/rfc8314.html) ｜ [RFC 7817 Updated TLS Server Identity Check Procedure for Email](https://www.rfc-editor.org/rfc/rfc7817.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cfg-implicit-tls-mail-access-ports.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
