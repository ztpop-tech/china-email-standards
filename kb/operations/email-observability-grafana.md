---
title: "基于Grafana/Prometheus的邮件可观测性"
source: "https://ztpop.net/kb/email-observability-grafana.html"
license: CC-BY 4.0
---

# 基于Grafana/Prometheus的邮件可观测性

## 邮件系统的可观测性指标体系

邮件系统的可观测性建设不同于通用Web应用——邮件交付存在异步队列机制，使得传统的请求-响应延迟指标无法直接映射。根据Google SRE手册提出的四大黄金指标（延迟、流量、错误率、饱和度）和CNCF's OpenTelemetry项目的定义，邮件系统需要定义一套领域特定的指标集。邮件投递延迟（Latency）应细分为MTA入站排队时间、MTA到MTA传输时间和MDA存储写入时间三个分段；流量（Traffic）方面需要记录每小时的入站/出站邮件量、连接数和队列深度；错误率（Errors）则涵盖SMTP 5xx永久失败、SPF/DKIM/DMARC认证失败以及退信率；饱和度（Saturation）关注邮件队列磁盘使用率、Dovecot连接线程池使用率和IMAP并发连接数。RFC 8553介绍的Email Authentication Results Reporting可以补充认证层面的可观测性。可观测性建设的最终目标是支持SLO（Service Level Objective）的持续度量——例如：99.9%的邮件在5分钟内完成投递、IMAP登录成功率不低于99.5%。

## Prometheus Exporter部署方案

邮件系统的指标暴露需要多个Prometheus Exporter的配合。为此设计了三个层级的数据采集架构。

* Postfix Exporter：开源项目postfix\_exporter通过解析postfix的showq、mailq和postfix-script等命令输出来暴露队列深度、投递延迟分布和服务进程状态。需注意，postfix\_exporter的默认配置中队列深度是Gauge类型，而投递成功率需要定义为Counter类型以支持Delta计算。
* Dovecot Exporter：dovecot-exporter通过编译Dovecot的stats插件，利用Dovecot的HTTP API（doveadm stats dump）暴露进程池使用率、认证成功/失败计数和IMAP/POP3连接数。此Exporter需要在Dovecot编译时启用--with-stats参数。
* 自定义Blackbox Exporter配置：通过Prometheus的blackbox\_exporter实现对外部SMTP服务的主动拨测（SMTP probe）。该拨测模拟一个完整的SMTP会话（HELO→MAIL FROM→RCPT TO→DATA→QUIT），验证外部MX可达性和TLS握手完整性。

```
# Prometheus scrape_config 核心配置
scrape_configs:
  # Postfix 指标采集
  - job_name: 'postfix'
    static_configs:
      - targets: ['mail01:9154', 'mail02:9154']
    metrics_path: /metrics
    params:
      collections: ['queue', 'uptime', 'connections']

  # Dovecot 指标采集
  - job_name: 'dovecot'
    static_configs:
      - targets: ['mail01:9164', 'mail02:9164']
    metrics_path: /metrics
    params:
      modules: ['auth', 'imap', 'pop3', 'submissions']

  # SMTP 拨测
  - job_name: 'smtp_blackbox'
    metrics_path: /probe
    params:
      module: [smtp_starttls]
    static_configs:
      - targets:
        - mx.ztpop.net:25
        - alt1.aspmx.l.google.com:25
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox:9115  # blackbox-exporter地址
```

## Grafana监控面板设计

一套完整的邮件可观测性Grafana仪表盘应包含四个核心面板群组。第一篇面板群组展示邮件量概览——使用Grafana的时间序列图展示入站/出站邮件量（单位：封/秒），叠加邮件大小的P50/P95/P99分布；第二篇面板集聚焦邮件队列状态——使用Singlestat面板展示当前队列深度，Gauge面板展示队列磁盘使用百分比，并用热力图展示队列等待时间分布；第三篇群组展示认证与安全——以饼图展示SPF/DKIM/DMARC认证结果比例，以状态时间线展示TLS版本分布（TLSv1.0、v1.2、v1.3），并以表格面板展示认证失败率排前十的发源IP；第四篇群组展示SLO达成状态——使用典型的Grafana SLO面板，以燃烧速率指示器（Burn Rate Indicator）展示SLO指标是否有突破风险。每个面板都应关联一个Alertmanager告警规则，例如：队列深度连续3分钟大于1000封触发P1告警、SPF失败率超过1%触发P3告警。

## 告警规则与实践

告警规则设计应采用多窗口燃烧速率方法而非简单的固定阈值。以99.9%的邮件投递SLO为例，推荐使用以下四个窗口的燃烧速率告警规则：1分钟窗口（快速燃烧）当错误率达到0.55%时触发P1告警、5分钟窗口（慢速燃烧）当错误率达到0.27%时触发P2告警、30分钟窗口（中速燃烧）当错误率达到0.09%时触发P3告警、以及6小时窗口（低速燃烧）当错误率达到0.037%时触发P4告警。这种方法避免了对瞬时抖动过度告警，同时确保在SLO窗口结束前有足够时间进行干预。Alertmanager的inhibit\_rules配置可以抑制低级别告警当高级别告警已被触发——例如，当P1的队列死锁告警触发时，自动抑制P3的磁盘使用率告警。此外，Alertmanager应配置多个接收器（receivers）：P1告警发送至电话告警和PagerDuty，P2发送至钉钉/微信机器人，P3和P4则仅记录至Jira ticket。

| 指标名称 | Prometheus类型 | Exporter来源 | SLO目标 | 告警阈值 |
| --- | --- | --- | --- | --- |
| postfix\_queue\_active | Gauge | Postfix Exporter | ≤500 封 | >1000 × 3min |
| dovecot\_auth\_success\_total | Counter | Dovecot Exporter | 成功率 > 99.5% | 成功率 < 97% |
| postfix\_delivery\_duration\_seconds | Histogram | Postfix Exporter | P95 < 60s | P95 > 180s |
| smtp\_probe\_tls\_version{module="smtp\_starttls"} | Gauge | Blackbox Exporter | TLS ≥ 1.2 | TLS < 1.2 |
| postfix\_reject\_count\_total | Counter | Postfix Exporter | 拒绝率 < 5% | 拒绝率 > 15% |
| node\_filesystem\_avail{mountpoint="/var/spool/postfix"} | Gauge | Node Exporter | > 20% | < 10% |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-observability-grafana.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
