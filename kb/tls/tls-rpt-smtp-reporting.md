---
title: "TLS-RPT SMTP 传输加密报告深度解析 — RFC 8460：JSON 失败类型全量分析与自动化处理管道 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/tls-rpt-smtp-reporting.html"
license: CC-BY 4.0
---

# TLS-RPT SMTP 传输加密报告深度解析 — RFC 8460：JSON 失败类型全量分析与自动化处理管道 · ztpop 邮件技术知识库

TLS-RPT SMTP 传输加密报告深度解析 — RFC 8460：JSON 失败类型全量分析与自动化处理管道

## 摘要

TLS-RPT（SMTP TLS Reporting, RFC 8460, September 2018）是 SMTP 传输加密生态中最被低估的协议。与 MTA-STS（RFC 8461）同期发布，TLS-RPT 为域名所有者提供了 SMTP 会话层面的 TLS 连接可观测性——域管理员可以通过 DNS TXT 记录声明报告接收地址，接收来自全球发送方 MTA 的每日 JSON 格式汇总报告。本文以 RFC 8460 协议文本为基线，覆盖 DNS 记录声明语法、
`_smtp._tls`
子域 TXT 记录的 rua 标签规范、JSON 报告的全部字段结构（organization-name、date-range、policies 数组、summary 统计、failure-details 故障明细），逐项解析
`certificate-expired`
、
`certificate-host-mismatch`
、
`certificate-not-trusted`
、
`starttls-not-supported`
、
`tlsa-invalid`
、
`validation-failure`
、
`sts-policy-fetch-error`
七种 result-type 的触发条件与根因定位。后半部分提供可投产的 TLS-RPT JSON 解析 Python 脚本、Prometheus + Grafana TLS 成功率监控面板构建、Postfix TLS 日志与 TLS-RPT 报告的交叉比对方法。昆仑邮件系统为日均 500 万封入站邮件的客户集群运维的 TLS-RPT 处理管道将作为参考架构呈现。

## 1. 协议架构：DNS 声明 → JSON 报告 → MTA 汇总发送

### 1.1 三步工作流（RFC 8460 §3–§4）

TLS-RPT 的生命周期分为三个阶段：

1. **策略发现（Policy Discovery）**
   ：发件方 MTA 每次与某个接收域建立 SMTP 连接时，构造 DNS 查询
   `_smtp._tls. IN TXT`
   。如果查询返回了有效的
   `v=TLSRPTv1`
   记录，发件方 MTA 将解析其中的
   `rua=`
   标签，提取报告接收地址。
2. **会话记录（Session Recording）**
   ：发件方 MTA 在该 24 小时周期内记录下每一次对该接收域的 SMTP TLS 会话结果——包括成功连接的会话数（
   `total-successful-session-count`
   ）和失败会话的详细信息（
   `failure-details`
   ）。
3. **报告生成与发送（Report Generation & Delivery）**
   ：每日 00:00 UTC，发件方 MTA 将该周期的所有会话记录汇总为一份 gzip 压缩的 JSON 文件，作为
   `application/tlsrpt+json`
   MIME 附件通过 SMTP 发送到 rua 指定的接收地址（RFC 8460 §4.2）。

### 1.2 DNS TXT 记录声明（RFC 8460 §3.1）

TLS-RPT 策略以 DNS TXT 记录形式发布在
`_smtp._tls.`
子域上：

```
_smtp._tls.example.com.  3600  IN  TXT  "v=TLSRPTv1; rua=mailto:tls-reports@example.com"
```

记录字段说明：
`v=TLSRPTv1`
——协议版本标识，目前仅 v1 版本；
`rua=`
——Reporting URI for Aggregate reports，支持
`mailto:`
和
`https:`
两种 URI scheme。RFC 8460 §3.1 规定，rua 标签可使用逗号分隔多个报告地址，发件方 MTA 可选择将报告发送到其中任意一个或多个地址。对于大型邮件域，将 rua 导向专用的报告收集邮箱是标准实践——避免报告邮件混入常规管理邮箱。昆仑邮件系统的客户部署中，
`_smtp._tls`
的 DNS TTL 统一设为 3600 秒，允许在 rua 地址变更时在一小时内生效。

