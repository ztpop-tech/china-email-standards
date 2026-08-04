---
title: "STARTTLS 被中间人剥离导致明文传输，怎么发现和防住？"
source: "https://ztpop.net/kb/rfc3207-starttls-downgrade-stripping-detection.html"
license: CC-BY 4.0
---

# STARTTLS 被中间人剥离导致明文传输，怎么发现和防住？

1
STARTTLS 被中间人剥离导致明文传输，怎么发现和防住？
▼

**机制回顾：STARTTLS 是在明文会话中协商升级**

RFC 3207 定义的 STARTTLS 是一个 SMTP 服务扩展：**连接先以明文建立，服务端在 EHLO 响应中通告 STARTTLS 关键字，客户端发出 STARTTLS 命令，服务端以 220 应答后双方开始 TLS 握手。**

```
C: (建立 TCP 连接)
S: 220 mail.example SMTP service ready
C: EHLO client.example
S: 250-mail.example
S: 250 STARTTLS          <-- 这一行在明文中传输
C: STARTTLS
S: 220 Go ahead          <-- 这一行也在明文中
C: (开始 TLS 握手)
```

规范定义的相关回复码包括：**220** 表示准备开始 TLS；**454** 表示因临时原因 TLS 不可用；**530** 表示必须先发出 STARTTLS 命令。规范说明，客户端收到 454 时需要自行决定后续动作——若 TLS 是为了加密而协商，客户端可以据此决定是否继续。

另一条关键规定是**协议状态复位**：TLS 握手完成后，SMTP 协议被重置到初始状态，即服务端刚发出 220 服务就绪问候之后的状态。服务端**必须**丢弃此前从客户端获得的任何信息，客户端**必须**丢弃此前从服务端获得的任何信息（例如扩展列表）。因此客户端需要在握手后重新发起 EHLO。

**降级为什么可能：规范自己写明了这一点**

RFC 3207 §6 安全性考虑中有一句话直指要害：**在 TLS 握手开始之前，任何协议交互都是在明文中进行的，可能被主动攻击者修改。**规范正是基于这一事实，要求客户端与服务端在握手完成后必须丢弃握手之前获得的全部信息。

这条规定保护的是「握手后的会话不受握手前信息污染」，但它**无法保护握手本身是否发生**。攻击面因此很清楚：

* **删除通告。**处于路径上的攻击者把 EHLO 响应中的 STARTTLS 那一行改掉或删掉。客户端看到对方「不支持 TLS」，于是以明文继续。**整个过程对双方都是静默的**——发送方日志里只会记录一次成功的明文投递。
* **伪造错误应答。**攻击者拦截 STARTTLS 命令并返回 454，客户端按「临时不可用」处理，多数机会性配置会退回明文。
* **破坏握手。**让 TLS 握手失败，诱使客户端在重试时降级。

根本原因在于：**机会性 TLS 的判定依据来自明文信道本身，而明文信道的内容不可信。**这不是实现缺陷，而是机制的固有边界——RFC 3207 定义的是「如何升级」，没有也无法定义「如何确保必须升级」。

规范还指出另一层限制：**除非投递链上的每一跳（包括向第一台 SMTP 服务器的提交）都经过认证，否则 STARTTLS 不适合用于认证邮件的作者。**传输层加密与内容来源认证是两件事。

**解决方向：把「必须加密」变成可验证的策略**

既然明文信道不可信，就必须从**信道之外**获得关于对方 TLS 能力的可信信息。这正是后续几份规范的设计思路：

* **MTA-STS（RFC 8461）**：域名通过 DNS 与 HTTPS 发布策略，声明本域的邮件服务器支持 TLS 以及期望的强制程度。发送方缓存该策略后，**即使某次会话中没看到 STARTTLS 通告，也知道这不正常**，从而拒绝以明文投递。它把判定依据从「这次会话里看到了什么」转移到「此前通过独立信道获取的策略」。
* **DANE for SMTP（RFC 7672 / RFC 6698）**：通过 DNSSEC 保护的 TLSA 记录发布服务器证书关联信息。发送方据此既能确认对方必须使用 TLS，也能验证证书。**它依赖 DNSSEC 提供的完整性保证**，与 MTA-STS 走的是不同的信任路径。
* **TLS 报告（RFC 8460）**：让接收方域获得关于其他方与自己建立 TLS 连接时成败情况的聚合报告。**这是把降级从「不可见」变成「可观测」的关键一环**——没有它，即使部署了策略也难以知道实际执行情况。
* **提交与访问路径（RFC 8314）**：对用户提交与邮箱访问路径，规范主张使用 TLS 而非明文。**用户提交这一跳往往是整条链路上最薄弱也最容易被忽略的环节。**
* **TLS 本身的配置（RFC 9325）**：BCP 195 给出了 TLS 与 DTLS 安全使用的建议，涵盖版本与算法选择。**「用上了 TLS」与「用对了 TLS」是两回事。**

