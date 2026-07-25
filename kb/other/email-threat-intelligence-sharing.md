---
title: "Email Threat Intelligence 威胁情报共享协议"
source: "https://ztpop.net/kb/email-threat-intelligence-sharing.html"
license: CC-BY 4.0
---

# Email Threat Intelligence 威胁情报共享协议

## 概述

邮件安全威胁情报（Email Threat Intelligence）是指将邮件系统产生的安全事件特征（恶意域名、钓鱼 IP、恶意附件哈希、BEC 发件人模式等）以标准化的数据结构描述，并在组织间共享的能力。STIX（Structured Threat Information Expression）[1] 和 TAXII（Trusted Automated Exchange of Intelligence Information）[2] 是实现这一能力的 IETF 标准协议；MISP（Malware Information Sharing Platform）是目前最广泛部署的开源情报平台。

## STIX (RFC 7201 / STIX 2.1)

### 协议概述

STIX 是一种基于 JSON 的威胁情报描述语言。RFC 7201 [1] 定义了 STIX 1.x 的架构，而 STIX 2.x 基于 JSON-LD，大幅简化了数据结构。核心对象类型（SDOs - STIX Domain Objects）包括：

| SDO 类型 | 描述 | 邮件安全示例 |
| --- | --- | --- |
| Indicator | 可观察到的威胁特征 | 钓鱼邮件发件 IP、恶意附件 SHA256 |
| Campaign | 系列攻击活动 | "2026 Q2 银行钓鱼攻击" |
| Threat Actor | 威胁行为者 | "TA-543"（已知 BEC 组织） |
| Attack Pattern | 攻击模式（CAPEC） | Business Email Compromise（BEC） |
| Malware | 恶意软件特征 | Emotet 附件的 YARA 规则 |
| Observed Data | 观察到的原始数据 | 邮件头对、MTA 日志 |
| Relationship | 对象间关系 | "Indicator 指向 Malware A" |

### STIX 邮件威胁实例

```
{
  "type": "indicator",
  "id": "indicator--a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created": "2026-07-24T00:00:00.000Z",
  "modified": "2026-07-24T00:00:00.000Z",
  "name": "BEC 钓鱼邮件发件 IP",
  "description": "用于 BEC 欺诈邮件的已知发件 IP /24 范围",
  "pattern": "[ipv4-addr:value = '203.0.113.0/24']",
  "pattern_type": "stix",
  "valid_from": "2026-07-24T00:00:00.000Z",
  "labels": ["phishing", "email", "bec"],
  "indicator_types": ["malicious-activity"],
  "kill_chain_phases": [{
    "kill_chain_name": "email-attack-chain",
    "phase_name": "initial-delivery"
  }]
}
```

```
{
  "type": "indicator",
  "id": "indicator--b2c3d4e5-f6a7-890b-cdef-2345678901ab",
  "name": "钓鱼域 SPF 配置指纹",
  "description": "利用 SPF 软失败域发送冒充邮件",
  "pattern": "[domain-name:value = 'phish-example.com'] AND [domain-dns-spf:contains('?all')]",
  "pattern_type": "stix",
  "valid_from": "2026-07-23T00:00:00.000Z",
  "labels": ["spoofing", "spf-bypass"]
}
```

## TAXII (RFC 7202 / TAXII 2.1)

### 传输协议

TAXII [2] 是 STIX 的传输层协议，定义了情报集合（Collections）和 频道（Channels）的概念。TAXII 2.1 基于 RESTful API，支持 HTTPS 传输，提供 `Discovery`、`Collection Management`、`Poll` 和 `Publish` 四个核心 API 端点。

### TAXII API 交互示例

```
# TAXII 2.1 发现端点
curl -s https://taxii.example.com/taxii2/ \
  -H "Accept: application/taxii+json;version=2.1" \
  -H "Authorization: Bearer ${API_TOKEN}"

# 列出可用的情报集合
curl -s https://taxii.example.com/taxii2/collections/ \
  -H "Accept: application/taxii+json;version=2.1" \
  -H "Authorization: Bearer ${API_TOKEN}" | jq '.collections[] | {id, title, can_read}'

# 从集合拉取最新的邮件威胁情报
# 获取集合中的 STIX 对象（最近 1 小时）
SINCE=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)
curl -s "https://taxii.example.com/taxii2/collections/${COLLECTION_ID}/objects/?added_after=${SINCE}" \
  -H "Accept: application/taxii+json;version=2.1" \
  -H "Authorization: Bearer ${API_TOKEN}" | \
  jq '[.objects[] | select(.type=="indicator" and (.labels[] | contains("email")))]'
```

## MISP 集成

### MISP 架构概述

MISP（Malware Information Sharing Platform）是一个开源的威胁情报共享平台，提供基于 Web 的协作界面、自动化的 IoC 导入/导出、以及与邮件网关的集成能力。MISP 支持以 STIX 格式导出情报，并内置了与 Postfix、Rspamd 等邮件组件的集成模块。

### 邮件安全 IoCs 类型

