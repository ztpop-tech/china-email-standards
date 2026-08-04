---
title: "List-Unsubscribe 相关头字段（RFC 2369 与 RFC 8058）应如何正确实现？"
source: "https://ztpop.net/kb/rfc2369-list-unsubscribe-header-fields.html"
license: CC-BY 4.0
---

# List-Unsubscribe 相关头字段（RFC 2369 与 RFC 8058）应如何正确实现？

1
List-Unsubscribe 相关头字段（RFC 2369 与 RFC 8058）应如何正确实现？
▼

**RFC 2369 的六个列表头字段**

RFC 2369 的思路是用 URL 作为列表核心命令的元语法，使邮件客户端能够把列表操作呈现为界面元素，而不必让用户记忆命令。它定义了六个头字段：

* `List-Help`——获取列表使用帮助
* `List-Subscribe`——订阅
* `List-Unsubscribe`——退订
* `List-Post`——向列表投稿
* `List-Owner`——联系列表管理者
* `List-Archive`——访问归档

语法规则同样重要：字段值由一个或多个**尖括号包裹的 URL** 组成，多个 URL 以逗号分隔，并按**偏好递减**的顺序排列，客户端应优先使用靠前者。圆括号内可放置注释。URL 必须**可以被直接使用**，不得要求用户先行修改。`List-Post` 允许一个特殊值 `NO`，表示该列表不接受投稿。此外，这些字段**不应被添加到并非来自列表的邮件上**。

```
List-Unsubscribe: <https://example.com/u/9f3c1a>,
                  <mailto:unsub-9f3c1a@example.com>
List-Help: <https://example.com/list-help> (使用说明)
List-Owner: <mailto:list-owner@example.com>
```

**RFC 8058 的一键退订机制**

仅有 `List-Unsubscribe` 时，客户端点击后往往跳转到一个网页，用户还需再次确认或登录，退订体验割裂。RFC 8058 为此新增一个头字段：

```
List-Unsubscribe: <https://example.com/u/9f3c1a>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

其规则为：`List-Unsubscribe-Post` 的**唯一合法值**就是 `List-Unsubscribe=One-Click`；同时出现这两个字段时，`List-Unsubscribe` 中**必须至少包含一个 HTTPS URI**。邮件客户端执行退订时，向该 HTTPS URI 发起 **HTTP POST** 请求，内容类型为 `application/x-www-form-urlencoded`，请求体为 `List-Unsubscribe=One-Click`。

关键约束是：退订必须**一次生效**。服务端不得再返回确认页面、不得要求登录、不得要求用户在偏好中心里做选择。任何形式的二次交互都违背该规范的设计目的。

**为什么必须有对齐的 DKIM 签名**

头字段是可以被任意伪造的。若不加约束，攻击者只需构造一封带 `List-Unsubscribe-Post` 的邮件，就能诱导客户端向任意 HTTPS 端点发起 POST。RFC 8058 因此给出两条安全要求：

* **URI 应当是不透明且难以猜测的标识**。把收件人地址明文拼进退订 URL（例如 `?email=alice@example.com`）是常见但危险的做法——它等于把「批量退订任意订阅者」的能力开放给任何能构造 URL 的人，也让退订端点变成地址有效性的探测接口。
* 客户端**应当只对具备有效 DKIM 签名的邮件执行一键退订**，且该签名需要**覆盖 List-Unsubscribe 与 List-Unsubscribe-Post 这两个头字段**，其 `d=` 域需与 From 头中的域对齐。这意味着发送方在配置 DKIM 时，必须把这两个字段显式加入签名的头字段列表（`h=` 标签），否则合规客户端可能拒绝执行一键退订。这一条是实践中最容易被忽略的失效点。

**六类常见失效点**

一键退订不生效时，按下列顺序排查通常能快速定位：

1. `List-Unsubscribe` 中**只有 mailto: 而没有 HTTPS URI**——不满足 RFC 8058 前提，客户端不会显示一键退订。
2. HTTPS 端点**不接受 POST**，返回 405，或把 POST 重定向到登录页。
3. 端点启用了**CSRF 保护**，拒绝没有同源来源或令牌的 POST。一键退订的 POST 天然来自邮件客户端，不具备这些凭据，必须为该端点单独设计豁免路径与防滥用手段（依靠不可猜测的 URI 而非来源校验）。
4. **DKIM 的 h= 未覆盖**这两个头字段，或 `d=` 与 From 域不对齐。
5. 退订处理**异步且延迟过久**。用户点了退订却继续收到邮件，下一步动作往往就是点击「举报垃圾邮件」——退订失效会直接转化为投诉，损害的是发件人信誉本身。
6. 把 `List-*` 字段**加到了非列表邮件上**（例如密码重置这类事务邮件），既违反 RFC 2369 的建议，也会让用户误以为可以退订必要的事务通知。

**与服务商要求的关系**

一键退订已从「建议」变为部分服务商的**硬性要求**。Google 的官方发件人指南明确：日发送量超过 5,000 封的发件人，其营销类与订阅类邮件必须支持一键退订，并给出了需要包含的两个头字段示例；当收件人使用一键退订时，发送方会收到相应的 POST 请求。Yahoo 也在其发件人最佳实践页面提出对应要求。

需要提醒的是：关于「必须在多少小时/多少天内完成退订处理」这一时限，**Google 的该页面并未给出数字**。坊间广泛流传的具体时限说法缺乏该官方页面的出处支撑，运维上应以各服务商官方页面的当前表述为准，并在工程实现上按**尽可能即时**的目标设计，而不是对着某个传闻数字卡点。

**退订不是唯一出口**

RFC 2369 提供的 `List-Help` 与 `List-Owner` 给出了自动化之外的人工通道。同时，可正常收信并有人处理的 `abuse@` 与 `postmaster@` 角色地址依然是必需的——当自动退订因任何原因失效时，这些通道是用户在「举报垃圾邮件」之外仅剩的选择。把所有退订路径都收敛到单一 HTTPS 端点，一旦该端点故障，投诉率就会直接上升。

参考：IETF [RFC 2369《The Use of URLs as Meta-Syntax for Core Mail List Commands》](https://www.rfc-editor.org/rfc/rfc2369.txt)（Standards Track，1998-07）与 [RFC 8058《Signaling One-Click Functionality for List Email Headers》](https://www.rfc-editor.org/rfc/rfc8058.txt)（Standards Track，2017-01）；服务商要求见 Google [Email sender guidelines](https://support.google.com/a/answer/81126)、Yahoo [Sender Best Practices](https://senders.yahooinc.com/best-practices/)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc2369-list-unsubscribe-header-fields.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
