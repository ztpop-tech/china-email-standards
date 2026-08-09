---
title: "Authentication-Results 头能直接采信吗？信任边界该怎么划？"
source: "https://ztpop.net/kb/ir-auth-results-trust-boundary-2026.html"
license: CC-BY 4.0
---

# Authentication-Results 头能直接采信吗？信任边界该怎么划？

1
Authentication-Results 头能直接采信吗？信任边界该怎么划？
▼

**核心结论：只有自己写的那条可以采信**

Authentication-Results 是一个普通的邮件头字段，任何人都能在发信时自行加上一条写着「全部通过」的内容。它本身不带任何密码学保护。因此研判时必须能够区分：哪一条是本方基础设施写入的，哪一条是随邮件带进来的。

**规范的强制要求：边界必须剥离外来实例**

RFC 7601《Message Header Field for Indicating Message Authentication Status》第 5 节标题即为 Removing Existing Header Fields，其中规定：符合规范的 MTA 必须删除那些声称由其信任边界内添加、但实际上并非来自另一受信任 MTA 的 Authentication-Results 头字段实例。边界 MTA 可以简单地移除所有跨入信任边界的邮件中的该类头字段，或仅放行来自特定受信任认证 MTA 的实例。该节还要求：对于携带不受支持版本的该头字段应当移除；若 SMTP 连接来自非受信任的内部 MTA，则必须移除。

**怎么落地划定信任边界**

信任边界 = 本组织实际控制、且已按上述要求配置了剥离逻辑的那一组 MTA。落地检查三件事：1) 入站边界是否已配置对外来 Authentication-Results 的无条件剥离；2) 本方写入该头时是否带有可识别的 authserv-id（用于标明是哪台服务器做的评估）；3) 内部各跳之间是否明确了哪些属于受信任 MTA，避免内部转发链把外来结果带过边界。任一项缺失，该头在研判中就不可用。

**研判时的读法**

在原始邮件中自上而下找到第一条 authserv-id 与本方边界服务器标识相符的Authentication-Results，以它为准；其下若还存在其他实例，视为外部输入，仅作参考不作依据。若边界未做剥离而头中存在多条，则应判定该头整体不可信，转而回到 Received 链与网关日志中取证。

**常见误区**

误区一：看到 dmarc=pass 就放行。认证通过只说明该域授权了这次发送并与 From 对齐，近似域完全可以自建并全部通过。误区二：把邮件客户端展示的「已验证」标记当作依据——客户端展示可能基于未经剥离的原始头。误区三：在内部转发后重新评估并覆盖原结果，导致丢失边界处的原始判定。

参考：[RFC 7601](https://www.rfc-editor.org/rfc/rfc7601.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ir-auth-results-trust-boundary-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
