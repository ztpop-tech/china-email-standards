---
title: "TLS-RPT 邮件传输安全报告 — RFC 8460：JSON 报告结构与 MTA-STS 策略联动 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/tls-rpt-guide.html"
license: CC-BY 4.0
---

# TLS-RPT 邮件传输安全报告 — RFC 8460：JSON 报告结构与 MTA-STS 策略联动 · ztpop 邮件技术知识库

TLS-RPT 邮件传输安全报告 — RFC 8460：JSON 报告结构与 MTA-STS 策略联动

## 摘要

TLS-RPT（TLS Reporting, RFC 8460, September 2018）是 SMTP TLS 加密生态中的可观测性组件。MTA-STS（RFC 8461）和 DANE（RFC 7672）提供了域名级别的传输加密策略执行机制，但它们都缺乏一个原生的问题发现通道——域管理员无法知道其他 MTA 在尝试向自己的域发送邮件时是否遇到了 TLS 协商失败。TLS-RPT 填补了这个空白：它定义了一种基于 DNS TXT 记录声明报告接收地址（
`_smtp._tls`
子域）的机制，由发送方 MTA 在每次 SMTP 会话后生成 JSON 格式的 TLS 连接报告，每日汇总一次以
`multipart/report`
格式通过邮件发送到域管理员指定的报告地址。本文逐字段解析 RFC 8460 定义的 JSON 报告结构，覆盖与 MTA-STS 策略联动的工作流，并以证书过期（certificate-expired）、主机名不匹配（certificate-host-mismatch）、STARTTLS 未支持（starttls-not-supported）三种高频 TLS 故障类型的检测与修复作为桥梁到运维实践。

## 1. TLS-RPT 架构：DNS 声明 + JSON 报告

### 1.1 DNS TXT 记录声明（RFC 8460 §3）

域管理员通过在
`_smtp._tls.`
的 DNS TXT 记录中发布报告策略来启用 TLS-RPT：

```
_smtp._tls.example.com.  IN  TXT  "v=TLSRPTv1; rua=mailto:tls-reports@example.com"
```

`v=TLSRPTv1`
声明协议版本（目前只有 v1），
`rua`
标签（Reporting URI for Aggregate reports）指定报告接收地址，支持
`mailto:`
和
`https:`
两种 URI scheme。RFC 8460 第 3.1 节规定：rua 地址必须是完整的 URI，域管理员可以指定多个 rua 地址（以逗号分隔），每个发送方 MTA 可以根据自身能力将报告发送到任意一个或多个地址。

对于大型邮件域，TLS-RPT 报告量可达到每日数千封。昆仑邮件系统为一个日均 200 万封入站邮件的企业客户运维的 TLS-RPT 处理管道中，每日接收约 8,000 封来自 Google、Microsoft、Yahoo 等主要 MTA 的 TLS-RPT 报告，使用定制 Python 解析器将 JSON 数据导入 Prometheus 时序数据库用于 TLS 成功率监控。

### 1.2 报告传输格式（RFC 8460 §4）

TLS-RPT 报告以 MIME
`multipart/report`
格式通过 SMTP 发送，包含两个部分：第一部分是
`text/plain`
的人类可读摘要，第二部分是
`application/tlsrpt+json`
（RFC 8460 注册的 MIME 类型）附件的机器可读 JSON 数据。发送方 MTA 每日 00:00 UTC 生成一份覆盖过去 24 小时的汇总报告，包含该期间内所有向目标域发起的 SMTP TLS 会话的记录。

## 2. TLS-RPT JSON 报告结构逐字段解析

### 2.1 报告顶层结构（organization-name, date-range, contact-info）

```
{
  "organization-name": "Google Inc.",
  "date-range": {
    "start-datetime": "2026-07-10T00:00:00Z",
    "end-datetime": "2026-07-10T23:59:59Z"
  },
  "contact-info": "smtp-tls-reporting@google.com",
  "report-id": "2026-07-10T00:00:00Z_example.com",
  "policies": [ ... ]
}
```

