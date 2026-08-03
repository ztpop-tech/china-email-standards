---
title: "如何防御邮件信头注入攻击？"
source: "https://ztpop.net/kb/email-header-injection-defense.html"
license: CC-BY 4.0
---

# 如何防御邮件信头注入攻击？

1
如何防御邮件信头注入攻击？
▼

**攻击原理**

当 Web 表单/接口把用户可控输入（如姓名、主题、收件人）直接拼进邮件信头，且未过滤回车换行（CRLF，`%0d%0a`）时，攻击者可注入额外信头：例如追加 `Bcc:` 把邮件密送第三方、插入第二个 `To:`、或伪造 `From:` 与 `Subject:`，甚至注入整段正文制造钓鱼。这是典型的信头注入（Header Injection）。

**输入校验**

对所有进入信头的用户数据，严格拒绝任何 、 及编码变体（如 `%0A`、）；对收件人/抄送地址按 RFC 5321/5322 做语法与数量校验，禁止地址字段出现逗号分隔的多个值未经验证；对姓名等自由文本限制字符集并转义。宁可拒绝含换行的内容，也不要尝试「清洗」后再拼回信头。

**安全构造**

优先使用经审计的邮件库（如 Python `email` 包、JavaMail、PHP `mb_send_mail` 等）而非手工拼接原始 SMTP；让库负责正确引用与编码。若必须接触底层 SMTP，确保 DATA 之前所有信头均由服务端受控生成、用户值经过 MIME 编码且绝不含 CRLF。对出站邮件统一在 MSA 层重写/规范化信头、丢弃非法行，作为纵深防御最后一道闸。

参考：OWASP「Email Header Injection」防护指南、RFC 5322《Internet Message Format》信头语法、CWE-93《CRLF 注入》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-header-injection-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
