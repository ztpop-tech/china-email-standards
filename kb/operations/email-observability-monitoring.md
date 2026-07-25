---
title: "邮件系统可观测性：监控、告警与 SLO 设计"
source: "https://ztpop.net/kb/email-observability-monitoring.html"
license: CC-BY 4.0
---

# 邮件系统可观测性：监控、告警与 SLO 设计

## 一、概述

邮件系统作为企业关键通信基础设施，其可靠性直接影响业务连续性。传统运维依赖日志巡检与被动告警，难以在故障发生前识别劣化趋势。可观测性（Observability）通过度量（Metrics）、日志（Logging）、追踪（Tracing）三大支柱，为邮件基础设施提供系统性的状态洞察能力。本文以 Prometheus 生态为核心，论述邮件系统可观测性栈的工程构建方法，涵盖协议层指标采集、MTA 队列监控、延迟分布分析及 SLO 驱动的告警体系。

邮件系统的可观测性需求与通用 Web 服务存在显著差异：SMTP 协议层存在多跳转发延迟累积效应；IMAP/POP3 连接为长连接模式，会话复用率直接影响用户体验；邮件队列深度是前置指标，可提前数分钟预警投递瓶颈。这些特性要求监控方案具备协议感知能力，而非简单套用 HTTP 服务监控模板。

## 二、四大黄金信号在邮件系统中的映射

Google SRE 方法论提出的四大黄金信号——延迟（Latency）、流量（Traffic）、错误（Errors）、饱和度（Saturation）——在邮件系统中需要协议层适配。以下逐一分析其映射方式与关键指标。

### 2.1 延迟（Latency）

邮件系统中的延迟为多维度概念，需区分以下层次：

* **SMTP 连接建立延迟**：从 TCP 三次握手完成到收到 220 就绪响应的时间。正常值 < 200ms，若持续 > 1s 则需排查反向 DNS 查询或 Greylisting 策略。
* **端到端投递延迟**：从邮件提交到最终邮箱落盘的时间，包含队列等待、病毒扫描、内容过滤各阶段。
* **邮件传输延迟**：单个 SMTP 会话中 MAIL FROM 到 250 OK 的时间，反映远端 MTA 接收速率。
* **IMAP/POP3 响应延迟**：SELECT、FETCH、UID SEARCH 等命令的响应时间，直接影响客户端体验。

延迟采集的核心工具是 mtail——从 MTA 日志中实时提取结构化指标的轻量级解析器。以下为 Postfix 日志的 mtail 规则示例，用于计算 SMTP 连接延迟的 p50/p90/p99 分布：

```
# mtail: /etc/mtail/postfix_smtp_latency.mtail
counter smtp_conn_total by status
gauge smtp_conn_delay by quantile

/connect to (.+)\[([^\]]+)\]:25: (.+)/ {
  smtp_conn_total[$3]++
}

/delay=([0-9.]+), delays=/ {
  $delay = strptime($1, "s")
  smtp_conn_delay["p50"] = histogram($delay)
}
```

Grafana 面板中，PromQL 查询可直接计算延迟分位数：

```
# p50 SMTP 连接延迟（1分钟窗口）
histogram_quantile(0.50, rate(smtp_conn_delay_bucket[1m]))

# p99 SMTP 端到端投递延迟
histogram_quantile(0.99, rate(mail_delivery_duration_seconds_bucket[5m]))
```

### 2.2 流量（Traffic）

邮件流量指标反映系统负载水平：

* **SMTP 并发连接数**：通过 `smtpd` 进程数或 `ss -antp | grep :25 | wc -l` 获取。Postfix `default_process_limit` 默认为 100，接近上限时应扩容或启用连接缓存。
* **邮件接收速率**：每分钟接收的邮件数量，按发件域分组可识别突发流量来源。
* **队列消息速率**：active/deferred/bounce 队列的出入速率，反映 MTA 吞吐能力。

Prometheus node\_exporter 配合自定义 textfile collector 可采集这些指标：

```
# /var/lib/node_exporter/textfile_collector/mailq.prom
# HELP postfix_queue_size Postfix queue message count by queue
# TYPE postfix_queue_size gauge
postfix_queue_size{queue="active"} 47
postfix_queue_size{queue="deferred"} 312
postfix_queue_size{queue="hold"} 0
postfix_queue_size{queue="incoming"} 128
```

采集脚本使用 `postqueue -p` 或直接读取 `/var/spool/postfix/` 目录下各队列的文件数量，通过 cron 每分钟更新一次。

### 2.3 错误（Errors）

邮件系统的错误维度包括：

