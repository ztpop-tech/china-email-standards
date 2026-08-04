---
title: "SPF 或 DKIM 的 TXT 记录太长发布失败，应该怎么正确切分？"
source: "https://ztpop.net/kb/dns-txt-character-string-chunking-spf-dkim.html"
license: CC-BY 4.0
---

# SPF 或 DKIM 的 TXT 记录太长发布失败，应该怎么正确切分？

1
SPF 或 DKIM 的 TXT 记录太长发布失败，应该怎么正确切分？
▼

**根源：DNS 的字符串是「长度字节 + 内容」，不是任意长文本**

很多人把 TXT 记录当成一个可以放任意长文本的字段，这是长记录发布失败的根源。

按 RFC 1035 §3.3 的定义，**character-string 由一个长度字节，后跟该数量的字符构成**；它被当作二进制信息处理。既然长度用**单个字节**表达，单个 character-string 能容纳的内容长度就有一个硬性上限，无法通过任何配置绕开。

而 RFC 1035 §3.3.14 定义 TXT 记录的 RDATA 为 **TXT-DATA，即一个或多个 character-string**。注意这里是**复数**——一条 TXT 记录本身就可以由多个字符串组成。

因此正确的心智模型是：**TXT 记录不是「一段长文本」，而是「一个字符串列表」**。发布长策略时要做的不是想办法突破单串长度，而是把内容切成多个串放进同一条记录。

**正确切分：多字符串，单条记录**

RFC 7208 §3.3 专门处理了单条 DNS 记录中的多字符串问题。其规则是：**若一条已发布的 SPF 记录含有多个 character-string，则这些字符串必须串接起来，串接时不插入任何空格。**

区文件中的写法是把多个带引号的串并列在同一条记录里：

```
; 正确：一条 TXT 记录，内部由多个字符串组成
example.com. IN TXT ( "v=spf1 ip4:198.51.100.0/24 "
                      "include:_spf.provider.example "
                      "-all" )
```

DKIM 的公钥记录同样如此。RFC 6376 §3.6.2.2 在讨论以 DNS TXT 记录承载公钥时说明，若一条 TXT 记录含有多个字符串，则这些字符串在使用前必须串接。RSA 公钥的 base64 编码通常较长，DKIM 记录几乎必然需要切分：

```
selector1._domainkey.example.com. IN TXT ( "v=DKIM1; k=rsa; p=MIIBIjANBg"
                                           "kqhkiG9w0BAQEFAAOCAQ8AMIIBCg"
                                           "KCAQEA...." )
```

**切分点可以落在内容的任意位置，包括词的中间**，因为串接时不插入任何字符。但为了可读与可维护，实践中通常切在语义边界上（SPF 切在机制之间、DKIM 切在 base64 的固定列宽处）。

**最常见的错误：拆成多条记录**

把长策略拆成同名的多条 TXT 记录，是这一主题下最常见也最有破坏性的错误。它与「一条记录内的多个字符串」看起来相似，语义却完全相反。

```
; 错误示范：同名两条 TXT 记录
example.com. IN TXT "v=spf1 ip4:198.51.100.0/24 "
example.com. IN TXT "include:_spf.provider.example -all"
```

为什么这是错的：按 RFC 2181 的澄清，同名同类型的多条记录构成一个 RRSet，**RRSet 内各记录之间没有定义顺序**。查询方拿到的是一个无序集合，无法知道应该把哪条接在哪条后面。

更关键的是 SPF 的选择规则。RFC 7208 §4.5 规定了记录选择过程：在查询返回的记录中挑出以版本节 `v=spf1` 开头的那些；**如果选出的记录多于一条，则检查结果为 permerror**。上面的错误示范中，第二条不以 `v=spf1` 开头，会被直接丢弃——结果是策略被静默截断，`-all` 消失，本应硬失败的邮件变成 neutral。**这是一个「配置看起来存在、实际保护已失效」的静默故障。**

反过来，如果两条记录都以 `v=spf1` 开头（例如迁移时新旧记录并存忘了删旧的），则直接 permerror，全域 SPF 校验失败。

**查询与验证方法**

1. **用 dig 看原始返回，注意引号边界。**`dig +short TXT example.com` 的输出中，**每一对引号就是一个 character-string**。同一行内有多对引号 = 一条记录多个字符串（正确）；输出为多行，每行各自成串 = 多条记录（对 SPF 而言通常是错的）。
2. **确认没有残留的旧记录。**迁移邮件服务商时最容易出现新旧 SPF 并存。上线新记录后立即用 `dig TXT` 全量核对，不要只看控制台里自己刚填的那一条。
3. **DKIM 用实际验证来确认，而不是只看记录能否解析出来。**公钥记录能被查到，不代表串接后的 base64 是完整且正确的。**切分时误吞或误增一个字符，记录照样能发布、能查询，只是所有签名都验不过。**必须实际发一封签名邮件并检查校验结果。
4. **留意托管面板的自动处理。**不同 DNS 托管服务对长 TXT 值的处理不一致：有的会自动切分，有的会截断，有的会拒绝，有的要求用户自行写引号。**无论面板显示什么，都以 `dig` 从权威服务器查到的结果为准。**
5. **注意 SPF 的查询次数限制。**RFC 7208 §4.6.4 对 DNS 查询次数有明确上限。用 include 来规避单条记录长度问题，会消耗查询次数配额；超限同样导致 permerror。**「记录太长」与「查询太多」是两个独立的约束，不能用一个去解另一个。**
6. **考虑响应包大小。**过长的 TXT 记录会增大 DNS 响应。虽然现代解析普遍支持较大响应与 TCP 回退，但在网络路径受限的环境中仍可能出现截断或超时，表现为间歇性的认证失败。**能精简策略就精简，不要一味靠切分解决。**

**运维要点小结**

* **一条记录，多个字符串——这是唯一正确的形态。**
* **串接时不插入任何字符**，因此切分点不影响语义，但要小心不要在切分时误增或误删字符。
* **永远不要用多条同名 TXT 记录来承载一份策略。**RRSet 无序，结果不可预期。
* **变更后必须实测。**SPF 看校验结果是 pass 还是 permerror，DKIM 看签名能否通过验证。**只看记录「发布成功」是不够的**，这一类故障的共同特征就是配置存在而功能失效。
* **把 SPF 与 DKIM 记录纳入配置监控。**域名转移、面板改版、批量导入都可能悄悄改变记录形态。定期比对实际解析结果与预期基线，是发现这类静默失效最有效的手段。

参考：RFC 1035《Domain names - implementation and specification》§3.3 Standard RRs、§3.3.14 TXT RDATA format，P. Mockapetris，1987 年 11 月，STD 13，https://www.rfc-editor.org/rfc/rfc1035.html ；RFC 1034《Domain names - concepts and facilities》，P. Mockapetris，1987 年 11 月，STD 13，https://www.rfc-editor.org/rfc/rfc1034.html ；RFC 7208《Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1》§3.3 Multiple Strings in a Single DNS Record、§4.5、§4.6.4，S. Kitterman，2014 年 4 月，https://www.rfc-editor.org/rfc/rfc7208.html ；RFC 6376《DomainKeys Identified Mail (DKIM) Signatures》§3.6.2.2，D. Crocker、T. Hansen、M. Kucherawy 编，2011 年 9 月，STD 76，https://www.rfc-editor.org/rfc/rfc6376.html ；RFC 2181《Clarifications to the DNS Specification》，R. Elz、R. Bush，1997 年 7 月，https://www.rfc-editor.org/rfc/rfc2181.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dns-txt-character-string-chunking-spf-dkim.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