```
# 查询 TLS-RPT 策略
dig TXT _smtp._tls.example.com +short

# 输出示例
"v=TLSRPTv1; rua=mailto:tls-report@example.com"

# 多个 rua 地址（逗号分隔）
_smtp._tls.example.com.  IN  TXT  "v=TLSRPTv1; rua=mailto:rpt@example.com,https://rpt-collector.example.com/v1/tlsrpt"
```

## 2. JSON 报告字段全量拆解（RFC 8460 §4.3–§4.5）

### 2.1 报告顶层字段

每份 TLS-RPT 报告是一个 JSON 对象，顶层包含四个必填字段：

2.1 报告顶层字段

| 字段 | 类型 | RFC 8460 | 说明 |
| --- | --- | --- | --- |
| `organization-name` | string | §4.3 | 发件方 MTA 运营组织的名称。无标准化约束，由发件方自行填写，仅作识别用途。Google 的报告填写为 "Google Inc."，Microsoft 填写为 "Microsoft Corporation"。 |
| `date-range` | object | §4.3 | 报告覆盖的时间范围，包含 `start-datetime` 和 `end-datetime` 两个 ISO 8601 UTC 时间戳。通常覆盖前一日 00:00:00Z 至 23:59:59Z。 |
| `contact-info` | string | §4.3 | 发件方的联系信息（通常为电子邮件地址），用于域管理员在发现 TLS 异常时联系发件方 MTA 运营团队。 |
| `report-id` | string | §4.3 | 报告的唯一标识符。RFC 8460 建议格式为 `收件人!发送方!开始时间范围!结束时间范围.唯一后缀` 。用于去重和关联。 |

### 2.2 policies 数组结构

`policies`
数组是 TLS-RPT 报告的数据核心。每一个数组元素代表一个 TLS 策略域的结果聚合：

```
{
  "policies": [{
    "policy": {
      "policy-type": "sts",
      "policy-string": [
        "version: STSv1",
        "mode: testing",
        "mx: mail.example.com",
        "mx: mx2.example.com",
        "max_age: 86400"
      ],
      "policy-domain": "example.com",
      "mx-host": "mail.example.com"
    },
    "summary": {
      "total-successful-session-count": 18500,
      "total-failure-session-count": 127
    },
    "failure-details": [ ... ]
  }]
}
```

2.2 policies 数组结构

| 字段路径 | 类型 | 说明 |
| --- | --- | --- |
| `policy.policy-type` | enum | 策略类型： `sts` （MTA-STS, RFC 8461）、 `tlsa` （DANE, RFC 7672）、 `no-policy-found` （无策略，机会性 TLS）。发件方 MTA 根据实际采用的策略决定此值。 |
| `policy.policy-string` | array of strings | 发件方 MTA 缓存的 MTA-STS policy 文件内容（仅 `policy-type: sts` 时存在）。逐行复现目标域 `.well-known/mta-sts.txt` 的内容，用于故障定位时的策略审计。 |
| `policy.policy-domain` | string | TLS 策略作用的域名。 |
| `policy.mx-host` | string | 发件方 MTA 实际连接的 MX 主机名。与 `failure-details` 中的 `receiving-mx-hostname` 字段配合，用于定位具体是哪台 MX 服务器出现了 TLS 故障。 |
| `summary.total-successful-session-count` | int | 24 小时内 TLS 协商成功且（若策略为 sts/tlsa）验证通过的会话总数。 |
| `summary.total-failure-session-count` | int | 24 小时内 TLS 协商失败或策略验证失败的会话总数。 |

### 2.3 failure-details 故障明细字段

`failure-details`
数组是 TLS-RPT 的情报来源——每一个元素代表一类失败会话的聚合：