`organization-name`
：发送方 MTA 运营组织的名称，由发送方自行填写，无标准化验证，仅作识别用途。
`date-range`
：覆盖的时间范围，RFC 8460 要求时间戳使用 ISO 8601 格式并以 UTC 表示。
`report-id`
：报告的唯一标识符，由发送方生成，用于去重和关联。
`contact-info`
：发送方的联系信息（通常为 email 地址），供域管理员遇问题时联系。

### 2.2 policies 数组：策略类型与 TLS 结果

`policies`
数组是报告的核心数据，每个元素代表一个 TLS 策略域（policy domain），包含该域下所有 TLS 会话的成功/失败统计：

```
"policies": [{
  "policy": {
    "policy-type": "sts",
    "policy-string": [
      "version: STSv1",
      "mode: enforce",
      "mx: mail.example.com",
      "max_age: 604800"
    ],
    "policy-domain": "example.com"
  },
  "summary": {
    "total-successful-session-count": 4750,
    "total-failure-session-count": 12
  },
  "failure-details": [
    {
      "result-type": "certificate-expired",
      "sending-mta-ip": "209.85.220.41",
      "receiving-mx-hostname": "mail.example.com",
      "receiving-mx-helo": "mail.example.com",
      "failed-session-count": 3,
      "failure-reason-code": "X509_V_ERR_CERT_HAS_EXPIRED",
      "additional-information": {
        "certificate-hostname": "mail.example.com",
        "certificate-expiration": "2026-07-09T12:00:00Z"
      }
    }
  ]
}]
```

### 2.3 policy-type 字段取值

RFC 8460 定义了三种
`policy-type`
：
**sts**
（MTA-STS, RFC 8461）——发件方根据目标域的 MTA-STS policy 文件执行了 TLS 强制策略；
**tlsa**
（DANE, RFC 7672）——发件方根据 DNSSEC 签名的 TLSA 记录验证了服务器证书；
**no-policy-found**
——目标域未发布任何 TLS 策略，发件方使用了机会性 TLS（Opportunistic TLS, RFC 3207）。

### 2.4 result-type 故障编码（RFC 8460 §4.3）

2.4 result-type 故障编码（RFC 8460 §4.3）

| result-type | 含义 | 触发条件 |
| --- | --- | --- |
| `certificate-expired` | 接收方 TLS 证书已过期 | `notAfter` 字段晚于当前 UTC 时间 |
| `certificate-host-mismatch` | 证书 CN/SAN 与 MX 主机名不匹配 | 发件方连接的 MX 主机名不在证书的 subjectAltName 列表中 |
| `certificate-not-trusted` | 证书链中某个 CA 不受信任 | 根 CA 不在发件方 MTA 的信任锚存储（如 `/etc/ssl/certs/` ）中 |
| `starttls-not-supported` | 接收方 MTA 在 EHLO 响应中未声明 STARTTLS | 端口 25 的 EHLO 响应不含 250-STARTTLS 行 |
| `tlsa-invalid` | TLSA 记录与服务器证书不匹配 | DANE-TA(2) 或 DANE-EE(3) 的关联数据哈希与指纹不匹配 |
| `validation-failure` | 通用验证失败（非以上分类的 TLS 错误） | TLS 握手阶段异常（如协议版本不兼容、密码套件不匹配） |

## 3. 与 MTA-STS 的策略联动

### 3.1 MTA-STS 与 TLS-RPT 的互补关系

MTA-STS（RFC 8461, September 2018）和 TLS-RPT 由同一 RFC 组同期发布，设计上互为补充。MTA-STS 是策略执行引擎——域管理员通过
`_mta-sts.`
的 TXT 记录声明 MTA-STS 模式（testing 或 enforce），通过
`https://mta-sts./.well-known/mta-sts.txt`
的 policy 文件定义合法的 MX 主机列表和 max\_age。TLS-RPT 是策略执行的可观测性通道——域管理员通过接收报告观测 MTA-STS 策略是否导致了投递失败。