**检测与排错方法**

1. **直接观测通告是否存在。**用 `openssl s_client -starttls smtp -connect host:25` 或先手工 EHLO 观察响应，确认对端是否通告 STARTTLS。**从不同网络位置各测一次**——若结果不一致，说明某条路径上存在改写。
2. **比对多个观测点。**降级攻击通常发生在特定网络路径上。从多个出口、多个网络环境测同一目标，是发现路径上改写的最直接方法。
3. **把加密状态记进日志并做成指标。**每次投递都应记录：是否协商了 TLS、协议版本、算法套件、证书验证结果。**只记「投递成功」是不够的**，明文投递同样是成功投递。
4. **对明文投递比例设告警。**与某个重要对端之间的加密比例突然下降，是降级的直接信号。**这个指标必须按对端维度看，全局平均值会把局部问题稀释掉。**
5. **启用 TLS 报告并真正去读。**报告能揭示其他发送方与自己建连时的失败情况，这些是从自身日志里看不到的视角。
6. **核对 454 的真实性。**频繁收到 454 时，应当分辨是对端确实临时不可用，还是有人在伪造这个应答。**对同一对端在不同时间、不同路径上复测，是最简单的鉴别方法。**
7. **注意握手后必须重发 EHLO。**排错时若发现「TLS 建立成功但后续命令被拒」，检查客户端是否遗漏了握手后的 EHLO，或是否错误地复用了握手前获得的扩展列表——规范要求这些信息必须被丢弃。

**部署建议与取舍**

* **先观测，再强制。**直接对所有对端强制 TLS 会造成投递失败。合理顺序是：先记录并观测各对端的加密情况，识别出不支持 TLS 的对端，评估业务影响，再逐步收紧。
* **对重要对端单独设强制策略。**与关键业务伙伴、金融机构、监管方之间的邮件，值得单独配置强制加密与证书验证，而不是依赖机会性协商。
* **MTA-STS 从测试模式开始。**该规范提供了非强制的测试模式，可在不影响投递的前提下先收集数据。**跳过这一步直接强制，是最常见的自伤方式。**
* **发布策略的同时也要消费策略。**只对外发布而自己不校验他人策略，只保护了别人发给你的邮件，没保护你发给别人的。
* **不要把传输加密当作端到端加密。**STARTTLS 保护的是相邻两跳之间的链路。邮件在每一跳都会解密并以明文形式存在于该服务器上。**内容的端到端保护需要 S/MIME 或 OpenPGP 这类报文层机制**，与传输层加密解决的是不同问题。
* **覆盖提交这一跳。**用户客户端到提交服务器的这一跳同样会被降级攻击，且这一跳通常携带用户凭据。按 RFC 8314 的方向处理，不要只顾服务器之间的链路。

参考：RFC 3207《SMTP Service Extension for Secure SMTP over Transport Layer Security》§4、§5、§6 Security Considerations，P. Hoffman，2002 年 2 月，Standards Track，DOI 10.17487/RFC3207，https://www.rfc-editor.org/rfc/rfc3207.html ；RFC 8461《SMTP MTA Strict Transport Security (MTA-STS)》，D. Margolis 等，2018 年 9 月，https://www.rfc-editor.org/rfc/rfc8461.html ；RFC 8460《SMTP TLS Reporting》，D. Margolis 等，2018 年 9 月，https://www.rfc-editor.org/rfc/rfc8460.html ；RFC 7672《SMTP Security via Opportunistic DNS-Based Authentication of Named Entities (DANE) Transport Layer Security (TLS)》，V. Dukhovni、W. Hardaker，2015 年 10 月，https://www.rfc-editor.org/rfc/rfc7672.html ；RFC 6698《The DNS-Based Authentication of Named Entities (DANE) Transport Layer Security (TLS) Protocol: TLSA》，P. Hoffman、J. Schlyter，2012 年 8 月，https://www.rfc-editor.org/rfc/rfc6698.html ；RFC 8314《Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access》，K. Moore、C. Newman，2018 年 1 月，https://www.rfc-editor.org/rfc/rfc8314.html ；RFC 9325《Recommendations for Secure Use of Transport Layer Security (TLS) and Datagram Transport Layer Security (DTLS)》，Y. Sheffer 等，2022 年 11 月，BCP 195，https://www.rfc-editor.org/rfc/rfc9325.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc3207-starttls-downgrade-stripping-detection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
