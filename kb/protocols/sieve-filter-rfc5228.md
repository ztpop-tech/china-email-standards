---
title: "Sieve 邮件过滤语言深度解析 — RFC 5228：服务端过滤、Vacation 与 ManageSieve"
source: "https://ztpop.net/kb/sieve-filter-rfc5228.html"
license: CC-BY 4.0
---

# Sieve 邮件过滤语言深度解析 — RFC 5228：服务端过滤、Vacation 与 ManageSieve

在邮件服务器上，过滤逻辑放在哪一层直接决定体验与一致性。客户端过滤（如 Outlook 规则）只在特定客户端在线时生效，换设备或网页端收信就失效；服务端过滤在邮件投递（final delivery）时由 MTA/LDA 执行，对所有客户端统一生效。RFC 5228 定义的 Sieve 正是邮件系统领域事实标准的服务端过滤语言[1]。本文以标准文本为准拆解其模型与部署。

## 为什么需要服务端过滤

邮件系统面临的核心矛盾是：用户希望「按规则分拣邮件」，但收信客户端多样（IMAP、Web、移动端）。把规则放在客户端，规则无法跨客户端共享；放在服务端，则无论用户用何种客户端，邮件落库前已被分拣。Sieve 的设计约束是「安全且可中断」：脚本不能执行任意代码、不能发起网络请求、不能陷入死循环[1]。

## RFC 5228 Sieve 语言模型

Sieve 脚本由一系列「条件→动作」块组成。每条命令要么是 test（判断），要么是 action（执行）。基础 action 包括 `keep`、`fileinto`、`redirect`、`discard`、`reject`[1]。

```
require ["fileinto", "vacation"];
if header :contains "from" "boss@example.com" {
    fileinto "INBOX/Important";
}
if address :domain :is "to" "list.example.com" {
    fileinto "INBOX/Lists";
}
if not exists "Date" {
    discard;
}
```

脚本从上到下执行，命中 `fileinto` 后将邮件归入指定邮箱；未显式 `keep`/`fileinto` 且未 `discard` 的邮件默认落入收件箱。注意 Sieve 中「隐式 keep」规则：若脚本未产生任何显式动作，邮件仍保留[1]。

## 常用扩展：Vacation 与 Subaddress

`vacation` 扩展实现自动回复（区别于 MTA 级 vacation），仅对首封邮件回复一次并带冷却期；`subaddress` 支持 `user+tag@domain` 的地址标签匹配[2]。

```
require ["vacation"];
vacation :days 7 :subject "Out of office" "我将于下周返岗，紧急事务请致电 021-xxxx。";
```

## ManageSieve (RFC 5804) 管理协议

用户如何上传/编辑脚本？RFC 5804 定义 ManageSieve，一个独立于邮件协议的管理通道（通常监听 4190 端口），提供 `PUTSCRIPT`、`SETACTIVE`、`LISTSCRIPTS`、`GETSCRIPT` 等命令，配合 SASL 认证[3]。

```
# ManageSieve 交互（示意）
C: PUTSCRIPT "default" {长度}
S: OK
C: SETACTIVE "default"
S: OK
```

## 在 Dovecot / Postfix 中部署

Dovecot 通过 Pigeonhole 插件提供 Sieve 与 ManageSieve。Postfix 将最终投递交给 Dovecot LMTP，由 LMTP 调用 Sieve：

```
# dovecot.conf 片段
protocol lmtp {
  mail_plugins = $mail_plugins sieve
}
service managesieve-login { inet_listener sieve { port = 4190 } }
# 用户脚本目录：~/sieve/ 下 default.sieve 为激活脚本
```

## 安全约束

* **无副作用**：Sieve 不能执行 shell、不能访问文件系统任意路径，避免成为邮件系统提权入口。
* **循环防护**：`redirect` 可能形成转发环，服务端需限制跳数。
* **权限边界**：ManageSieve 必须走 SASL 认证，脚本归属严格绑定邮箱账号。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/sieve-filter-rfc5228.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
