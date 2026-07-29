---
title: "Postfix Log 分析与报警体系搭建"
source: "https://ztpop.net/kb/postfix-log-analysis-alerting.html"
license: CC-BY 4.0
---

# Postfix Log 分析与报警体系搭建

Postfix 日志是邮件运维的核心数据源。本文从日志结构解析出发，覆盖 pflogsumm、logwatch、fail2ban 和 ELK 集成，提供 key 日志模式识别方法和报警阈值设计原则。

## Postfix 日志结构

Postfix 所有日志通过 syslog 写入，典型条目：

```
Jul 24 10:15:32 mail postfix/smtpd[12345]: 4XYZ123456: client=unknown[203.0.113.50], sasl_method=LOGIN, sasl_username=user@example.com
Jul 24 10:15:33 mail postfix/cleanup[12346]: 4XYZ123456: message-id=<202607241015.ABCDEF@example.com>
Jul 24 10:15:34 mail postfix/qmgr[12347]: 4XYZ123456: from=, size=20480, nrcpt=1 (queue active)
Jul 24 10:15:35 mail postfix/smtp[12348]: 4XYZ123456: to=, relay=mx.recipient.com[198.51.100.25]:25, delay=1.2, delays=0.1/0.3/0.5/0.3, dsn=2.0.0, status=sent (250 OK)
```

关键字段解析：

Postfix 日志核心字段

| 日志源 | 进程 | 动作 | 关键信息 |
| --- | --- | --- | --- |
| smtpd | 接收连接 | client=, sasl\_method=, relay= | IP、认证方法、发件人 |
| cleanup | 邮件清洗 | message-id=, headers-from= | Message-ID、信头发件人 |
| qmgr | 队列管理 | from=, size=, nrcpt=, queue active/deferred | 发件人、大小、接收人数 |
| smtp | 出站投递 | to=, relay=, delay=, delays=, dsn=, status= | 目标地址、中继、延迟、状态 |
| bounce | 退信生成 | 原 QueueID: status=bounced | 退信原因 |
| anvil | 速率限制 | statistics: max rate | 连接速率、异常峰值 |

## pflogsumm 日报生成

```
# 安装
apt install pflogsumm  # 或从源码安装
yum install postfix-perl-scripts

# 每日报告
pflogsumm -d today /var/log/mail.log | mail -s "Postfix Daily Report $(date +%F)" ops@example.com

# 日报关键指标解读
# 正常范围参考值：
# deferred: < 5% of total deliveries
# bounced:  < 3% of total deliveries  
# rejected: < 10% of total connections
# delay avg: < 5s  (连接建立到完成的时间)
```

## logwatch 集成

```
# logwatch 配置
# /etc/logwatch/conf/logwatch.conf
MailTo = ops@example.com
Range = yesterday
Detail = High
Service = postfix

# 自定义 Postfix 过滤器
# /etc/logwatch/scripts/services/postfix
# 已内置在 logwatch 中，通过 logwatch --service postfix 启用

# cron 每日自动发送
0 7 * * * /usr/sbin/logwatch --service postfix --output mail
```

## fail2ban 配置

```
# /etc/fail2ban/jail.local
[postfix-auth]
enabled  = true
port     = smtp,ssmtp,submission
filter   = postfix-auth
logpath  = /var/log/mail.log
maxretry = 5
findtime = 600   # 10 分钟内
bantime  = 1800  # 封禁 30 分钟

[postfix-rbl]
enabled  = true
port     = smtp,ssmtp,submission
filter   = postfix-rbl
logpath  = /var/log/mail.log
maxretry = 1
findtime = 86400
bantime  = 86400

# /etc/fail2ban/filter.d/postfix-auth.conf
[Definition]
failregex = ^%(__prefix_line)swarning: .* SASL authentication failed.*$
            ^%(__prefix_line)swarning: .* SASL PLAIN authentication failed.*$

# /etc/fail2ban/filter.d/postfix-rbl.conf
[Definition]
failregex = ^%(__prefix_line)s.* reject: RCPT from .*: 554 5\.7\.1 Service unavailable.*$
```

## ELK 集成方案