典型部署工作流：(1) 首先部署 MTA-STS 策略的
`mode: testing`
（策略仅报告，不中断投递）；(2) 启用 TLS-RPT DNS 记录，观察 7-14 天内的报告数据；(3) 修复报告中出现的 TLS 故障（如证书续期、MX 主机名修正）；(4)
`total-failure-session-count`
降至 0 后切换 MTA-STS 为
`mode: enforce`
。

### 3.2 sts policy-type 的额外字段

当
`policy-type`
为
`sts`
时，JSON 报告的
`policy`
对象包含
`policy-string`
数组——发送方 MTA 在发送时缓存的目标域 MTA-STS policy 文件内容的逐行记录。这个字段对于审计和故障定位极为有用：如果
`failure-details`
中出现了
`certificate-host-mismatch`
，检查
`policy-string`
中的
`mx:`
行可确认发送方使用的 MX 主机名是否与证书中的 subjectAltName 匹配。

```
"policy-string": [
  "version: STSv1",
  "mode: enforce",
  "mx: mail1.example.com",
  "mx: mail2.example.com",
  "max_age: 86400"
]
```

如果
`mx:`
行声明了
`mail1.example.com`
但该主机的 TLS 证书 SAN 为
`*.example.net`
，则
`certificate-host-mismatch`
必然发生。

## 4. 常见 TLS 故障的诊断与修复

### 4.1 certificate-expired：证书过期

检测方法：在 TLS-RPT 报告中查找
`"result-type": "certificate-expired"`
，
`additional-information`
对象提供
`certificate-expiration`
字段记录证书过期时间。命令行复现：

```
$ echo | openssl s_client -connect mail.example.com:25 \
    -starttls smtp 2>/dev/null | \
    openssl x509 -noout -dates
notBefore=Jul  9 00:00:00 2025 GMT
notAfter=Jul  8 23:59:59 2026 GMT
```

修复：(1) 使用 Let's Encrypt 的 certbot 自动化续期（
`certbot renew --force-renewal`
）；(2) 续期后确保 Postfix 重新加载证书：
`systemctl reload postfix`
；(3) 验证新证书链完整：
`openssl s_client -connect mail.example.com:25 -starttls smtp -showcerts`
确认整个链（服务器证书→中间 CA→根 CA）可被验证。

### 4.2 certificate-host-mismatch：主机名不匹配

TLS 客户端（发件方 MTA）在握手完成后会验证服务器证书的 CN 和 subjectAltName 是否包含其连接的 MX 主机名。如果 MX 主机名（如
`mail.example.com`
）不在证书的 SAN 列表中，验证失败。复现命令：

```
$ echo | openssl s_client -connect mail.example.com:25 -starttls smtp \
    -verify_hostname mail.example.com 2>&1 | grep 'verify error'
verify error:num=62:Hostname mismatch
```

修复方案：(1) 重新签发证书，在 SAN 中包含所有 MX 主机名（如
`DNS:mail.example.com, DNS:mail2.example.com`
）；(2) 对于使用通配符证书（
`*.example.com`
）的域，确保 MX 记录指向的主机名在通配符作用域内；(3) 检查 Postfix 的
`myhostname`
是否被 EHLO 响应中的主机名引用，因为发件方可能根据 EHLO 响应中的主机名进行证书主机名验证（取决于发件方实现，RFC 6125 §6.4.4 允许对 SMTP 使用 EHLO 主机名或 MX 主机名进行验证）。

### 4.3 starttls-not-supported：STARTTLS 未启用

当 MTA-STS 策略要求
`mode: enforce`
但接收方 MTA 在端口 25 的 EHLO 响应中未声明
`250-STARTTLS`
时，发件方将记录
`starttls-not-supported`
。复现：

```
$ telnet mail.example.com 25
EHLO sender.example.com
# 检查响应中是否包含 250-STARTTLS
```

