---
title: "邮件系统监控与告警体系：Prometheus + Grafana 指标模型与 blackbox_exporter SMTP 探测"
source: "https://ztpop.net/kb/prometheus-grafana-email-monitoring-alert-system.html"
license: CC-BY 4.0
---

# 邮件系统监控与告警体系：Prometheus + Grafana 指标模型与 blackbox_exporter SMTP 探测

## 1. 邮件系统监控的四层架构

邮件系统的可观测性（Observability）建设需要覆盖四个独立的数据映射层——只有四层齐备，才能从"系统在运行"的无感状态走向"系统状态可解释"的工程化运维：

1. **协议层**：SMTP/IMAP/POP3 协议的往返延迟、连接成功率、协议错误响应码分布
2. **队列层**：Active/Deferred/Hold 队列深度变化趋势、邮件在队列中的停留时间
3. **安全层**：SPF/DKIM/DMARC 验证通过率、DNSBL 命中率、认证失败率
4. **资源层**：磁盘 I/O 延迟、网络带宽利用率、MTA 进程的内存和 CPU 消耗

## 2. Prometheus 核心指标体系

以下指标模型基于 Postfix 和 Dovecot 的通用导出器构建。所有延迟指标应记录 P50、P95 和 P99 三个百分位以反映真实性能分布 [1]。

### 2.1 Postfix 队列指标（postfix\_exporter）

```
# /usr/local/bin/postfix_exporter 配置
# 推荐指标清单（Gauge/Histogram 类型）：

# 队列深度（Gauge）：
postfix_queue_active              # active 队列中的邮件数
postfix_queue_deferred            # deferred 队列中的邮件数
postfix_queue_hold                # hold 队列中的邮件数
postfix_queue_incoming            # incoming 队列中的邮件数
postfix_queue_maildrop            # maildrop 队列中的邮件数

# 投递延迟（Histogram，单位秒）：
postfix_delivery_delay_seconds{
  queue="deferred",
  bucket=[1,5,15,30,60,120,300,600,1800,3600]
}

# 队列增长速率（Counter）：
postfix_messages_inbound_total    # 入站邮件总数
postfix_messages_outbound_total   # 出站邮件总数
postfix_messages_bounced_total    # 退信邮件总数
postfix_messages_deferred_total   # 延迟邮件总数
```

### 2.2 Dovecot IMAP 指标（dovecot\_exporter）

```
# Dovecot 指标（通过 stats 插件暴露到 Prometheus 格式）：
dovecot_connections{type="imap"}
dovecot_connections{type="pop3"}
dovecot_connections{type="lmtp"}

dovecot_auth_failures_total{
  method="plain|login|cram-md5",
  reason="invalid_credentials|policy_reject|rate_limit"
}

dovecot_mailbox_size_bytes{
  namespace="INBOX",
  bucket=[1e6,1e7,1e8,1e9,2e9]
}

dovecot_command_latency_seconds{
  command="FETCH|STORE|SEARCH|APPEND",
  bucket=[0.01,0.05,0.1,0.5,1,5]
}
```

### 2.3 Rspamd/SpamAssassin 指标

```
# Rspamd 指标（暴露于 localhost:11334/metrics）：
rspamd_scanned_total{action="reject|greylist|add_header|soft_reject|no_action"}
rspamd_scan_duration_seconds{classifier="bayes|neural|rbl|fuzzy"}
rspamd_memory_bytes{purpose="statistics|config|neural"}
rspamd_connections_active

# SpamAssassin（通过 spamd 统计插件）：
spamassassin_spam_ratio
spamassassin_scan_time_seconds{p99=1.5}
```

## 3. blackbox\_exporter SMTP 探测

Prometheus 社区提供的 `blackbox_exporter` 支持 SMTP 协议级别的主动探测，能够模拟外部 MTA 对目标邮件服务器发起完整的 SMTP 握手流程并检测各阶段的成功率和响应时间 [2]。

### 3.1 blackbox\_exporter SMTP 模块配置

