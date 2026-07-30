---
title: "ARC部署与故障排除完全指南"
source: "https://ztpop.net/kb/arc-setup-guide.html"
license: CC-BY 4.0
---

# ARC部署与故障排除完全指南

## ARC协议概述

Authenticated Received Chain（ARC）协议由RFC 8617定义，旨在解决邮件转发场景中DKIM签名失效导致的DMARC误判问题。当邮件经过邮件列表、自动转发等中间环节时，原始发件域的DKIM签名可能因内容修改而失效。ARC在每次跳转时添加新的ARC签名（AS）和ARC消息签名（AMS），并最终由ARC密封签名（ARS）形成不可篡改的验证链。

ARC协议引入了三个关键的邮件头部字段：ARC-Seal（密封签名）、ARC-Message-Signature（消息签名）和ARC-Authentication-Results（认证结果）。这三个字段共同构成了一个可验证的信任链，使得最终接收方即使原始DKIM签名已失效，也能通过ARC链确认中间节点的认证结论。

ARC的设计目标并非替代DKIM或DMARC，而是在现有的身份验证体系之上提供一种转发认证机制。根据RFC 8617 §1，ARC的核心价值在于保持认证状态在消息路径上的连续性和可追溯性。

## 部署前提与条件

部署ARC之前，需要确认以下基础设施条件已就绪：

* MTA软件支持ARC：OpenDKIM ≥2.11.0、OpenDMARC ≥1.4.0、Postfix需配合milter支持
* 已部署DKIM签名：ARC依赖既有的DKIM基础设施，建议在DKIM稳定运行后再启用ARC
* DNS解析正常：ARC使用与DKIM相同的DNS选择器查询机制
* 内部邮件流拓扑清晰：确认哪些MTA是转发节点，哪些是终结点

## ARC签名部署步骤

### 选择器与密钥管理

ARC使用独立的DNS选择器（推荐命名为arc或arc2025），与DKIM选择器分开管理。密钥生成方法与DKIM一致，推荐使用rsa-sha256算法，2048位密钥长度。也可使用ed25519-sha256（RFC 8463）。密钥文件保存为PEM格式，路径示例：/etc/opendkim/keys/arc.private。

```
# 生成ARC签名私钥
opendkim-genkey -D /etc/opendkim/keys/ -d example.com -s arc2025 -b 2048
# 生成的arc2025.txt包含DNS TXT记录，需发布到DNS
```

### MTA集成（以Postfix + OpenDKIM为例）

在OpenDKIM配置文件（/etc/opendkim.conf）中启用ARC支持，关键配置项如下：

```
# /etc/opendkim.conf
Domain                  example.com
KeyFile                 /etc/opendkim/keys/arc2025.private
Selector                arc2025
Socket                  inet:8891@localhost

# ARC 配置
ArcSignMessages         yes
ArcVerifyMessages       yes
Mode                    sv
```

OpenDMARC端也需配合启用ARC验证。在/etc/opendmarc.conf中添加：

```
# /etc/opendmarc.conf
AuthservID              example.com
PctCheck                yes
RejectFailures          false

# ARC信任配置
TrustedAuthservIDs      ml.example.com,forward.example.com
EnableCoredump          false

# 启用ARC支持
ArcVerification         yes
```

## 故障排除指南

### ARC链断裂

若ARC验证失败，首先检查密封顺序。RFC 8617 §5要求ARC-Seal必须包装在原始内容之上，ARS必须在所有AS和AMS之后添加。常见的断裂原因包括：邮件在ARC签名后又被非ARC感知的MTA修改了内容，或中间MTA未正确追加ARC头部。

诊断方法：提取邮件原始内容，使用opendkim -vvV方式手动验证每个ARC阶段。

```
# 手工验证ARC链
opendkim -vvV -t < /var/spool/mail/example.eml
# 输出中应显示各个ARC阶段的验证结果
```

### DNS记录缺失

ARC的DNS查询格式为{selector}.\_domainkey.{domain}的TXT记录。常见错误包括：选择器名称不匹配（签名时使用的选择器与DNS发布的记录不对应）、TXT记录过期、或ARC记录意外地包含了dkim=签名值。ARC的DNS记录格式与DKIM不同，发布时需明确标识为arc=

```
# DNS TXT记录示例
arc2025._domainkey.example.com TXT
  "v=ARC1; h=sha256; k=rsa; "
  "p=MIGfMA0GCSqGSIb4DQEBAQUAA4GNADCBiQKBgQC..."
```

### ARC与DMARC策略冲突

DMARC接收方在评估ARC认证链时，通常遵循RFC 8617 §6.2的定义：若ARC链有效且第一个AS/AMS的认证结果显示pass，则接收方可选择信任ARC结论。但不同接收方的实现存在差异——Gmail和Microsoft 365对ARC的信任程度各不相同。建议在启用ARC的同时，保持DMARC报告监控，观察pct=1情况下ARC对认证通过率的实际影响。

## 性能考量

ARC签名的计算成本与DKIM相当，主要开销集中在RSA签名验证上。每增加一个ARC签名链，接收方的验证时间将线性增长。对于使用Ed25519算法的ARC签名，计算性能可提升约5-8倍（相对于2048位RSA）。在邮件列表场景中，建议对ARC签名长度设定上限——RFC 8617建议接收方最多处理50个ARC链节。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/arc-setup-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
