---
title: "MTA-STS 故障排查手册"
source: "https://ztpop.net/kb/mta-sts-troubleshooting.html"
license: CC-BY 4.0
---

# MTA-STS 故障排查手册

## MTA-STS协议概要与故障定位框架

MTA-STS（SMTP MTA Strict Transport Security）由RFC 8461定义，是一种基于策略文件的安全机制，允许邮件发送方通过HTTPS获取接收域的强制TLS策略。MTA-STS的核心组件包括：DNS TXT记录（\_mta-sts.{domain}）、HTTPS上的策略文件（https://mta-sts.{domain}/.well-known/mta-sts.txt）和缓存机制。

故障排查需从三个层面展开：DNS解析环节、HTTPS策略获取环节、SMTP TLS连接环节。每个环节都有独特的故障模式和诊断方法。

## DNS记录故障排查

### 记录缺失或配置错误

MTA-STS的DNS记录位于\_mta-sts.{domain}的TXT记录中，格式为v=STSv1; id=xxxxxxxx;。最常见的三种故障：

* ID值不匹配：id标签的值必须与策略文件中的id字段完全一致（包括大小写），每次策略更新时同步修改
* TXT记录格式错误：缺少引号或包含无效字符
* TTL设置过短：建议不少于3600秒，过短的TTL会导致频繁的DNS查询增加延迟

```
# 验证DNS记录
$ nslookup -type=TXT _mta-sts.example.com
# 预期输出：
_mta-sts.example.com text = "v=STSv1; id=20250730T120000;"

# dig返回完整响应
$ dig TXT _mta-sts.example.com +short
"v=STSv1; id=20250730T120000;"

# 常见错误：缺少分号结束
# 错误："v=STSv1; id=1234"  ← 缺少尾部分号
# 正确："v=STSv1; id=1234;"   ← 协议要求!
```

### 缓存与传播问题

DNS记录的更新时间取决于TTL值。MTA-STS缓存策略独立于DNS缓存——RFC 8461 §3.3规定发送方可以在max\_age范围内缓存策略。若DNS记录已更新但策略文件未同步，发送方将继续使用旧ID对应的策略直至缓存过期。

## HTTPS策略文件故障排查

### 策略文件获取失败

策略文件位于https://mta-sts.{domain}/.well-known/mta-sts.txt。常见失败原因包括：HTTPS证书到期、证书与实际域名不匹配、HTTP返回非200状态码、或.mta-sts子域名不存在。

```
$ curl -sI https://mta-sts.example.com/.well-known/mta-sts.txt
# 预期：HTTP/2 200
# 错误：HTTP/2 404 — 文件不存在或路径错误
# 错误：HTTP/2 301 — 重定向（MTA-STS禁止重定向!）

$ openssl s_client -connect mta-sts.example.com:443 -servername mta-sts.example.com
# 检查证书链
# Subject: CN = mta-sts.example.com
# 证书必须与.mta-sts子域名完全匹配（RFC 8461 §3.2）
```

### 策略内容验证

```
# 有效的策略文件示例
version: STSv1
mode: enforce
mx: mail1.example.com
mx: *.mx.example.net
mx: mail.backup.com
max_age: 86400

# 常见错误：
# 1. MX字段与DNS MX记录不一致
# 2. mode: testing 但期望 enforce
# 3. max_age超出RFC上限（不超过31557600秒/365天）
```

RFC 8461 §4.1规定策略文件必须使用“application/text“ MIME类型，文件编码为UTF-8。每行使用key: value格式，冒号后必须跟一个空格。MX字段支持通配符（\*），但\*.example.com仅匹配一个标签层级的子域名。

## SMTP TLS连接故障排查

### 证书验证失败

MTA-STS的证书验证规则基于RFC 6125。典型失败原因：

* 证书CN/SAN与策略文件中的MX主机名不匹配
* 证书链不完整（缺少中间CA证书）
* 证书已过期或尚未生效
* 支持IP地址的MX时证书未包含通配符或正确SAN

### testing模式下不强制TLS

RFC 8461 §3.2定义了三种mode：testing（仅记录，不强制执行TLS）、enforce（强制执行TLS）和none（禁用MTA-STS）。testing模式是故障排查的最佳起点——在此模式下即使TLS连接失败，邮件也会降级为明文发送，不会丢失。在确认TLS链路正常后切换到enforce。

## MTA-STS与DANE的互操作性问题

同一域可以同时部署MTA-STS和DANE TLSA记录（RFC 7672）。当两者并存时，DANE具有更高的优先级——因为DANE根植于DNSSEC，安全性更强。但由于DANE要求完整的DNSSEC部署，大多数域仅部署MTA-STS。

联合部署时的潜在冲突：

* MTA-STS策略中列出的MX主机与DANE TLSA记录的端口/协议不匹配
* DANE要求STARTTLS（端口25）时强制证书验证不同
* 策略缓存过期时间不同步导致过渡期不确定性

故障排查工具的实用命令：

```
# 使用smtp-sts工具检查完整MTA-STS状态
$ python3 -m smtp_sts check example.com

# 手动模拟MTA-STS验证流程
$ openssl s_client -connect mail.example.com:25 -starttls smtp
# 查看服务器返回的STARTTLS支持声明
# 从EHLO响应中检查是否返回STARTTLS
```

建议运维团队在启用enforce模式前，至少运行testing模式观察90天（覆盖最长max\_age周期的两倍以上），确保所有依赖链路的TLS配置稳定可靠。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mta-sts-troubleshooting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
