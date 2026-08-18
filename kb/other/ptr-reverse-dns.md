---
title: "RFC 1912 / RFC 5321 · 邮件服务器必备配置"
source: "https://ztpop.net/kb/ptr-reverse-dns.html"
license: CC-BY 4.0
---

# RFC 1912 / RFC 5321 · 邮件服务器必备配置

## 摘要

PTR（Pointer）记录是 DNS 反向解析的核心机制，将 IP 地址映射回域名。在邮件投递中，PTR 记录是 SMTP 会话建立阶段接收方检查的第一道防线——缺少 PTR 或正反向不一致的 IP 会被大型邮件服务商直接拒绝连接，邮件甚至不会进入内容扫描环节。本文阐述 PTR 的工作原理、对邮件投递的具体影响、各主流邮箱的拒绝策略，以及正确的配置方法。

## 1. PTR 记录的基本原理

### 1.1 正向解析 vs 反向解析

* **正向解析（A/AAAA 记录）**
  ：域名 → IP 地址。由域名持有者在域名注册商的 DNS 面板中配置。
* **反向解析（PTR 记录）**
  ：IP 地址 → 域名。由 IP 地址的持有者（ISP 或云服务商）在 IP 管理面板中配置。

核心不对称性：域名的 A 记录在你的控制之下，但 IP 的 PTR 记录在分配 IP 给你的 ISP 或云服务商的控制之下。

### 1.2 DNS 反向查询的层次结构

反向查询使用
`.arpa`
顶级域下的
`in-addr.arpa`
子域。IP
`203.0.113.25`
的反向查询对应域名为
`25.113.0.203.in-addr.arpa`
。DNS 服务器在该链路上查找 PTR 记录。

```
# 反向查询 IP 的 PTR 记录
dig -x 203.0.113.25

# 等同于
dig PTR 25.113.0.203.in-addr.arpa

# Windows
nslookup 203.0.113.25
```

## 2. PTR 在 SMTP 中的作用

### 2.1 SMTP 连接阶段检查（RFC 5321 §4.1.4）

当发信 MTA 向接收方 MTA 发起连接时，SMTP 会话的第一步是发送
`EHLO`
命令声明自己的身份。接收方 MTA 随后读取 TCP 连接的对端 IP，执行 PTR 反向查询。验证链路为：

1. 发信 IP → PTR 查询 → 返回域名
   `mail.example.com`
2. `mail.example.com`
   → A 记录查询 → 返回 IP 地址
3. 检查第 2 步返回的 IP 是否等于第 1 步的源 IP（
   **正向/反向解析闭环**
   ）
4. 检查
   `mail.example.com`
   是否与 HELO/EHLO 声明的主机名一致

四步验证全部通过，SMTP 会话才被允许继续进行。任何一步失败都可能导致连接被拒绝。

### 2.2 各主流邮箱的 PTR 拒绝策略

2.2 各主流邮箱的 PTR 拒绝策略

| 邮箱服务商 | 无 PTR 时的行为 | 返回代码 |
| Outlook.com / Hotmail.com / Live.com | 直接拒绝连接 | `554 No SMTP service` |
| AOL / Yahoo Mail | 直接拒绝连接 | `554 5.7.1 Bad DNS PTR resource record` |
| mail.com / GMX | 直接拒绝连接 | `554 No SMTP service` |
| Gmail | 降级但可能放行 | 标记为可疑 | 部分情况下 `550 5.7.25` |
| 国内主流邮箱（sina.com） | 临时拒绝 | `450 4.7.1 Client host rejected` |

国内如国内主流企业邮箱（QQ/Exmail）和国内主流邮箱服务商对 PTR 的严格度经历逐步提升过程。历史数据显示部分国内邮箱在 2020 年前对 PTR 检查宽松，但自 2023 年以来 PTRA 缺失引发的投递失败报告显著增多。

## 3. 配置方法

### 3.1 主流云服务商操作路径

* **阿里云 ECS**
  ：ECS 控制台 → 实例 → 左侧菜单"网络与安全" → 弹性公网 IP → 选择 IP → 设置反向解析
* **腾讯云 CVM**
  ：云服务器控制台 → 公网 IP → 更多 → 设置反向解析
* **华为云 ECS**
  ：弹性公网 IP → 修改反向解析
* **自建机房**
  ：联系 IP 线路提供商（中国电信/联通/移动）通过工单系统申请 PTR 设置

### 3.2 PTR 记录值选择

PTR 记录值应为邮件服务器的 HELO/EHLO 主机名，例如：

```
IP: 203.0.113.25
PTR: mail.example.com
A记录: mail.example.com → 203.0.113.25 (正向解析闭环)
```

**常见错误**
：将 PTR 指向根域
`example.com`
而非邮件服务器主机名。虽然这不会导致正向/反向闭环被破坏，但会增加 HELO/EHLO 一致性检查失败的概率。

### 3.3 验证命令

```
# 验证 PTR 记录
dig -x 203.0.113.25

# 验证正向解析闭环
dig A mail.example.com

# 验证一致性检查
# PTR返回的域名正向解析的IP必须等于源IP
```

## 4. 常见问题

### 4.1 动态 IP 如何处理 PTR

动态 IP（PPP/PPPoE/住宅宽带）通常属于 PBL（Policy Block List）范围。如果通过动态 IP 直发邮件，即使配置了 PTR，该 IP 段在 Spamhaus PBL 中的策略性收录仍会导致大部分邮箱拒收。解决方案是使用中继 MTA（relayhost）通过有固定 IP 服务器的 SMTP 转发。

### 4.2 云服务商的默认 PTR

云服务商的公网 IP 通常预置了默认 PTR 记录，形如
`ecs-203-0-113-25.compute.aliyuncs.com`
，这不符合邮件投递要求。必须修改为你的域下的合法主机名，并确保正向解析匹配。

### 4.3 多个 IP 的场景

如果邮件服务器通过多个公网 IP 出站，每个 IP 都需要单独的 PTR 记录。最佳实践是为每个出站 IP 分配独立的主机名（如
`mx1.example.com`
、
`mx2.example.com`
），并对应配置 SPF
`ip4`
授权。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ptr-reverse-dns.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
