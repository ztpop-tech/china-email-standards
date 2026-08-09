---
title: "国产化改造之后，MTA-STS 和 TLS-RPT 还有必要部署吗？"
source: "https://ztpop.net/kb/xc-mta-sts-tlsrpt-in-xinchuang.html"
license: CC-BY 4.0
---

# 国产化改造之后，MTA-STS 和 TLS-RPT 还有必要部署吗？

**先分清层次：算法是一回事，策略是另一回事**

一个常见误解是「上了国密就不用管 MTA-STS 了」。两者处在不同层次：

* **国密改造**解决的是**用什么算法加密**。
* **RFC 8461 SMTP MTA Strict Transport Security (MTA-STS)** 解决的是**对端能否被强制加密、能否防止降级**——它让发送方知道「这个域承诺支持 TLS，若协商不成就不要投递」。
* **RFC 8460 SMTP TLS Reporting** 解决的是**加密失败能否被发现**——它让你收到对端视角的失败报告。

**结论：算法再强，若能被剥离成明文，防护等于零。**策略层与算法层必须同时具备。

**MTA-STS 的三个组成部分：缺一不可**

部署由三部分构成，任何一部分缺失或不一致都会导致策略不生效：

1. **DNS TXT 记录**：位于 `_mta-sts.<域名>`，内容形如 `v=STSv1; id=<策略版本标识>`。**id 用于通知对端策略已更新，每次改策略必须同步改 id**，否则对端会继续使用缓存的旧策略。
2. **策略文件**：通过 HTTPS 发布于 `https://mta-sts.<域名>/.well-known/mta-sts.txt`，包含版本、模式、允许的 MX 主机名、缓存有效期等字段。
3. **承载策略文件的 HTTPS 服务**：该站点的证书必须有效。**这是最容易翻车的一环**——策略文件本身的可信度完全依赖这张证书，证书过期会使整个策略静默失效。

策略中列出的 MX 主机名必须与实际 MX 记录一致，且这些主机的证书需满足 RFC 7817 Updated TLS Server Identity Check Procedure for Email-Related Protocols 的身份校验规程。

**TLS-RPT：先上报告，再谈强制**

RFC 8460 SMTP TLS Reporting 定义的报告机制通过 `_smtp._tls.<域名>` 处的 TXT 记录发布接收地址，内容形如 `v=TLSRPTv1; rua=mailto:<接收地址>`。

**为什么必须先上它：**MTA-STS 的强制模式一旦开启，协商失败的邮件会被拒收。若事先不知道有哪些对端会失败、失败原因是什么，强制就是在盲开。**TLS-RPT 提供的正是这份「开启前必须看到」的数据。**

**可操作建议：**报告接收地址应指向可自动解析归档的邮箱，并把报告数据纳入定期查看流程；报告本身也应留存，它是加密有效性的直接证据，对等保与密评都有用。

**testing 到 enforce 的切换判定条件**

策略文件的 mode 字段支持 `none`、`testing`、`enforce` 三种取值。切换必须有数据依据：

1. **先置 testing**：对端会按策略校验但不因失败而拒投，同时会在 TLS 报告中反馈失败。
2. **观察一个完整业务周期**，逐条排查报告中的失败项。常见原因：MX 列表与策略不一致、证书主机名不匹配、中间证书缺失、部分 MX 未配置 TLS。
3. **失败项清零后再切 enforce**。判定条件是「连续一个业务周期内无新增失败」，而不是「大部分成功」。
4. 切换后继续监控报告，出现新增失败立即处理。

**反面做法：**直接上 enforce。后果是部分合法邮件被对端拒收，而你在收到投诉之前完全不知情。

**国产化环境下的三个额外注意点**

* **策略列出的 MX 必须覆盖全部实际 MX**：改造期间常有新旧网关并存，若策略只写了新网关，经旧网关的投递会被判为不符合策略而失败。**并存期务必把两套都列入。**
* **双栈证书要与策略校验兼容**：同一 MX 同时提供国密与国际证书时，需确认对端在协商国际算法时取到的证书主机名同样正确。
* **承载策略文件的站点若做了国密改造，需保留国际算法兼容**：对端 MTA 拉取策略文件时使用的是通用 HTTPS 客户端，若该站点只支持国密，境外对端将无法取到策略，策略等同于不存在。

**验证方法与常见故障排查顺序**

部署后按此顺序自查：

1. 查询两条 TXT 记录是否可解析、格式是否正确。
2. 用干净环境访问策略文件 URL，确认可访问、证书有效、内容格式正确。
3. 比对策略中的 MX 列表与实际 MX 记录，必须完全一致。
4. 对每个 MX 主机实际握手，确认 TLS 可用、证书链完整、主机名匹配。
5. 确认 TLS 报告能正常收到并可解析。
6. 每次修改策略后确认 id 已变更。

整体邮件传输安全实践可参考 NIST SP 800-177 Rev.1 Trustworthy Email。

参考：[RFC 8461 SMTP MTA Strict Transport Security (MTA-STS)](https://www.rfc-editor.org/rfc/rfc8461.html) ｜ [RFC 8460 SMTP TLS Reporting](https://www.rfc-editor.org/rfc/rfc8460.html) ｜ [RFC 7817 Updated TLS Server Identity Check Procedure for Email-Related Protocols](https://www.rfc-editor.org/rfc/rfc7817.html) ｜ [NIST SP 800-177 Rev.1 Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/xc-mta-sts-tlsrpt-in-xinchuang.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