```
"failure-details": [{
  "result-type": "certificate-expired",
  "sending-mta-ip": "209.85.220.41",
  "receiving-mx-hostname": "mail.example.com",
  "receiving-mx-helo": "mail.example.com",
  "failed-session-count": 42,
  "failure-reason-code": "X509_V_ERR_CERT_HAS_EXPIRED",
  "additional-information": {
    "certificate-hostname": "mail.example.com",
    "certificate-expiration": "2026-07-09T12:00:00Z"
  }
}]
```

2.3 failure-details 故障明细字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `result-type` | 是 | 故障类型（见 §3 全量解析）。 |
| `sending-mta-ip` | 是 | 发件方 MTA 的出口 IP 地址。用于区分不同来源地的故障（例如某个 IP 因 RPKI 或 GeoIP 导致证书链问题）。 |
| `receiving-mx-hostname` | 否 | SMTP 连接指向的 MX 主机名。对于多 MX 场景，此字段帮助定位具体哪台服务器出现故障。 |
| `receiving-mx-helo` | 否 | 接收方在 SMTP EHLO 响应中宣告的主机名。对于 `certificate-host-mismatch` 故障的定位尤为关键。 |
| `failed-session-count` | 是 | 报告周期内该故障类型在该 source-ip + mx-host 组合下发生的会话次数。 |
| `failure-reason-code` | 否 | 发件方 TLS 库返回的低层错误码（如 OpenSSL 的 X509\_V\_ERR\_\* 码）。有助于精确诊断。 |
| `additional-information` | 否 | 自由格式 JSON 对象，提供与故障诊断相关的额外元数据。常见字段包括 `certificate-hostname` 、 `certificate-expiration` 、 `received-certificate-subject` 。 |

## 3. 七大 result-type 故障全量分析

RFC 8460 §4.5 定义了六种标准 result-type，加上实践中最常见的
`sts-policy-fetch-error`
，共七类故障：

3. 七大 result-type 故障全量分析

| result-type | 触发条件 | RFC 8460 引用 |
| --- | --- | --- |
| `certificate-expired` | 接收方 MTA 的 TLS 证书 `notAfter` 字段晚于当前 UTC 时间，即证书已过期 | §4.5 表 1 |
| `certificate-host-mismatch` | 证书 CN 或 SAN 均不包含发件方连接的 MX 主机名（RFC 6125 §6.4.4） | §4.5 表 1 |
| `certificate-not-trusted` | 证书链中某一级 CA 不在发件方 MTA 的信任锚存储中（如自签名证书、私有 CA） | §4.5 表 1 |
| `starttls-not-supported` | 接收方 MTA 在 EHLO 响应中未声明 250-STARTTLS 能力。当策略要求 enforce 时此故障导致投递中断 | §4.5 表 1 |
| `tlsa-invalid` | DANE TLSA 记录（RFC 7672）的关联数据哈希与服务器证书指纹不匹配 | §4.5 表 1 |
| `validation-failure` | 通用 TLS 握手失败（协议版本不兼容、密码套件协商失败、证书链中某级已撤销） | §4.5 表 1 |
| `sts-policy-fetch-error` | （非 RFC 8460 标准类型，但在 Google 和 Microsoft 的 TLS-RPT 报告中频繁出现）发件方无法通过 HTTPS 获取目标域的 MTA-STS policy 文件（ `.well-known/mta-sts.txt` ），原因包括 DNS 解析失败、TLS 握手失败、HTTP 5xx/4xx、policy 文件格式错误 | 实践中观测 |

### 3.1 certificate-expired 深度诊断

证书过期是生产环境中最常见的 TLS-RPT 告警来源。当一个域的 TLS 证书在
`notAfter`
日期之后，发件方 MTA 记录
`certificate-expired`
并在
`additional-information`
中提供
`certificate-expiration`
字段。诊断流程：