修复：在 Postfix 的
`main.cf`
中确保
`smtpd_tls_security_level = may`
（允许但不是必须）或
`= encrypt`
（强制），且证书文件路径正确：

```
smtpd_tls_cert_file = /etc/letsencrypt/live/mail.example.com/fullchain.pem
smtpd_tls_key_file = /etc/letsencrypt/live/mail.example.com/privkey.pem
smtpd_tls_security_level = may
smtpd_tls_loglevel = 1
```

## 5. 报告处理架构与自动化

在生产环境中手动解析每天数千封 TLS-RPT 邮件是不现实的。建议的处理管道：(1) 创建一个专用的收件邮箱（如
`tls-reports@example.com`
），所有 TLS-RPT rua 地址指向此邮箱；(2) 使用 Python
`tlsrpt`
库（pip install tlsrpt）或自定义脚本通过 IMAP 定期拉取邮件，提取
`application/tlsrpt+json`
附件；(3) 将 JSON 数据写入时序数据库（Prometheus + InfluxDB 或 Elasticsearch），通过 Grafana 面板监控 TLS 成功率、故障类型分布和趋势。一个典型的处理脚本骨架：

```
#!/usr/bin/env python3
import imaplib, email, json
from tlsrpt import TLSReport

mail = imaplib.IMAP4_SSL('imap.example.com')
mail.login('tls-reports@example.com', 'password')
mail.select('INBOX')
_, msgs = mail.search(None, 'UNSEEN')
for num in msgs[0].split():
    _, data = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    for part in msg.walk():
        if part.get_content_type() == 'application/tlsrpt+json':
            report = json.loads(part.get_payload(decode=True))
            for policy in report.get('policies', []):
                failures = policy.get('failure-details', [])
                for f in failures:
                    print(f"ALERT: {f['result-type']} "
                          f"from {f['sending-mta-ip']} "
                          f"count={f['failed-session-count']}")
mail.close()
mail.logout()
```

GB/T 37002-2018 第 6.3.4 节要求邮件系统应具备对传输过程中发生的安全事件进行记录和告警的能力——TLS-RPT 报告处理管道直接满足了这一合规要求，提供按日粒度的 SMTP TLS 传输安全审计轨迹。

### 参考文献

1. RFC 8460 — SMTP TLS Reporting (IETF, September 2018). Section 3 TLS-Report Domain TXT Record, Section 4 TLS-Report Format, Section 4.3 Result Types, Section 5 Security Considerations.
2. RFC 8461 — SMTP MTA Strict Transport Security (MTA-STS) (IETF, September 2018). Section 3 MTA-STS Policy, Section 4 Policy Application, Section 5 MTA-STS DNS TXT Record.
3. RFC 7672 — SMTP Security via Opportunistic DANE TLS (IETF, October 2015). Section 3 TLSA Records for SMTP, Section 4 Sender-side Policy Application.
4. RFC 3207 — SMTP Service Extension for Secure SMTP over Transport Layer Security (IETF, February 2002). Section 4 STARTTLS Extension Definition.
5. RFC 6125 — Representation and Verification of Domain-Based Application Service Identity within Internet Public Key Infrastructure Using X.509 (IETF, March 2011). Section 6.4.4 SMTP Identity Verification.
6. RFC 8314 — Cleartext Considered Obsolete: Use of TLS for Email Submission and Access (IETF, January 2018). Section 3.1 Implicit TLS vs STARTTLS.
7. GB/T 37002-2018 — 信息安全技术 电子邮件系统安全技术要求. 第 6.3.4 节 安全审计, 第 6.3.2 节 传输安全.
8. NIST SP 800-52 Rev.2 — Guidelines for the Selection, Configuration, and Use of TLS Implementations (NIST, August 2019). Section 3.4 Certificate Validation.
9. Postfix TLS Readme —
   <https://www.postfix.org/TLS_README.html>
10. python-tlsrpt library —
    <https://pypi.org/project/tlsrpt/>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tls-rpt-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