| IoC 类别 | MISP 属性类型 | 在邮件安全中的应用 |
| --- | --- | --- |
| 发件人 IP | ip-src / ip-dst | RBL 黑名单自动更新、Postfix check\_client\_access |
| 域名 | domain / hostname | Rspamd 域名信誉积分衰减、MTA-STS 策略中标记 |
| SPF 配置特征 | text | 识别 SPF ?all 钓鱼域的模式指纹 |
| URL | url | 邮件正文链接过滤、sandbox 触发 |
| 附件哈希 | md5 / sha1 / sha256 | ClamAV 签名更新、附件级别扫描 |
| 邮件主题/正文指纹 | email-subject / email-body | SpamAssassin 规则更新 |
| 回复地址 | email-src / email-dst | BEC 诈骗者回复地址标记 |

### MISP 与邮件网关汇合架构

```
# MISP → Postfix/Rspamd 自动集成架构

# 1. MISP 发布的情报通过脚本定期拉取
# /etc/cron.d/misp-sync
*/5 * * * * root /usr/local/bin/misp-to-postfix.py

# 2. misp-to-postfix.py - 核心逻辑
# 从 MISP REST API 拉取最新的邮件相关 IoCs
# 转换为 Postfix 可识别的格式写入 hash 表

# MISP API 调用
curl -s -H "Authorization: ${MISP_KEY}" \
  -H "Accept: application/json" \
  "https://misp.local/events/restSearch/returnFormat:json/tags:tlp:green/type:ip-src,domain,url/host-org-id:1" \
  | jq -r '.response[].Event?.Attribute[]? | select(.type == "ip-src") | .value' \
  > /tmp/known-malicious-ips.txt

# 3. 生成 Postfix 访问表
# /etc/postfix/misp_check_client
cat /tmp/known-malicious-ips.txt | \
  while read ip; do
    echo "$ip REJECT 550 5.7.1 MISP - Known malicious source"
  done > /etc/postfix/misp_check_client
postmap /etc/postfix/misp_check_client

# 4. 在 main.cf 中引用
# smtpd_client_restrictions =
#   check_client_access hash:/etc/postfix/misp_check_client
#   permit_mynetworks, ...
```

## 态势感知实战架构

### 完整 ETL 管道

```
# 端到端的邮件威胁情报管道
#
# 1. 数据源层：邮件网关日志、SpamAssassin 规则命中、用户举报垃圾邮件
# 2. 转换层：将 MTA 日志、识别记录转换为 STIX 格式对象
# 3. 共享层：通过 TAXII 推送到上下游情报池
# 4. 消费层：从 MISP 拉取情报，反哺邮件安全策略

# 将邮件安全事件转换为 STIX Indicator（Python 伪代码）
# from stix2 import Indicator, DomainName
# 
# def email_log_to_stix(log_entry):
#     """将邮件日志条目转换为 STIX indicator"""
#     indicators = []
#     # 提取发件 IP
#     if log_entry.client_ip:
#         ind = Indicator(
#             name=f"Known spam source {log_entry.client_ip}",
#             pattern=f"[ipv4-addr:value = '{log_entry.client_ip}']",
#             pattern_type="stix",
#             labels=["spam", "email"],
#             valid_from=datetime.utcnow()
#         )
#         indicators.append(ind)
#     # 提取附件哈希
#     if log_entry.attachment_hash:
#         ind = Indicator(
#             name=f"Malicious attachment {log_entry.attachment_hash[:8]}",
#             pattern=f"[file:hashes.SHA256 = '{log_entry.attachment_hash}']",
#             pattern_type="stix",
#             labels=["malware", "email-attachment"],
#         )
#         indicators.append(ind)
#     return indicators
```

### 邮件安全情报应用示例

```
# Rspamd 集成 MISP 情报
# /etc/rspamd/local.d/antivirus.conf
misp {
  enabled = true;
  # MISP API 配置
  server = "https://misp.local";
  api_key = "...";
  # 同步间隔 (秒)
  interval = 300;
  # 仅拉取邮件相关情报
  tags_filter = ["email", "phishing", "spam"];
  # 对命中的邮件增加评分
  score = 15.0;
  # 自动插入 X-MISP-* 头
  add_header = true;
}
```

### STIX 的邮件安全扩展

STIX 2.1 的扩展机制（Extension Definition）允许社区定义专门用于邮件安全的扩展对象。以下是一些邮件安全场景中常用的扩展方向：

* **SPF/DKIM/DMARC 配置指纹**：将域名的邮件认证配置模式（如 SPF ?all + DKIM non-existent）转化为可匹配的 Indicator——这对于识别"社交工程域名"（typosquatting + 弱认证配置）至关重要
* **BEC 语义模式**：基于发件人显示名与邮箱域名的语义不匹配（如 "CEO" 但发件域为 gmail.com）生成情报
* **邮件头与 MTA 指纹**：基于 Received: 链中的 MTA 标识和时区跳变模式识别邮件路由异常

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-threat-intelligence-sharing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