* **SMTP 临时失败率（4xx）**：通常由 Greylisting、收件方限速或临时 DNS 故障引起。
* **SMTP 永久失败率（5xx）**：用户不存在、域名无效或反垃圾策略拦截，需区分自身系统错误与外部拒绝。
* **认证失败率**：SASL 认证失败的占比，突然升高可能表示暴力破解攻击。
* **投递失败（Bounce）率**：在合理范围内（< 5%）属正常，突然升高需排查 DNS 或 IP 声誉问题。

从 Postfix 日志中提取错误率的 mtail 规则：

```
counter smtp_status_total by status_code, relay

/status=sent \(250/ {
  smtp_status_total["250"]++
}

/status=deferred \(4[0-9][0-9]/ {
  /\(4([0-9][0-9])/
  smtp_status_total["4" + $1]++
}

/status=bounced \(5/ {
  /\(5([0-9][0-9])/
  smtp_status_total["5" + $1]++
}
```

### 2.4 饱和度（Saturation）

饱和度衡量资源使用接近容量上限的程度：

* **CPU 饱和度**：通过 `node_cpu_seconds_total` 计算 CPU 使用率，并监控 load average 与 CPU 核心数的比值。
* **内存饱和度**：监控可用内存与 swap 使用量，Dovecot 的 `mail_cache` 和索引在内存不足时性能急剧退化。
* **磁盘 IOPS 饱和度**：Maildir 格式下小文件 IO 密集，`node_disk_io_time_seconds_total` 反映磁盘忙碌程度。
* **连接池饱和度**：Dovecot 的 `mail_max_userip_connections`（默认 10）和 Postfix 的 `smtpd_client_connection_count_limit`。

## 三、邮件队列深度监控与告警

邮件队列深度是邮件系统健康状况的最敏感前置指标。当 active 队列持续增长时，表明 MTA 发送速率低于邮件到达速率；deferred 队列增长则意味着远端投递存在系统性障碍。

### 3.1 队列监控架构

推荐的采集链路为：cron 每分钟执行 `mailq` 汇总脚本 → 写入 node\_exporter textfile → Prometheus 拉取 → Grafana 可视化。脚本示例：

```
#!/bin/bash
# /usr/local/bin/mailq-metrics.sh
ACTIVE=$(find /var/spool/postfix/active -type f 2>/dev/null | wc -l)
DEFERRED=$(find /var/spool/postfix/deferred -type f 2>/dev/null | wc -l)
INCOMING=$(find /var/spool/postfix/incoming -type f 2>/dev/null | wc -l)
HOLD=$(find /var/spool/postfix/hold -type f 2>/dev/null | wc -l)

cat > /var/lib/node_exporter/textfile_collector/mailq.prom << EOF
# HELP postfix_queue_size Postfix queue sizes
# TYPE postfix_queue_size gauge
postfix_queue_size{queue="active"} $ACTIVE
postfix_queue_size{queue="deferred"} $DEFERRED
postfix_queue_size{queue="incoming"} $INCOMING
postfix_queue_size{queue="hold"} $HOLD
EOF
```

### 3.2 告警规则设计

告警应基于运行趋势而非静态阈值。以下为 Prometheus alerting rules 示例：

```
groups:
- name: mail_queue
  rules:
  - alert: MailQueueGrowing
    expr: deriv(postfix_queue_size{queue="active"}[30m]) > 10
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "Active queue growing at {{ $value }}/min"
      description: "Postfix active queue has been growing for 15+ minutes. Current size: {{ with query \"postfix_queue_size{queue='active'}\" }}{{ . | first | value }}{{ end }}"

  - alert: MailQueueBurst
    expr: postfix_queue_size{queue="active"} > 1000
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Active queue exceeds 1000 messages"
      description: "Unexpected mail queue depth. Check deferred queue and SMTP connectivity."
```

## 四、Dovecot 连接池监控

Dovecot 的 IMAP/POP3 服务端连接管理直接影响终端用户体验。关键监控维度包括：

* **活动连接数**：通过 `doveadm who` 统计或解析 Dovecot 日志中的 LOGIN/LOGOUT 事件。
* **认证延迟**：SASL 认证耗时，PAM/LDAP 后端性能瓶颈的指示器。
* **邮箱打开时间**：`maildir_very_dirty_syncs` 开启时加快但可能丢元数据，关闭时安全但大邮箱打开慢。
* **索引命中率**：Dovecot 的 FTS（全文搜索）索引缓存效率。

Dovecot 从 v2.2 开始内置 stats 模块，可直接暴露 Prometheus 格式指标。在 `/etc/dovecot/conf.d/10-metrics.conf` 中配置：

```
metric imap_commands {
  event_name = imap_command_finished
  filter {
    # 统计所有 IMAP 命令的耗时分布
  }
  fields = cmd_name duration
}

metric http_server {
  listener {
    path = /var/run/dovecot/metrics
    mode = 0666
  }
}
```

通过 Prometheus textfile collector 读取该 Unix domain socket 即可集成。

## 五、送达率 SLO 设计与燃烧率告警

