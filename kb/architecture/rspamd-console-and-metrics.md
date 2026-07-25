---
title: "Rspamd WebUI 监控面板与 Redis 指标分析"
source: "https://ztpop.net/kb/rspamd-console-and-metrics.html"
license: CC-BY 4.0
---

# Rspamd WebUI 监控面板与 Redis 指标分析

## 概述

Rspamd 是一个高性能垃圾邮件过滤系统，内置 WebUI 监控界面和 Redis 后端双重指标体系。WebUI 在 11334 端口提供实时吞吐率、历史扫描趋势、Top 符号命中频率和连接池状态等面板。Redis 后端则存储所有统计计数器的持久化数据，包括每符号命中次数、Bayesian 分类器词频和模糊哈希缓存。二者配合可帮助运维人员了解过滤系统的运行态势：当日已扫描邮件总量、各动作分布比例、CPU 与内存使用率。

## WebUI 核心面板解读

Rspamd WebUI 的 Throughput Graph 以折线图展示最近时间段内每秒扫描邮件数（p/s）的趋势。Spam/Ham 饼图显示 add header / reject / greylist / no action 的动作分布。Symbols 面板按命中频率降序排列各规则的触发次数——高频命中的规则对应了当前垃圾邮件流的主要特征。History 面板提供可筛选时间窗口的历史统计曲线，支持按动作类型分别查看增长趋势。

```
# Rspamd WebUI 配置
# /etc/rspamd/rspamd.conf.local:
#   worker "controller" { bind_socket = "0.0.0.0:11334"; secure_ip = "192.168.0.0/16"; }

# 通过 API 获取实时统计 JSON
curl -s http://127.0.0.1:11334/stat | python3 -m json.tool | head -80
curl -s http://127.0.0.1:11334/graph?type=throughput | python3 -m json.tool

# 获取各 Symbol 命中计数
curl -s http://127.0.0.1:11334/symbols | python3 -m json.tool | head -50
```

## Redis 后端指标监控

Rspamd 使用 Redis 存储统计计数器、Bayesian 分类器数据、模糊哈希缓存和速率限制状态。Redis INFO 命令可获取内存占用、命中率和键空间分布等核心指标。重点监控 used\_memory\_rss 防止 Redis OOM 导致过滤失效，keyspace\_hits/misses 比率反映缓存效率。Rspamd 的 stat 模块每 10 秒将累积的符号命中次数写入 Redis，通过 redis-cli 查询特定符号的历史计数可发现突发性垃圾邮件活动。

```
# Redis 核心指标
redis-cli INFO stats | grep -E "keyspace|evicted|hit"
redis-cli INFO memory | grep -E "used_memory|maxmemory"

# 查询 Bayesian 分类器统计
redis-cli HGETALL BAYES_HAM
redis-cli HGETALL BAYES_SPAM

# 查询特定符号计数
redis-cli HGETALL S_URIBL_BLACK
redis-cli HGETALL S_DKIM_ALLOW

# 查看所有 Rspamd 前缀的 key 数量
redis-cli --scan --pattern "rs*" | wc -l
```

## 踩坑与排错

Redis 内存不足时 Rspamd 会静默关闭某些模块（Bayesian、速率限制），导致过滤效果突然下降。应设置 maxmemory-policy 为 volatile-lru 而非 noeviction，以避免写入失败引起模块中断。WebUI secure\_ip 白名单配置不当可能导致所有来源都无法访问面板——建议先用 SSH 隧道测试：ssh -L 11334:127.0.0.1:11334 user@server。历史数据量过大会拖慢 WebUI 加载，可通过 history\_redis.conf 中的 nrows 参数限制数据行数。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rspamd-console-and-metrics.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
