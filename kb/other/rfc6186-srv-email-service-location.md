---
title: "RFC 6186 如何用 SRV 记录实现邮件服务自动发现？"
source: "https://ztpop.net/kb/rfc6186-srv-email-service-location.html"
license: CC-BY 4.0
---

# RFC 6186 如何用 SRV 记录实现邮件服务自动发现？

1
RFC 6186 如何用 SRV 记录实现邮件服务自动发现？
▼

**规范定位**

RFC 6186 的目标十分聚焦：描述如何使用 DNS 的 SRV 记录来定位邮件服务。对用户而言，理想的账户配置体验是只输入邮件地址与口令，客户端即可自动找出该域的提交服务器与收信服务器；SRV 记录正是为此提供的标准化机制。

**五个服务标签**

**邮件提交**——新增 `submission` 标签，标识一台 MSA，该标签同时涵盖使用与不使用 TLS 的连接（TLS 部分依 SMTP 的 STARTTLS 定义）：

```
_submission._tcp     SRV 0 1 587 mail.example.com.
```

**IMAP**——新增两个标签：`_imap` 标识的 IMAP 服务器可以通告 LOGINDISABLED 能力、可以要求 MUA 在认证前先执行 STARTTLS（这两个扩展对 MUA 与服务器都是强制实现，但对服务提供商并非强制使用）；`_imaps` 标识的服务器则在连接建立时直接启动 TLS：

```
_imap._tcp     SRV 0 1 143 imap.example.com.
_imaps._tcp    SRV 0 1 993 imap.example.com.
```

**POP3**——同样新增两个标签：`_pop3` 标识的服务器可要求 MUA 在认证前使用 STLS 扩展命令，`_pop3s` 标识的服务器在连接时直接启动 TLS：

```
_pop3._tcp     SRV 0 1 110 pop3.example.com.
_pop3s._tcp    SRV 0 1 995 pop3.example.com.
```

**用优先级表达站点偏好**

SRV RR 的 priority 字段允许域指明某些记录比其他记录更优先（数值越小越优先）。它通常用于在同一服务标签的记录集中做选择，但并不限于单一服务内部。许多站点同时提供 IMAP 与 POP3 两种邮件存储访问方式，却希望向用户表达其中一种更受推荐。

为此，站点**应当**同时提供 IMAP（`_imap` 与/或 `_imaps`）与 POP3（`_pop3` 与/或 `_pop3s`）两组 SRV 记录，并把「首选」服务的优先级数值设得更低。当 MUA 同时支持 IMAP 与 POP3 时，应当取回两种服务的记录并使用优先级数值最低者；若两者优先级相同，MUA 可自行选择。若在同一优先级上存在协议不同、权重不同的多条记录，客户端**必须**先选定打算使用的协议，再在该协议对应的记录集上执行 RFC 2782 的权重选择算法。

```
_imap._tcp     SRV  0 1 143 imap.example.com.
_pop3._tcp     SRV 10 1 110 pop3.example.com.
```

上例中 IMAP 优先级为 0、POP3 为 10，即向 MUA 表明：在两者皆可用时，优先使用 IMAP。此外，SRV RR 也可以用来表明某域完全不支持某项特定服务。

**与证书校验的配合**

SRV 发现必须与 TLS 身份校验联动才安全：RFC 7817 明确要求，客户端在使用 RFC 6186 的发现流程时，必须额外把用户邮件地址的域名部分作为参考标识，与服务器证书中的 SRV-ID 比对；同时对支持 RFC 6186 的邮件客户端，SRV-ID 标识类型的支持是必需的。缺少这一步，攻击者篡改 DNS 应答即可把客户端引向任意主机。托管服务商在签发证书时应据此把 `_imaps.<客户域名>` 一类 SRV-ID 纳入 subjectAltName。

参考：IETF [RFC 6186《Use of SRV Records for Locating Email Submission/Access Services》](https://www.rfc-editor.org/rfc/rfc6186.txt)（Standards Track，2011-03）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc6186-srv-email-service-location.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
