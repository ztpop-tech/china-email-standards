---
title: "RFC 8461 MTA-STS：用 DNS 与 HTTPS 强制 SMTP 传输层加密"
source: "https://ztpop.net/kb/rfc8461-mta-sts.html"
license: CC-BY 4.0
---

# RFC 8461 MTA-STS：用 DNS 与 HTTPS 强制 SMTP 传输层加密

## 概述

SMTP 依赖 STARTTLS（RFC 3207）在会话中协商 TLS，可抵御被动流量窃听。但 STARTTLS 是"机会型"加密：攻击者只要能剥离会话中的 `250 STARTTLS` 响应，或篡改收件域的 MX 解析，就能把加密会话降级为明文，进而实施中间人拦截。RFC 8461 定义的 MTA-STS 让收件域通过 DNS + HTTPS 发布一份"期望策略"，声明发送方应当对该域强制 TLS，从而在协议层面消除降级空间。

## 为什么需要 MTA-STS

传统的 opportunistic TLS 存在两类可被主动利用的弱点：

* **响应剥离**：攻击者在 SMTP 握手阶段删除服务端返回的 STARTTLS 能力声明，发送方误以为对端不支持加密，直接明文投递。
* **MX 重定向**：攻击者篡改 DNS 解析或路由，把邮件引向自己控制的、持有效但非预期证书的服务器。

MTA-STS 不依赖 DNSSEC，而是依托 Web PKI（浏览器级证书信任链）来验证策略文件本身，使发送方能确认"这份强制 TLS 策略确实来自该域"。

## 策略发现：TXT 记录 + HTTPS 策略文件

发送方按两步发现策略：

1. 查询 `_mta-sts.<Policy Domain>` 的 TXT 记录，确认策略版本与 `id`（用于判断缓存是否过期）。
2. 通过 HTTPS GET `https://mta-sts.<Policy Domain>/.well-known/mta-sts.txt`，要求 Policy Host 提供匹配 `mta-sts` DNS-ID 的合法 X.509 证书；仅 HTTP 200 有效，不跟随 3xx 重定向，不使用 HTTP 缓存。

## 策略文件字段

| 字段 | 说明 | 约束 |
| --- | --- | --- |
| `version` | 策略版本，当前仅 `STSv1` | 必填，仅一次 |
| `mode` | `enforce` / `testing` / `none` | 必填，仅一次 |
| `max_age` | 策略缓存生命周期（秒，最大 31557600） | 必填，仅一次 |
| `mx` | 允许的 MX 主机模式（如 `mail.example.com` 或 `*.example.net`） | 可多条；`none` 模式除外 |

## 三种模式

* **enforce**：必须拒绝向未通过 MX 匹配、证书校验或不支持 STARTTLS 的主机投递；失败视为临时错误并重试。
* **testing**：不阻断投递，但若存在 TLS-RPT 实现，则上报策略应用失败，用于上线前灰度收集问题。
* **none**：声明域未启用 MTA-STS，作为干净退出的 opt-out 机制。

## 部署示例

DNS TXT 发现记录：

```
_mta-sts.example.com. IN TXT "v=STSv1; id=20260726085700Z;"
```

HTTPS 策略文件 `/.well-known/mta-sts.txt`：

```
version: STSv1
mode: enforce
mx: mail.example.com
mx: *.example.net
max_age: 604800
```

## 与 TLS-RPT（RFC 8460）协同

MTA-STS 设计上需与 TLS-RPT（RFC 8460）配合：当策略 `mode` 非 `none` 时，下列事件应作为可报告失败上报——存在有效 TXT 但 HTTPS 策略获取失败、联系到的 MX 不支持 STARTTLS 或证书未按策略验证。`testing` 模式正是为了在影响投递前，通过 TLS-RPT 收集部署问题报告。

### 相关主题

* [RFC 8460 TLS-RPT 报告机制](/kb/rfc8460-tls-rpt.html)：MTA-STS 的失败可观测性配套规范
* [DANE TLSA 在 SMTP 的部署](/kb/dane-tlsa-smtp-deployment.html)：另一种基于 DNSSEC 的传输身份校验路径
* [邮件 TLS 加密技术栈](/kb/email-tls-encryption-stack.html)：从 STARTTLS 到 MTA-STS 的演进
* [MTA-STS 记录生成器](/tools/mta-sts-generator.html)：一键生成 \_mta-sts TXT 记录与策略文件，支持 testing/enforce 模式

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8461-mta-sts.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