```
# Filebeat 配置 (/etc/filebeat/filebeat.yml)
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/mail.log
    - /var/log/mail.err
    - /var/log/mail.warn
  fields:
    service: postfix
  multiline:
    pattern: '^[A-Z][a-z]{2}\s+\d+'
    negate: true
    match: after

output.elasticsearch:
  hosts: ["https://elastic:9200"]
  username: "filebeat"
  password: "${ES_PWD}"

# Logstash grok 模式 (/etc/logstash/conf.d/postfix.conf)
filter {
  if [service] == "postfix" {
    grok {
      match => { "message" => "%{SYSLOGTIMESTAMP:timestamp} %{SYSLOGHOST:hostname}         %{WORD:process}\[%{NUMBER:pid}\]: %{GREEDYDATA:postfix_msg}" }
    }
    if [postfix_msg] =~ /delay=/ {
      grok {
        match => { "postfix_msg" => "delay=%{NUMBER:delay_total},           delays=%{NUMBER:delay_before_qmgr}/%{NUMBER:delay_qmgr}/%{NUMBER:delay_conn}/%{NUMBER:delay_smtp}" }
      }
    }
  }
}
```

## 关键日志模式与报警阈值

报警规则设计

| 日志模式 | 触发条件 | 严重级别 | 响应动作 |
| --- | --- | --- | --- |
| deferred（队列延迟） | deferred 队列超过 100 封持续 >30 分钟 | ⚠️ Warning | qshape 检查被拒域；检查 DNS 解析 |
| reject（连接拒绝） | 每分钟 reject 数 > 50 | ⚠️ Warning | 检查是否被攻击或策略过严 |
| bounce（退信） | 某目标域退信率 > 20% | 🔴 Critical | 检查目标域可达性；确认是否被列入黑名单 |
| delay avg（平均延迟） | avg delay > 30s 持续 15 分钟 | 🔴 Critical | 检查出站连接、DANE 验证；可能需要降级 |
| SASL auth fail | 同一 IP 认证失败 > 5 次/10分钟 | 🔴 Critical | fail2ban 封禁；检查是否是暴力破解 |
| connection rate | 超过基线 3σ（标准差） | ⚠️ Warning | 检查是否被 DDoS 或合法流量暴增 |
| TLS verify fail | 证书验证失败 > 10 次/小时 | ⚠️ Warning | 检查对方 MTA 证书；可能需要更新 CA bundle |

## 自动化报警脚本

```
#!/bin/bash
# /usr/local/bin/postfix-alert.sh

THRESHOLD_DEFERRED=100
THRESHOLD_BOUNCE_PCT=20
CHECK_INTERVAL=600

# 检查 deferred 队列
DEFERRED=$(mailq | grep -c "^[A-F0-9]")
if [ "$DEFERRED" -gt "$THRESHOLD_DEFERRED" ]; then
    echo "Deferred queue: $DEFERRED (threshold: $THRESHOLD_DEFERRED)" |         mail -s "⚠️ Postfix Queue Alert" ops@example.com
    qshape deferred | head -20 | mail -s "Top deferred domains" ops@example.com
fi

# 检查出站 delay 异常
pflogsumm -d today --verbose-deliveries /var/log/mail.log |     awk 'NR>6 {if($7>30) print}' |     mail -s "⚠️ High delay deliveries" ops@example.com

# cron: */10 * * * * /usr/local/bin/postfix-alert.sh
```

### 核心要点

* Postfix 日志字段呈现的是完整的邮件生命周期——从连接到投递每一步都可追溯
* pflogsumm 提供每日摘要；logwatch 提供日记级别分析；fail2ban 提供实时防御
* ELK 集成应以 delay、reject、bounce 为核心，配合 Grok 解析实现结构化搜索
* 报警阈值应基于历史基线而非绝对数值——建议运行 30 天确定基线后再设定 3σ 阈值
* 参考标准：RFC 5321（SMTP 状态码）、RFC 3463（增强状态码）、RFC 3461（DSN）

本站技术文章采用 CC-BY 4.0 许可，可自由引用，仅需标注来源 [ztpop.net](https://www.ztpop.net)。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-log-analysis-alerting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