```
# /etc/prometheus/blackbox_exporter/blackbox.yml
modules:
  smtp_tcp:
    prober: tcp
    tcp:
      preferred_ip_protocol: ip4
      query_response:
        - expect: "^220.*ESMTP"
        - send: "EHLO probe.ztpop.net\r\n"
        - expect: "^250-STARTTLS|^250-AUTH"
        - send: "QUIT\r\n"

  smtp_starttls:
    prober: tcp
    tcp:
      tls: true
      tls_config:
        insecure_skip_verify: false
      query_response:
        - expect: "^220.*ESMTP"
        - send: "EHLO probe.ztpop.net\r\n"
        - expect: "250-STARTTLS"
        - send: "STARTTLS\r\n"
        - expect: "^220.*Ready"
        - send: "EHLO probe.ztpop.net\r\n"
        - expect: "^250-AUTH"
        - send: "QUIT\r\n"

  smtp_tls_port_465:
    prober: tcp
    tcp:
      tls: true
      tls_config:
        insecure_skip_verify: false
      query_response:
        - send: "EHLO probe.ztpop.net\r\n"
        - expect: "^250-AUTH LOGIN"
        - send: "QUIT\r\n"
```

### 3.2 Prometheus 抓取配置

```
# prometheus.yml - blackbox_exporter 目标配置
scrape_configs:
  - job_name: 'smtp_blackbox'
    metrics_path: /probe
    params:
      module: [smtp_tcp]
    static_configs:
      - targets:
        - 'mx.ztpop.net:25'
        - 'mx2.ztpop.net:25'
        - 'smtp.example.org:25'
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115  # blackbox_exporter 监听地址

  # STARTTLS 探测（与 TCP 探测分开以获得独立的指标集）
  - job_name: 'smtp_starttls_blackbox'
    metrics_path: /probe
    params:
      module: [smtp_starttls]
    static_configs:
      - targets:
        - 'mx.ztpop.net:25'
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115
```

## 4. 告警规则设计

告警规则的设计应遵循"减少重复告警、聚焦业务影响"的原则。以下告警规则集覆盖了邮件系统的四个核心风险面 [3]。

### 4.1 Prometheus 告警规则

```
# /etc/prometheus/rules/mail_alerts.yml
groups:
  - name: mail_queue
    rules:
      # 队列深度异常
      - alert: PostfixQueueDeep
        expr: postfix_queue_deferred > 1000
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Deferred queue > 1000 for 15 minutes"
          description: "当前 deferred 队列深度 {{ $value }}，正常应 < 1000"

      - alert: PostfixQueueCritical
        expr: postfix_queue_deferred > 10000
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Deferred queue > 10000"
          description: "延迟队列深度 {{ $value }}，需立即检查投递链路"

  - name: mail_latency
    rules:
      - alert: SMTPDeliveryLatencyHigh
        expr: histogram_quantile(0.99, rate(postfix_delivery_delay_seconds_bucket[5m])) > 300
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "P99 delivery latency > 5 minutes"
          description: "P99 投递延迟 {{ $value }}s，超过 300s 阈值"

  - name: mail_auth
    rules:
      - alert: HighAuthFailureRate
        expr: rate(dovecot_auth_failures_total[5m]) / rate(dovecot_connections[5m]) > 0.3
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "认证失败率 > 30%"
          description: "{{ $labels.instance }} 认证失败率 {{ $value | humanizePercentage }}"

      - alert: BruteforceDetection
        expr: rate(dovecot_auth_failures_total{reason="invalid_credentials"}[5m]) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "密码暴力破解检测"
          description: "5分钟内认证失败次数 > 10 次/秒"

  - name: mail_bounce
    rules:
      - alert: BounceRateElevated
        expr: rate(postfix_messages_bounced_total[30m]) / rate(postfix_messages_outbound_total[30m]) > 0.1
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "退信率大于 10%"
          description: "最近 30 分钟退信率 {{ $value | humanizePercentage }}"

  - name: mail_blackbox
    rules:
      - alert: SMTPProbeFailed
        expr: probe_success{job="smtp_blackbox"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "SMTP 探测失败"
          description: "黑盒探测 {{ $labels.instance }} 失败"

      - alert: SMTPLivenessProbeSlow
        expr: probe_duration_seconds{job="smtp_tls_blackbox"} > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "SMTP TLS 握手超过 10 秒"
          description: "{{ $labels.instance }} TLS 握手耗时 {{ $value }}s"

  - name: mail_resource
    rules:
      - alert: DiskIOHigh
        expr: rate(node_disk_io_time_seconds_total{device=~"sd[a-z]"}[5m]) > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "磁盘 I/O 利用率 > 90%"
          description: "{{ $labels.device }} I/O 利用率 {{ $value | humanizePercentage }}"
```

