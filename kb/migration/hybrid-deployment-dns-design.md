---
title: "混合部署 DNS 设计：MX 权重策略与子域隔离"
source: "https://ztpop.net/kb/hybrid-deployment-dns-design.html"
license: CC-BY 4.0
---

# 混合部署 DNS 设计：MX 权重策略与子域隔离

## 概述

混合邮件部署——部分用户在本地邮件服务器、部分用户在云端——需要精心设计的 DNS 架构来路由邮件流量并维护认证链的完整性。DNS 层面的决策包括：MX 记录的优先级和权重如何将入站邮件分流到不同环境，哪些子域托管在哪个系统上，SPF/DKIM/DMARC 的签名策略如何覆盖所有出站路径。一个设计良好的混合 DNS 方案应让外部发件方感知不到内部双环境的存在，所有认证检查无差别通过。

## MX 权重分流与子域隔离

混合部署的 MX 设计有两种主流方案：用户感知分离（不同子域使用不同的 MX）和透明分流（单一域使用等优先级 MX 轮询分发）。用户感知分离适用于环境边界清晰的组织——corp.example.com 的 MX 指向本地服务器，cloud.example.com 指向云端。透明分流适用于两个环境都能处理同一域邮件的场景——两个等优先级 MX 记录分别指向本地和云端，接收方 MTA 按 RFC 5321 随机选择目标 MX。

```
# 方案一：子域隔离
# corp.example.com.    IN  MX  10  mx-local.example.com.
# cloud.example.com.   IN  MX  10  mx-cloud.example.com.

# 方案二：等权重透明分流
# example.com.         IN  MX  10  mx-local.example.com.
# example.com.         IN  MX  10  mx-cloud.example.com.

# Postfix 接收不属于本节点的邮件时中继到另一环境
# /etc/postfix/transport:
# example.com  smtp:[mx-cloud.example.com]

# 验证 DNS 配置
dig +short MX example.com
dig +short TXT example.com | grep spf
dig +short TXT selector1._domainkey.example.com
```

## SPF/DKIM/DMARC 双环境签名

混合环境的电子邮件认证需要覆盖所有可能的出站路径。SPF 记录通过 include 机制将本地和云端的出站 IP 范围合并到同一条记录中。DKIM 签名需要使用不同的 selector 区分两个环境——本地环境使用 selector1，云端使用 selector2——避免签名密钥冲突。DMARC 记录使用 rua 邮箱接收来自两个环境的聚合报告，集中分析认证通过率。

```
# SPF 双环境合并
# example.com.  TXT "v=spf1 ip4:192.0.2.0/24 include:spf.cloud.example.com -all"

# DKIM 双 selector 策略
# selector1._domainkey.example.com  TXT  本地环境的 DKIM 公钥
# selector2._domainkey.example.com  TXT  云端环境的 DKIM 公钥

# Postfix 中配置 DKIM 签名
# /etc/opendkim.conf
Domain    example.com
Selector  selector1
KeyFile   /etc/opendkim/keys/selector1.private

# 验证双环境 DKIM
opendkim-testkey -d example.com -s selector1 -vvv
dig TXT selector1._domainkey.example.com +short

# DMARC 聚合报告
# _dmarc.example.com.  TXT "v=DMARC1; p=reject; rua=mailto:dmarc@example.com; pct=100"
```

## 踩坑与排错

等权重 MX 的轮询并非真正的负载均衡——部分发件方 MTA 总是选择列出的第一条 MX，需在 MX 前放置四层负载均衡器实现真正的流量分发。子域隔离方案需考虑跨域邮件路由——corp 子域用户发给 cloud 子域用户的邮件需配置内部中继路径。DKIM 签名 selector 不同导致 DMARC 验证方需要验证两条 DKIM 记录，在某些严格实施 DMARC 的接收方可能导致轻微的性能开销。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/hybrid-deployment-dns-design.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
