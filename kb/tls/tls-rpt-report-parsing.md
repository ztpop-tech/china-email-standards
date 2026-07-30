---
title: "TLS-RPT 报告解读与自动化分析"
source: "https://ztpop.net/kb/tls-rpt-report-parsing.html"
license: CC-BY 4.0
---

# TLS-RPT 报告解读与自动化分析

## TLS-RPT协议概述

TLS Reporting（TLS-RPT）由RFC 8460定义，是与MTA-STS和DANE配套的报告机制。当发送方试图建立加密连接但遭遇失败时，TLS-RPT向域名所有者报告这些失败详情。与DMARC的RUA聚合报告类似，TLS-RPT报告以JSON格式聚合发送方观察到的TLS连接结果。

启用TLS-RPT需要在DNS中发布一个TXT记录。报告接收地址通过rua=标签指定，格式为mailto: URI。TLS-RPT与MTA-STS共享DNS部署位置（\_smtp.\_tls.{domain}），但TLS-RPT的记录格式完全不同。

## TLS-RPT DNS配置与报告投递

### DNS记录格式

```
# TLS-RPT DNS TXT 记录
_smtp._tls.example.com TXT "v=TLSRPTv1; rua=mailto:tls-reports@example.com"

# 同时为子域配置
_smtp._tls.mail.example.com TXT "v=TLSRPTv1; rua=mailto:tls-subdomain@example.com"

# 多报告地址（逗号分隔）
_smtp._tls.example.com TXT "v=TLSRPTv1; \
  rua=mailto:tls@example.com,mailto:tls-backup@backup.example.com"
```

### 投递流程

RFC 8460 §4.4定义了报告投递的流程：发送方收集一个报告周期内的TLS失败记录，通过SMTP邮件投递到rua中指定的邮箱地址。报告邮件必须满足以下要求：Sender头部设置为空且Return-Path必须指向发送方，邮件主题固定为{Report Summary; Format: application/tlsrpt+json; Report-ID: UUID}，Content-Type为application/tlsrpt+json。接收方需要设置邮件过滤器来捕获和分类这些报告。

## JSON报告结构详解

TLS-RPT报告采用JSON格式（RFC 8259）。顶级结构如下：

```
{
  "organization-name": "Example Sender Corp",
  "date-range": {
    "start-datetime": "2025-07-28T00:00:00Z",
    "end-datetime": "2025-07-29T00:00:00Z"
  },
  "contact-info": "tls-report@example-sender.com",
  "report-id": "2025-07-28T00:00:00Z_example.com",
  "policies": [
    {
      "policy": {
        "policy-type": "sts",
        "policy-string": ["version: STSv1", "mode: enforce"],
        "policy-domain": "example.com",
        "mx-host": ["mail1.example.com", "*.mx.example.net"],
        "mx-pattern": ["mail1.example.com", "*.mx.example.net"]
      },
      "summary": {
        "total-successful-session-count": 850,
        "total-failure-session-count": 3
      },
      "failure-details": [
        {
          "result-type": "certificate-expired",
          "sending-mta-ip": "198.51.100.10",
          "receiving-mx-hostname": "mail1.example.com",
          "receiving-mx-helo": "mail1.example.com",
          "receiving-ip": "203.0.113.50",
          "failed-session-count": 2,
          "additional-information": "Certificate expired 2025-07-25T23:59:59Z"
        }
      ]
    }
  ]
}
```

关键字段解读：

* result-type — 失败原因分类（共9种RFC 8460定义的类型）
* total-successful-session-count — 成功会话数（正常指标）
* total-failure-session-count — 失败会话数（重点关注）
* policy-type — 可以是"sts"（MTA-STS）或"tlsa"（DANE）
* 上表中certificate-expired代表证书过期，需立即更新

## 失败原因类型与诊断

RFC 8460 §1定义了9种标准result-type。每种类型对应特定的TLS故障模式：

| result-type | 含义 | 常见原因 | 排修优先级 |
| --- | --- | --- | --- |
| starttls-not-supported | 服务器未响应STARTTLS | MTA版本过旧或端口配置错误 | 高 |
| certificate-expired | 接收方证书已过期 | 忘记更新CA证书 | 高 |
| certificate-not-yet-valid | 证书尚未生效 | 系统时间不同步或证书有效期误配 | 中 |
| certificate-host-mismatch | 证书CN/SAN与MX主机不匹配 | 证书颁发给错误的域名或泛域名未正确覆盖 | 高 |
| certificate-revoked | 证书已被吊销 | CA撤销或私钥泄露 | 紧急 |
| tlsa-invalid | TLSA记录无效 | DANE记录类型/协议/端口参数错误 | 高 |
| validation-failure | TLS验证失败 | 证书链问题算法不匹配 | 中 |
| sts-policy-fetch-error | MTA-STS策略获取失败 | HTTPS证书到期或.mta-sts子域不可达 | 高 |
| sts-policy-invalid | 策略文件解析错误 | 格式错误或缺少必填字段 | 中 |

## 自动化分析管道搭建

### 邮件提取与解析

```
# 使用Python解析TLS-RPT报告
import json
import email
from email import policy

with open('tls-report.eml', 'r') as f:
    msg = email.message_from_file(f, policy=policy.default)
    
# 验证Content-Type
if msg.get_content_type() != 'application/tlsrpt+json':
    raise ValueError(f"Not a TLS-RPT report: {msg.get_content_type()}")

payload = msg.get_content()
report = json.loads(payload)

# 提取策略和失败信息
for policy_entry in report.get('policies', []):
    policy_info = policy_entry['policy']
    summary = policy_entry['summary']
    
    success_rate = summary['total-successful-session-count'] / \
        (summary['total-successful-session-count'] + \
         summary['total-failure-session-count']) * 100
    
    print(f"Policy: {policy_info['policy-domain']}")
    print(f"Success rate: {success_rate:.2f}%")
    
    for failure in policy_entry.get('failure-details', []):
        print(f"  FAIL: {failure['result-type']}")
        print(f"    MX: {failure['receiving-mx-hostname']}")
        print(f"    Count: {failure['failed-session-count']}")
```

### 告警规则配置

基于TLS-RPT报告的告警规则建议：

1. 单日失败次数>100或成功率<90%时触发告警
2. certificate-revoked类型出现即触发紧急告警
3. certificate-expired类型在证书到期前30天即预警
4. 连续3天收到同一MX的sts-policy-fetch-error需手动排查

## 与DMARC RUA报告的配合分析

TLS-RPT报告与DMARC RUA报告互为补充。RUA报告提供发件域的身份验证通过率，TLS-RPT提供加密传输的连接质量。联合分析的最佳实践：

* 结合DMARC成功率和TLS-RPT成功率的交叉分析
* 当DMARC p=reject后TLS-RPT失败率突然升高时，检查是否有邮件发送方因TLS问题投递失败
* 使用统一的报告时间窗口（如24小时UTC分割）对齐两组报告的数据
* 定期（每周）生成TLS-RPT趋势报告，与MTA-STS策略变更日志交叉比对

建议将TLS-RPT报告管理纳入邮件运维的SLA标准流程。至少每周检查一次报告摘要，每月做一次趋势分析。对突然出现的批量失败迅速响应，这往往是证书到期或策略配置错误的早期信号。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tls-rpt-report-parsing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