服务等级目标（Service Level Objective）是连接系统监控与业务承诺的关键桥梁。对于邮件系统，建议定义以下 SLO：

### 5.1 核心 SLO 指标

5.1 核心 SLO 指标

| SLO 指标 | 目标值 | 测量窗口 | 计算方式 |
| 邮件送达率 | ≥ 99.9% | 30 天滑动窗口 | 成功投递数 / 总提交数 |
| 首次投递成功率 | ≥ 95% | 7 天滑动窗口 | 首次尝试即成功的投递占比 |
| SMTP 服务可用性 | ≥ 99.95% | 30 天滑动窗口 | SMTP 端口可连接时间占比 |
| IMAP 服务可用性 | ≥ 99.9% | 30 天滑动窗口 | IMAP 端口可认证时间占比 |

### 5.2 燃烧率告警

Google SRE Book 第 5 章提出的燃烧率（Burn Rate）概念——即错误预算消耗速率——适用于邮件系统的 SLO 告警设计。以 99.9% 送达率 SLO 为例，30 天错误预算为 43.2 分钟（30 × 24 × 60 × 0.001）。燃烧率告警规则：

```
# 1小时内消耗了2%的错误预算（约52秒不可用）→ 页面告警
- alert: DeliveryBurnRateHigh
  expr: (sum(rate(mail_delivery_failures_total[1h])) / sum(rate(mail_delivery_attempts_total[1h]))) > (0.001 * 14.4)
  for: 5m
  labels:
    severity: page
  annotations:
    summary: "Delivery error budget burning at {{ $value | humanizePercentage }}"

# 6小时内消耗了5%的错误预算 → 工单告警
- alert: DeliveryBurnRateMedium
  expr: (sum(rate(mail_delivery_failures_total[6h])) / sum(rate(mail_delivery_attempts_total[6h]))) > (0.001 * 2)
  for: 10m
  labels:
    severity: ticket
```

## 六、Grafana 仪表板设计

推荐的仪表板布局分为四个区域：

**第一行——服务概览**：三个 Stat Panel 显示送达率（当前值 vs SLO）、活跃连接数、队列深度；两个 Time Series Panel 显示 24h 邮件流量趋势和延迟热力图。

**第二行——协议层指标**：SMTP 延迟分位数（p50/p90/p99）、SMTP 状态码分布（2xx/4xx/5xx 堆叠）、IMAP 响应时间、POP3 并发会话数。

**第三行——队列与资源**：active/deferred 队列趋势、磁盘 IOPS、CPU 负载、内存使用率。

**第四行——告警状态**：当前活跃告警列表、燃烧率仪表盘。

建议使用 Grafana Dashboard Provisioning 将仪表板纳入版本控制，可通过 JSON 文件自动部署：

```
# /etc/grafana/provisioning/dashboards/mail.yaml
apiVersion: 1
providers:
- name: 'mail-infra'
  orgId: 1
  folder: 'Mail'
  type: file
  disableDeletion: true
  updateIntervalSeconds: 60
  options:
    path: /etc/grafana/provisioning/dashboards/json
```

## 七、日志聚合与链路追踪

Loki + Promtail 可实现邮件系统日志的结构化聚合。Postfix 与 Dovecot 的 syslog 输出通过 Promtail 采集并打上标签：

```
# /etc/promtail/config.yml
scrape_configs:
- job_name: postfix
  syslog:
    listen_address: 0.0.0.0:1514
    listen_protocol: tcp
    idle_timeout: 60s
    label_structured_data: true
  relabel_configs:
  - source_labels: ['__syslog_message_hostname']
    target_label: 'host'
  - source_labels: ['__syslog_message_app_name']
    target_label: 'service'
```

对于分布式邮件系统（多 MTA 节点），OpenTelemetry 可用于追踪一封邮件从 SMTP 入口到最终投递的完整路径，但需注意邮件传输的异步特性——SMTP 转发不是同步 RPC 调用，踪迹上下文无法通过协议头天然传递。实践中可在日志中嵌入 trace\_id 实现跨节点的松耦合关联。

## 八、常见日志分析示例

运维中可通过以下 Loki LogQL 查询快速定位问题：

```
# 过去1小时内 SMTP 5xx 错误最多发件IP Top 10
topk(10, sum by (client_ip) (count_over_time(
  {service="postfix/smtpd"} |= "status=reject" [1h]
)))

# 某域名投递延迟超过10秒的邮件数量趋势
sum(rate(
  {service="postfix/smtp"} |~ "delay=[1-9][0-9]+\\." | pattern `<_> to=<domain>`
  | domain="example.com" [5m]
))

# Dovecot IMAP 登录失败事件（可能为暴力破解）
sum by (user) (count_over_time(
  {service="dovecot"} |= "auth failed" [10m]
)) > 5
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-observability-monitoring.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