```
# Step 1: 直接连接验证证书
echo | openssl s_client -connect mail.example.com:25 \
    -starttls smtp 2>&1 | openssl x509 -noout -dates -subject -issuer

# Step 2: 从 MX 记录列表逐一验证（多 MX 环境必须逐一检查）
dig MX example.com +short
# 假设输出 mail1.example.com, mail2.example.com
for mx in mail1.example.com mail2.example.com; do
    echo "=== $mx ==="
    echo | openssl s_client -connect ${mx}:25 -starttls smtp 2>/dev/null \
        | openssl x509 -noout -dates -subject
done

# Step 3: 检查证书是否在报告时间范围内过期
# 对比 additional-information.certificate-expiration 与 date-range.end-datetime
```

根因定位：若
`additional-information.certificate-expiration`
早于
`date-range.end-datetime`
，说明证书在报告周期内已过期——确认 Let's Encrypt 自动续期 cron 是否正常运行，或商业证书是否已执行手动续期操作。若证书在报告时间范围内未过期但发件方仍报告
`certificate-expired`
，可能的原因包括：(1) 发件方 MTA 的系统时钟偏差（NTP 不同步导致提前判定过期）；(2) 证书已续期但 Postfix 未重新加载新证书（
`systemctl reload postfix`
未执行，仍在用旧证书文件）；(3) 中间 CA 证书过期而导致链验证失败（但被错误归类为
`certificate-expired`
），需检查完整证书链。

### 3.2 certificate-host-mismatch 根因矩阵

当发件方发起的 SMTP 连接目标主机名（MX 记录中的主机名或 EHLO 响应中的主机名）不在接收方证书的 subjectAltName 列表中时，触发
`certificate-host-mismatch`
。RFC 6125 §6.4.4 允许发件方使用 MX 主机名或 EHLO 主机名进行验证，因此两种不匹配均可能导致此故障。常见根因：

* **MX 记录指向 CNAME 而非 A 记录**
  ：MX 记录解析后的最终主机名与证书 SAN 不一致。例如
  `mx CNAME mail.example.com`
  → 实际连接
  `mail2.example.net`
  （不同域），但证书 SAN 仅有
  `*.example.com`
  。
* **负载均衡器（LB）TLS 卸载后证书不在 LB 上**
  ：LB 作为 SMTP 代理使用通用证书（如
  `*.lb.example.net`
  ）而 MX 记录指向
  `mx.example.com`
  。
* **通配符证书边界问题**
  ：
  `*.example.com`
  覆盖
  `a.example.com`
  但不覆盖
  `a.b.example.com`
  。若 MX 主机名为
  `mx-east.example.com`
  ，通配符覆盖；若为
  `mx.east.example.com`
  ，通配符不覆盖。

### 3.3 starttls-not-supported 的三种场景

`starttls-not-supported`
故障在 MTA-STS
`mode: enforce`
环境下最为致命——它不仅出现在 TLS-RPT 报告中，还会导致实际投递失败。三种典型场景：

1. **Postfix 配置中 smtpd\_tls\_security\_level = none**
   ：明确禁用了 STARTTLS。修改为
   `may`
   至少启用 STARTTLS 能力。
2. **证书文件路径错误导致 Postfix 启动 TLS 引擎失败**
   ：
   `postconf smtpd_tls_cert_file`
   指向的文件不存在或权限错误（非 root 用户无法读取）。Postfix 在后台静默禁用 TLS，EHLO 响应不再包含 250-STARTTLS。
3. **端口 25 前面有中间设备拦截 STARTTLS 声明**
   ：某些旧版企业防火墙或 SMTP 应用层网关（ALG）主动从 EHLO 响应中剥离 250-STARTTLS 行。需要使用
   `telnet`
   或
   `swaks`
   分别从内网和公网测试来排除。

## 4. TLS-RPT JSON 解析与 Prometheus 监控管道

### 4.1 Python 解析脚本（支持 .json.gz 附件）

