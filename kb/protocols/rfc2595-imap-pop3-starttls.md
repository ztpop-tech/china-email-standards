---
title: "RFC 2595 如何为 IMAP、POP3 定义 STARTTLS 与 STLS？"
source: "https://ztpop.net/kb/rfc2595-imap-pop3-starttls.html"
license: CC-BY 4.0
---

# RFC 2595 如何为 IMAP、POP3 定义 STARTTLS 与 STLS？

1
RFC 2595 如何为 IMAP、POP3 定义 STARTTLS 与 STLS？
▼

**规范动机**

TLS 为应用层协议提供防篡改与防窃听能力。由于 IMAP、POP 与 ACAP 普遍面临连接窃听与劫持攻击，采用这类保护十分必要。规范指出：许多站点在认证基础设施上投入巨大（例如已存储了大量口令单向函数值的数据库），因此需要一个不与用户认证紧耦合的隐私层，使站点无需新建认证体系、也不必强制所有用户改口令，即可抵御网络窃听。IETF 有强烈意愿消除在未加密通道上传输明文口令，TLS 正是与 SASL 并行的另一条可部署路径。

**IMAP STARTTLS 命令**

IMAP 支持该扩展时，会在 CAPABILITY 响应中列出 `STARTTLS` 能力。TLS 协商在服务器返回带标记的 OK 响应末尾 CRLF 之后立即开始；客户端一旦发出 STARTTLS，在看到服务器响应且 TLS 协商完成前不得再发送任何命令。STARTTLS 仅在未认证状态下有效，且即便协商中提供了客户端凭据，服务器仍保持未认证状态（此时可用 SASL EXTERNAL 机制认证，但支持 STARTTLS 的服务器并不强制支持 EXTERNAL）。

**关键安全要求**：TLS 启动后，客户端必须丢弃此前缓存的服务器能力信息，并应重新发出 CAPABILITY 命令。这是为了防范中间人在 STARTTLS 之前篡改能力列表的攻击——服务器在 TLS 之后完全可以通告不同的能力集。

**LOGINDISABLED 与明文口令控制**

IMAP 基础规范要求实现使用明文口令的 LOGIN 命令，许多站点出于安全考虑希望在未加密时禁用它。服务器可在能力响应中通告 `LOGINDISABLED`，此时对任何 LOGIN 尝试返回带标记的 NO 响应。实现 STARTTLS 的 IMAP 服务器**必须**在未加密连接上支持 LOGINDISABLED 能力；符合本规范的 IMAP 客户端在看到该能力时**不得**发出 LOGIN 命令。POP3 侧对应的是 `STLS` 命令。

基本互操作要求还包括：客户端与服务器都应提供一种「隐私运行模式」，在加密层成功启用之前拒绝认证，并在加密层被撤销时终止连接；实现 STARTTLS 的两端都必须可配置为——在没有足够强度的加密层时，拒绝一切明文登录命令与机制（含标准与非标准机制）。服务器若允许未加密明文登录，应能按全服务器与按用户两个粒度分别关闭它。

**为什么不推荐 imaps / pop3s 独立端口**

RFC 2595 第 7 节明确表示：为 SSL 单独注册的 imaps 与 pop3s 端口，其使用不被推荐，应优先使用 STARTTLS 或 STLS 命令。理由包括：独立端口会衍生独立的 URL 方案，以不恰当的方式侵入用户界面；独立端口暗示「安全 / 不安全」的二元模型，容易误导——「安全」端口可能实际使用了出口限制的弱套件，而普通端口反而可能被带安全层的 SASL 机制保护，其直接后果是防火墙管理员常被误导为放行「安全」端口却阻断标准端口；独立端口还导致客户端只实现「用 SSL / 不用 SSL」两种策略，而「可用时即用 TLS」这一理想策略在独立端口模型下十分笨拙，在 STARTTLS 下却很简单；此外端口号是有限资源，不宜开此先例。

需要注意的是，这一取向在后续标准中已有演进：RFC 8314 转而推荐邮件访问与提交采用隐式 TLS。读者应结合两份文献理解历史脉络。

参考：IETF [RFC 2595《Using TLS with IMAP, POP3 and ACAP》](https://www.rfc-editor.org/rfc/rfc2595.txt)（Standards Track，1999-06；其 2.4 节已被 RFC 7817 取代）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc2595-imap-pop3-starttls.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