## 5. Grafana 仪表盘设计

### 5.1 核心仪表盘面板布局

推荐构建三个独立仪表盘以区分不同运维场景的监控视角：

5.1 Grafana 仪表盘

| 仪表盘名称 | 目标用户 | 核心面板 |
| 邮件系统概览 | 值班运维 | 邮件吞吐量时间序列、队列深度热力图、P95 投递延迟、退信率趋势、SMTP 探测状态表 |
| 邮件投递深度诊断 | 邮件运维专员 | 每个域名级别的投递延迟和退信率、DNSBL 命中分布、TLS 加密率、各 MTA 进程连接数 |
| 邮件安全态势 | 安全运维 | SPF/DKIM/DMARC 验证结果分布、认证失败地理分布、暴力破解热力图、Rspamd 扫描评分分布 |

### 5.2 关键面板 PromQL 示例

```
# 面板 1：邮件吞吐（邮件/秒）
rate(postfix_messages_inbound_total[5m])

# 面板 2：Deferred 队列深度
avg(postfix_queue_deferred)

# 面板 3：P99 投递延迟
histogram_quantile(0.99,
  sum(rate(postfix_delivery_delay_seconds_bucket[5m])) by (le))

# 面板 4：退信率
rate(postfix_messages_bounced_total[30m])
  / rate(postfix_messages_outbound_total[30m])

# 面板 5：认证失败趋势（5 分钟内的失败次数）
rate(dovecot_auth_failures_total[5m])

# 面板 6：SMTP 探测延迟（P95）
histogram_quantile(0.95,
  rate(probe_duration_seconds{job="smtp_blackbox"}[5m]))

# 面板 7：TLS 加密比例
avg(rate(probe_duration_seconds{job="smtp_starttls_blackbox"}[5m]))
  / on(instance) group_left
avg(rate(probe_duration_seconds{job="smtp_blackbox"}[5m]))
```

## 6. SLO 设计与告警疲劳控制

SLO（Service Level Objective）是监控体系从"阈值触发"到"服务质量可度量"的关键跃升。邮件系统的典型 SLO 定义：

```
# SLO 定义示例（基于 30 天滑动窗口）

# 投递延迟 SLO（P95 < 5 分钟，99.9%）
- 目标: 99.9% 的邮件在 5 分钟内完成投递
- 测量: (postfix_delivery_delay_seconds{le="300"} 的计数) / 总数
- 告警: 当 SLO 达成率低于 99.5% 时发出 P1 告警

# SMTP 可用性 SLO（服务可用率 > 99.95%）
- 目标: SMTP 端口探测成功率 > 99.95%
- 测量: (probe_success{job="smtp_blackbox"} == 1) / 总探测次数
- 告警: 当任意 15 分钟窗口内可用率低于 99% 时发出 P1 告警

# 认证成功 SLO（认证成功率 > 99%）
- 目标: 99% 以上的 IMAP/POP3/SMTP 认证请求成功
- 测量: 1 - rate(dovecot_auth_failures_total[5m]) / rate(dovecot_connections[5m])
- 告警: 低于 95% 持续 10 分钟时发出 P2 告警
```

告警疲劳控制推荐：设置告警冷却时间（`repeat_interval: 4h`），同一高优先级告警 4 小时内不再重复发送。同时配合 `Alertmanager` 的 `inhibit_rules` 抑制机制——当 PostfixQueueCritical 告警触发时，自动抑制同一实例上由 PostfixQueueDeep 触发的所有 warning 级告警。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/prometheus-grafana-email-monitoring-alert-system.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