```
#!/usr/bin/env python3
"""
tlsrpt-parser.py — 解析 TLS-RPT 聚合报告 JSON，输出 Prometheus metrics
RFC 8460 §4.3–§4.5
用法: python3 tlsrpt-parser.py 
"""
import sys, json, gzip, os
from datetime import datetime
from collections import defaultdict

def load_report(path):
    if path.endswith('.gz'):
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            return json.load(f)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_report(report):
    org = report.get('organization-name', 'unknown')
    report_id = report.get('report-id', 'unknown')
    date_range = report.get('date-range', {})
    start = date_range.get('start-datetime', '?')
    end = date_range.get('end-datetime', '?')

    print(f"# TLS-RPT Report: {report_id}")
    print(f"# Reporter: {org}  Period: {start} → {end}")

    # 统计结构: {policy_domain: {result_type: {mx: count}}}
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    total_success = 0
    total_failure = 0

    for policy in report.get('policies', []):
        ptype = policy['policy']['policy-type']
        domain = policy['policy']['policy-domain']
        summary = policy.get('summary', {})
        success = summary.get('total-successful-session-count', 0)
        failure = summary.get('total-failure-session-count', 0)
        total_success += success
        total_failure += failure

        print(f"\n# Domain: {domain}  Policy: {ptype}")
        print(f"#   Success: {success}  Failure: {failure}  Rate: {success/(success+failure)*100:.2f}%" if (success+failure) > 0 else f"#   Success: {success}  Failure: {failure}")

        for fd in policy.get('failure-details', []):
            rt = fd.get('result-type', 'unknown')
            mx = fd.get('receiving-mx-hostname', '?')
            ip = fd.get('sending-mta-ip', '?')
            cnt = fd.get('failed-session-count', 0)
            reason = fd.get('failure-reason-code', '')
            stats[domain][rt][mx] += cnt

            print(f"  FAIL [{rt}] mx={mx} ip={ip} cnt={cnt} reason={reason}")

    # 输出 Prometheus 格式指标
    print(f"\n# Prometheus metrics (expose via textfile collector):")
    ts = datetime.utcnow().timestamp()
    print(f'tlsrpt_successful_sessions_total{{reporter="{org}"}} {total_success} {int(ts)}')
    print(f'tlsrpt_failed_sessions_total{{reporter="{org}"}} {total_failure} {int(ts)}')
    for domain in stats:
        for rt in stats[domain]:
            total = sum(stats[domain][rt].values())
            label_safe_domain = domain.replace('.', '_').replace('-', '_')
            print(f'tlsrpt_failure_by_type{{domain="{domain}",result_type="{rt}"}} {total} {int(ts)}')

if __name__ == '__main__':
    if len(sys.argv)
<
2:
        print(f"用法: {sys.argv[0]}  [...]")
        sys.exit(1)
    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            report = load_report(arg)
            parse_report(report)
        else:
            print(f"文件不存在: {arg}", file=sys.stderr)
```

### 4.2 Prometheus Textfile Collector 集成

将上述解析器的输出重定向到 Prometheus Node Exporter 的 textfile collector 目录，可实现每分钟更新的 TLS 成功率仪表盘：

```
# crontab: 每 5 分钟解析最新的 TLS-RPT 报告
*/5 * * * * /usr/local/bin/tlsrpt-parser.py /var/spool/tlsrpt/*.json.gz > /var/lib/prometheus/textfile/tlsrpt.prom

# Prometheus scrape config
# - job_name: node
#   static_configs:
#     - targets: ['localhost:9100']
```

### 4.3 Grafana 面板配置

推荐构建以下监控面板：

* **TLS 成功率趋势图**
  ：
  `rate(tlsrpt_successful_sessions_total[24h]) / (rate(tlsrpt_successful_sessions_total[24h]) + rate(tlsrpt_failed_sessions_total[24h])) * 100`
* **按 result-type 的故障分布**
  ：
  `tlsrpt_failure_by_type`
  指标的堆叠柱状图
* **按 Reporter 的 TLS 成功率 Top-K**
  ：用于发现某个特定发件方 MTA 的 TLS 问题（可能表明该 MTA 的 TLS 库版本陈旧
* **证书到期预警**
  ：从
  `certificate-expired`
  故障类型的变化率构建提前告警

## 5. 参考架构：昆仑邮件系统 TLS-RPT 处理管道

昆仑邮件系统为日均 500 万封入站邮件的企业集群设计了一套完整的 TLS-RPT 处理管道，架构如下：

