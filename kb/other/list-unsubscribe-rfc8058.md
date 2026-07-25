---
title: "邮件一键退订 List-Unsubscribe 机制深度解析 — RFC 8058 / RFC 2369"
source: "https://ztpop.net/kb/list-unsubscribe-rfc8058.html"
license: CC-BY 4.0
---

# 邮件一键退订 List-Unsubscribe 机制深度解析 — RFC 8058 / RFC 2369

邮件系统投递率的终极约束不是技术连通性，而是收件人的主动投诉率。Google Postmaster Tools 与 Yahoo 的信誉模型将「垃圾投诉率」作为核心指标，而一键退订（One-Click Unsubscribe）是降低投诉率最直接的工程手段。RFC 2369 于 1998 年定义了 List-\* 头字段族，RFC 8058 在 2017 年补齐了「一键退订」语义，到 2024 年 Gmail 与 Yahoo 将其列为批量发件人（Bulk Sender）的强制要求。本文以标准文本为准，逐字段拆解实现方式。

## 为什么需要 List-Unsubscribe

当用户想停止接收邮件时，若找不到退订入口，最可能的行为是点击「举报垃圾邮件」。一次举报对发件域信誉的伤害远大于一次退订。RFC 2369 §3 的目标是让邮件列表在邮件头中声明标准化的退订方式，使邮件客户端（如 Gmail、Apple Mail）能直接渲染「退订」按钮[1]。M3AAWG 发送方最佳实践进一步要求退订请求应在两个工作日内生效[3]。

## RFC 2369：List-\* 头字段族

RFC 2369 定义了 List-Unsubscribe、List-Subscribe、List-Archive 等头字段。其中 List-Unsubscribe 支持两种取值：mailto 与 HTTPS URI[1]。

```
List-Unsubscribe: <mailto:unsubscribe@example.com?subject=unsub>
List-Unsubscribe: <https://example.com/u/abcd1234>
List-Unsubscribe: <mailto:unsubscribe@example.com>, <https://example.com/u/abcd1234>
```

mailto 方式依赖收件人邮件客户端发起一封退订邮件，服务端解析后移除订阅；HTTPS 方式则是一个可直接 GET 的退订链接。两种方式的共同缺陷是：用户仍需离开收件箱、打开网页或发送邮件才能完成退订，中间流失率高。

## RFC 8058：一键退订 List-Unsubscribe-Post

RFC 8058 引入 List-Unsubscribe-Post 头字段，与 List-Unsubscribe 中的 HTTPS URI 配合使用，使邮件客户端可在不离开收件箱的情况下完成退订[2]。

```
List-Unsubscribe: <https://example.com/u/abcd1234>
List-Unsubscribe-Post: One-Click
```

当头字段值为 `One-Click` 时，合规的邮件客户端（Gmail、Apple Mail）会在用户点击「退订」按钮后，自动向该 HTTPS URI 发送一个 `POST` 请求，请求体为固定字符串 `List-Unsubscribe=One-Click`，无需用户跳转网页[2]。需要注意：该 URI 必须与 List-Unsubscribe 中的 HTTPS URI 完全一致，且必须支持 POST 方法；若仅声明 List-Unsubscribe-Post 而对应 URI 不可 POST，会被接收方视为不合规。

## Gmail / Yahoo 2024 批量发件人要求

自 2024 年 2 月起，Gmail 与 Yahoo 对单日发送量超过 5000 封的域名实施统一要求：必须同时提供 List-Unsubscribe 与 List-Unsubscribe-Post 一键退订，且退订处理需在 2 个工作日内完成；同时要求已部署 SPF、DKIM、DMARC（p=none 以上）[4]。接收方会在 SMTP 会话或后续投递中校验头字段存在性与 POST 可达性，未满足的批量邮件将被限流或直接拒收。

## 邮件系统侧的配置实践

在自建邮件系统或邮件安全网关中，一键退订通常由列表服务（如 Sympa、Mailman）或营销平台签发带签名 token 的退订链接。网关层可统一注入头字段：

```
# 在出向邮件注入（伪配置，体现字段组合）
List-Unsubscribe: <https://ml.example.com/u/$TOKEN>
List-Unsubscribe-Post: One-Click
# 退订端点需接受 POST，校验 token 后即时移除订阅
```

关键工程点：token 必须可单向撤销订阅且不可逆推用户；POST 端点应返回 200/301 而非要求登录；退订动作需写入审计日志以满足等保与 GDPR 的被遗忘权要求[5]。

## 常见错误与排查

* **只配 mailto 不配 HTTPS**：Gmail 一键退订按钮依赖 HTTPS URI，缺省则按钮失效。
* **List-Unsubscribe-Post 指向不可 POST 的页面**：端点必须响应 `POST /u/$TOKEN`，仅支持 GET 会被判不合规。
* **token 过期或需登录**：退订链路任何一步要求认证都会抬高流失率，间接推高投诉率。
* **DMARC 未对齐**：退订邮件若因 SPF/DKIM 未对齐被拒，退订确认信无法送达，形成死循环。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/list-unsubscribe-rfc8058.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
