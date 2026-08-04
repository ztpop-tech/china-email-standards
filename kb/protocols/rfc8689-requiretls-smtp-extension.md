---
title: "RFC 8689 REQUIRETLS 如何把机会式 STARTTLS 变成强制加密投递？"
source: "https://ztpop.net/kb/rfc8689-requiretls-smtp-extension.html"
license: CC-BY 4.0
---

# RFC 8689 REQUIRETLS 如何把机会式 STARTTLS 变成强制加密投递？

1
RFC 8689 REQUIRETLS 如何把机会式 STARTTLS 变成强制加密投递？
▼

**要解决的问题**

摘要部分点明痛点：**STARTTLS 的机会式（opportunistic）本质使其安全价值打折**——默认情况下「把邮件投出去」的优先级高于「安全地投出去」，一旦对端不支持或被降级，邮件照样以明文发出。RFC 8689 因此定义了 SMTP 服务扩展 **REQUIRETLS** 与消息头字段 **TLS-Required**，把「无 TLS 则不投递」变成可声明的硬要求。

**扩展的形式定义（§2）**

* 扩展名为 “Require TLS”，**EHLO 关键字为 `REQUIRETLS`**。
* **不定义任何新的 SMTP 动词**；只为 `MAIL FROM` 命令新增一个**无取值**的可选参数 `REQUIRETLS`。
* 由于可能追加一个空格加关键字，`MAIL FROM` 命令行最大长度**增加 11 个八位组**。
* 新增一个 SMTP 状态码，用于表达「客户端向不支持 REQUIRETLS 的服务器发送数据」这一错误。
* 该扩展对**中继（RFC 5321）、提交（RFC 6409）与 LMTP（RFC 2033）**均有效。

**使用 REQUIRETLS 的四项前置安全条件（§2）**

该选项**只能在满足 REQUIRETLS 安全要求的 SMTP 会话中**使用，四条缺一不可：

1. 会话本身 MUST 采用 TLS 传输。
2. 若目标 SMTP 服务器是通过 **MX 记录**查得的，其名称 **MUST 经收件域 MX 记录上的 DNSSEC 签名验证**，或 MX 主机名 **MUST 由 MTA-STS 策略（RFC 8461 §4.1）校验通过**。
3. 服务器出示的证书 MUST 经由客户端信任的信任链验证成功，或 MUST 依 DANE（RFC 7672）验证成功；信任根的选择由 SMTP 客户端自行决定。
4. STARTTLS 协商完成后，服务器 **MUST 在随后的 EHLO 响应中通告自身支持 REQUIRETLS**。

**TLS-Required 头字段：反向的「请忽略策略」（§3）**

本规范还定义了一个新的消息头字段 `TLS-Required`（RFC 5322 意义上的头字段），语义与 REQUIRETLS **相反**：它用于发起方**请求收件方的 TLS 策略（含 MTA-STS 与 DANE）被忽略**。典型用途是**向对方报告其邮件服务器配置错误**——例如对方 TLS 证书已过期，导致按策略根本无法投递告知邮件。该头字段有一个必需参数 `No`，表示 SMTP 客户端 SHOULD 尝试投递而不顾 TLS 策略。

**接收与发送方的处理要求（§4.1、§4.2.1）**

**接收侧（§4.1）**：收到带 `REQUIRETLS` 参数的 `MAIL FROM` 时，服务器 MUST 将该邮件标记为需 REQUIRETLS 处理。若 `MAIL FROM` 未带该参数、但邮件头含 `TLS-Required`，则 MUST 按该头字段所述选项标记。**两者同时出现时，以 MAIL FROM 参数为准，`TLS-Required` 头 MUST 被忽略**（但 MAY 在后续中继中保留）。若邮件被本地别名展开投向多个地址，**所有副本 MUST 以相同方式标记**。

**发送侧（§4.2.1）**：对标记为需 TLS 且 `MAIL FROM` 回退路径非空（空回退路径代表退信）的邮件，客户端 MUST 依次完成：按 RFC 5321 §5.1 查找目标服务器；若经 MX 查得且无有效 DNSSEC 签名，则 MUST 另行用 MTA-STS 校验服务器名；以 EHLO 开启会话；建立受 TLS 保护的会话并按 RFC 6125 或 RFC 7672 验证证书，**MX 记录中的主机名（无 MX 而直接用 A 记录时则为域名）MUST 匹配证书的 DNS-ID 或 CN-ID**；确认 TLS 建立后的 EHLO 响应通告了 REQUIRETLS 能力。

**失败处理与退信状态码（§4.2.1、§5）**

上述任一步骤失败，客户端 MUST 向服务器发 `QUIT`，并对收件域 MX 列表中的**每一台主机**重复第 2–5 步，尝试寻找满足发送方安全要求的投递路径。**若 MX 主机全部试完仍不满足，客户端 MUST NOT 把邮件投给该域**，并 MUST 按 RFC 5321 §3.6 向失败邮件的反向路径发送投递失败通知。推荐使用的状态码为：

* **`5.7.30` REQUIRETLS support required**：服务器不支持 REQUIRETLS。
* **`5.7.10` Encryption needed**：无法建立受 TLS 保护的 SMTP 会话。

客户端在发 `QUIT` 前，*MAY* 先把手上其他不需保护的邮件发给该服务器。

参考：RFC 8689《SMTP Require TLS Option》，https://www.rfc-editor.org/rfc/rfc8689 —— 章节 2 / 3 / 4.1 / 4.2.1 / 4.2.2 / 5

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8689-requiretls-smtp-extension.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