1. **收件层**
   ：专用 IMAP 邮箱
   `tls-reports@customer.example.com`
   ，所有 MTA-STS 和 TLS-RPT 的 rua 地址均指向此邮箱。
2. **提取层**
   ：Python 脚本通过 IMAP IDLE 模式实时监听新邮件到达事件，自动提取
   `application/tlsrpt+json`
   附件，解压并存入本地文件系统。邮件标记为已读后归档到 IMAP Archive 文件夹。
3. **解析层**
   ：每小时 cron 任务调用解析脚本批量处理累积的 JSON 报告，生成 Prometheus textfile 格式指标。
4. **告警层**
   ：Prometheus AlertManager 配置了三个告警规则：(a)
   `tlsrpt_failed_sessions_total > 0`
   持续超过 1 小时的 Warning 级别告警；(b) 单一
   `certificate-expired`
   事件的 Critical 级别告警（立即通知运维团队续期证书）；(c)
   `tls_success_rate < 95%`
   的 Warning 级别告警。
5. **可视化层**
   ：Grafana 面板按域维度展示 TLS 成功率、故障分布和 30 天趋势。运维团队在晨会时扫一眼即可确认所有域的 TLS 状况。

该管道处理的 TLS-RPT 报告日均量约 2,000 封（来自 Google、Microsoft、Yahoo、ProtonMail、GMX 等主要邮件服务商的发送 MTA），覆盖约 150 万次 SMTP TLS 会话的每日结果。根据 GB/T 37002-2018 第 6.3.4 节的邮件系统安全审计要求，TLS-RPT 报告构成了传输层安全审计轨迹的核心数据源。

### 参考文献

1. RFC 8460 — SMTP TLS Reporting (IETF, September 2018). 第 3 节 TLS-Report Domain TXT Record 定义 \_smtp.\_tls 子域及 v=TLSRPTv1/rua 标签语法, 第 4 节定义 JSON 报告格式、MIME 类型 application/tlsrpt+json, 第 4.3 节定义 JSON 顶层字段, 第 4.5 节定义七种 result-type 故障编码.
2. RFC 8461 — SMTP MTA Strict Transport Security (MTA-STS) (IETF, September 2018). 第 3 节 MTA-STS Policy 定义 policy 文件格式与 HTTPS 发布路径, 第 4 节 Policy Application 定义 testing/enforce 两种模式下的发件方行为, 第 5 节定义 \_mta-sts DNS TXT 记录.
3. RFC 6125 — Representation and Verification of Domain-Based Application Service Identity within Internet Public Key Infrastructure Using X.509 (IETF, March 2011). 第 6.4.4 节定义 SMTP 场景下的 TLS 证书主机名验证规则——允许使用 MX 主机名或 EHLO 主机名进行验证.
4. RFC 7672 — SMTP Security via Opportunistic DANE TLS (IETF, October 2015). 第 3 节 TLSA Records for SMTP 定义 DANE 模式下 TLSA 记录的用法, 第 4 节定义 DANE policy-type 下发件方的策略应用逻辑.
5. RFC 3207 — SMTP Service Extension for Secure SMTP over Transport Layer Security (IETF, February 2002). 第 4 节 STARTTLS Extension Definition 定义 SMTP STARTTLS 扩展的 EHLO 协商流程.
6. GB/T 37002-2018 — 信息安全技术 电子邮件系统安全技术要求. 第 6.3.4 节 安全审计要求邮件系统应记录传输安全事件并具备告警能力, 第 6.3.2 节定义邮件传输安全的基本技术要求.
7. NIST SP 800-52 Rev.2 — Guidelines for the Selection, Configuration, and Use of TLS Implementations (NIST, August 2019). 第 3.4 节 Certificate Validation 定义 TLS 证书验证的最佳实践, 第 3.5 节定义证书生命周期管理.
8. Postfix TLS Readme —
   <https://www.postfix.org/TLS_README.html>
   . STARTTLS 配置参数详解、日志级别设置及证书管理.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tls-rpt-smtp-reporting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
