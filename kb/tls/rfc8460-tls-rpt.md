---
title: "RFC 8460 TLS-RPT：SMTP TLS 连接失败报告机制"
source: "https://ztpop.net/kb/rfc8460-tls-rpt.html"
license: CC-BY 4.0
---

# RFC 8460 TLS-RPT：SMTP TLS 连接失败报告机制

## 概述

STARTTLS、DANE TLSA（RFC 7672）与 MTA-STS（RFC 8461）解决了 SMTP 传输加密的"能力"问题，却没有回答"加密到底有没有成功"。误配置或主动降级攻击可能导致邮件以明文或未认证方式投递，而接收域毫无感知。RFC 8460 定义的 TLS-RPT 让发送系统向接收域共享 TLS 连接的成功/失败统计与具体信息，用于检测中间人攻击、诊断误配置，并以"心跳"确认报告链路本身可用。

## 报告发布：\_smtp.\_tls TXT

接收域通过 DNS 的 `_smtp._tls.<domain>` TXT 记录发布 TLSRPT 策略，指令含 `v=TLSRPTv1` 与一个或多个 `rua=` 聚合报告 URI：

```
_smtp._tls.example.com. IN TXT "v=TLSRPTv1; rua=https://report.example.com/v1; rua=mailto:reports@example.com"
```

## JSON 报告结构

报告采用 I-JSON（RFC 7493）格式，顶层字段如下：

| 字段 | 含义 |
| --- | --- |
| `organization-name` | 负责报告的组织名称 |
| `date-range` | 报告时间范围（UTC 全天，RFC 3339） |
| `report-id` | 报告唯一标识 |
| `policies[]` | 策略数组，每项含 `policy` / `summary` / `failure-details` |
| `summary` | `total-successful-session-count` 与 `total-failure-session-count` |

## 失败类型（result-type）

| 分类 | result-type | 说明 |
| --- | --- | --- |
| 协商失败 | `starttls-not-supported` | 接收 MX 不支持 STARTTLS |
| 协商失败 | `certificate-host-mismatch` | 证书与 MTA-STS/DANE 约束不符（如 SAN 不匹配） |
| 协商失败 | `certificate-expired` / `certificate-not-trusted` | 证书过期 / CA 不信任或链错误 |
| MTA-STS | `sts-policy-fetch-error` / `sts-policy-invalid` / `sts-webpki-invalid` | 策略获取失败 / 策略无效 / PKIX 认证失败 |
| DANE | `tlsa-invalid` / `dnssec-invalid` / `dane-required` | TLSA 无效 / 无 DNSSEC / 强制 DANE 缺失 |

## 投递方式

* **HTTPS**：`rua=https://...`，发送方以 POST 提交，媒体类型 `application/tlsrpt+json` 或 `+gzip`，接收方返回 2xx 即成功。
* **MAILTO**：`rua=mailto:reports@example.com`，以 `multipart/report; report-type="tlsrpt"` 投递，报告须含有效 DKIM 签名，否则接收方丢弃。

## 示例报告片段

```
{
  "organization-name": "Example Sender",
  "date-range": { "start-datetime": "2026-07-25T00:00:00Z",
                  "end-datetime": "2026-07-25T23:59:59Z" },
  "report-id": "5065427c-23d3-47e1-a6e4-6d3f5b1e9a02",
  "policies": [{
    "policy-type": "sts",
    "policy-domain": "example.com",
    "summary": { "total-successful-session-count": 18432,
                 "total-failure-session-count": 7 },
    "failure-details": [{
      "result-type": "certificate-host-mismatch",
      "failed-session-count": 7,
      "receiving-mx-hostname": "mail.example.com",
      "receiving-ip": "203.0.113.10"
    }]
  }]
}
```

## 与 MTA-STS 的关系

TLS-RPT 是 MTA-STS（RFC 8461）的伴随规范。`policy-type: "sts"` 表示应用了 MTA-STS 策略，`policy-string` 直接携带接收站点的 STS 策略文本；若既无 DANE 也无 MTA-STS 策略，则标记 `no-policy-found`，仅作为连通性心跳。

### 相关主题

* [RFC 8461 MTA-STS](/kb/rfc8461-mta-sts.html)：强制 SMTP 传输加密的策略发布机制
* [DANE TLSA 在 SMTP 的部署](/kb/dane-tlsa-smtp-deployment.html)：基于 DNSSEC 的传输身份校验
* [DMARC 聚合报告解析](/kb/dmarc-aggregate-reporting.html)：邮件认证层的可观测性对照
* [TLS-RPT 记录生成器](/tools/tls-rpt-generator.html)：生成 \_smtp.\_tls 报告记录，配置 rua 报告地址监控 TLS 投递

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8460-tls-rpt.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
