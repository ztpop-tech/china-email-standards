---
title: "邮件服务器BGP路由劫持防护与RPKI部署"
source: "https://ztpop.net/kb/bgp-rpki-mail-security.html"
license: CC-BY 4.0
---

# 邮件服务器BGP路由劫持防护与RPKI部署

## BGP 对邮件传输的影响机制

BGP（Border Gateway Protocol）是互联网的域间路由协议，核心设计基于路径矢量算法（RFC 4271），依赖 AS\_PATH 属性进行最优路径选择。BGP 在设计上缺乏对路由公告的固有验证机制——一个 AS 可以宣告它并不实际拥有的 IP 前缀，这就是 BGP 路由劫持（Route Hijack）。

邮件传输对 BGP 劫持的脆弱性体现在三个层面：

1. **MX 记录指向的 IP 被劫持**：攻击者宣告目标邮件域的 MX 记录关联 IP 前缀，导致外域 MTA 将邮件投递到攻击者控制的服务器
2. **中间路径流量截获**：攻击者发起路径劫持，在邮件传输路径中插入恶意节点，实现 STARTTLS 降级或中间人攻击
3. **BGP 泄漏导致的投递黑洞**：错误的 BGP 公告（如 Route Leak）导致邮件路由环路或投递到死节点，造成大规模投递延迟

2024 年记录的 BGP 事件超过 4,000 起（MANRS 数据），其中约 15% 涉及邮件域名的 IP 前缀。（RFC 7908 定义了 BGP 泄漏的 7 种类型）

## RPKI 与 ROA：路由起源验证

RPKI（Resource Public Key Infrastructure）提供了一种基于 X.509 PKI 的 IP 前缀验证机制。核心概念：

RPKI 核心组件

| 组件 | 作用 | 标准依据 |
| --- | --- | --- |
| ROA（Route Origin Authorization） | IP 前缀持有者对指定 AS 的授权声明 | RFC 6483 |
| CA 证书 | 区域互联网注册机构（RIR）签发的资源证书 | RFC 6484 |
| OV（Object Validation） | 将 BGP 更新与 ROA 进行比对 | RFC 6810/RFC 8210（RPKI-RTR） |
| RTR 协议 | RPKI 验证信息从缓存分发到路由器 | RFC 8210 |

RPKI 验证结果有三种：

* **Valid**：BGP 更新中的前缀-AS 组合与 ROA 匹配
* **Invalid**：前缀-AS 与 ROA 冲突（路由应被拒绝）
* **NotFound**：不存在对应的 ROA（需依赖其他验证机制）

### 邮件域名 ROA 创建流程

保护邮件域对应的 IP 前缀不被劫持，需要向所属 RIR 创建 ROA：

```
# APNIC 示例：MyISP AS 12345 授权使用 203.0.113.0/24
# 通过 MyAPNIC 面板创建 ROA
# 参数：ASN=AS12345, Prefix=203.0.113.0/24, MaxLength=24
```

```
# 验证 ROA 是否已创建
curl -s "https://rpki-validator.example.com/api/roas?prefix=203.0.113.0/24" | jq .
```

## MANRS 实践与多线 BGP 冗余

MANRS（Mutually Agreed Norms for Routing Security）提出了路由安全的基本规范：

1. **过滤**：在网络边界阻止带有明显错误 AS\_PATH 的路由
2. **反劫持**：实施 RPKI 或 IRR 验证，防止未授权前缀公告
3. **协调**：维护准确的联系信息，参与路由事件响应
4. **全局验证**：在全球范围推动 RPKI 部署

### 多线 BGP 冗余设计

对于邮件服务，多线 BGP 冗余确保单条链路故障不中断 MX 可达性：

```
# 网络拓扑示意
# ┌──────────┐    ┌──────────┐    ┌──────────┐
# │  CN2      │    │  CU 169   │    │  CMNET    │
# │  AS4808   │    │  AS4837   │    │  AS9808   │
# └────┬─────┘    └────┬─────┘    └────┬─────┘
#      └───────────────┼───────────────┘
#                      │
#              ┌───────┴───────┐
#              │  MX Server    │
#              │  203.0.113.10 │
#              └───────────────┘
```

多线 BGP 部署要点：

* 每条链路使用独立的 AS 上联或同一 AS 的多 Transit 连接
* 通过 AS\_PATH prepend 控制入站流量路径（RFC 4271 §9.1.2.2）
* MX 域名设置多条 A/AAAA 记录（RFC 5321 §5.1），配合 BGP 下一跳可达性监测
* 实施 BGP community 标签精细控制路由策略

```
# 路由策略示例 - AS_PATH prepend 控制路径选择
route-map SET-PREPEND permit 10
  set as-path prepend 64500 64500 64500
```

## RPKI 与邮件运维集成

邮件系统运维团队应将 RPKI 验证纳入日常路由监测体系：

```
# 使用 Routinator (NLnet Labs) 搭建 RPKI 验证器
docker run -d --name routinator \
  -p 3323:3323 \
  -v /data/routinator:/root/.rpki-cache \
  nlnetlabs/routinator \
  --rtr 0.0.0.0:3323

# 验证路由状态
routinator --rtr 203.0.113.0/24 --asn 12345 validate
```

```
# 集成 BGPalerter 监测 BGP 异常
# 配置文件 config.yaml
prefixes:
  - "203.0.113.0/24"
  - "198.51.100.0/24"
monitors:
  - "ris"
  - "routeviews"
alerts:
  slack_webhook: "https://hooks.slack.com/services/..."
```

## 邮件路径的端到端保护

BGP 层面的防护只是邮件安全的一层。完整的保护需要与传输层加密协同：

BGP 防护与邮件安全协议的互补关系

| 防护层次 | 威胁 | 防护手段 | 标准 |
| --- | --- | --- | --- |
| 网络层 | BGP 劫持、前缀篡改 | RPKI ROA、BGP Filter、MANRS | RFC 6483/6484 |
| 传输层 | STRIPTLS、中间人 | MTA-STS + DANE TLSA | RFC 8461/7672 |
| 应用层 | 伪造发件人 | SPF/DKIM/DMARC | RFC 7208/6376/7489 |
| 监控层 | 路径偏离 | TLS-RPT + BGP 异常检测 | RFC 8460/7908 |

### 核心要点

* BGP 路由劫持直接影响 MX 记录可达性和邮件投递路径，是邮件安全中常被忽视的底层威胁
* RPKI/ROA 提供基于 PKI 的路由起源验证，部署 ROA 是防御 BGP 劫持的第一道防线
* MANRS 规范提供了路由安全的行为准则，国内运营商正在逐步部署 RPKI 验证器
* 多线 BGP 冗余 + STRIPLS 防御（DANE/MTA-STS）构成邮件路径的完整防护
* RFC 7908、RFC 8210 是 BGP 安全和 RPKI-RTR 的核心协议参考

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bgp-rpki-mail-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
