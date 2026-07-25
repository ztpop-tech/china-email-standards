---
title: "邮件投递追踪：Received 头部解析与 DSN 投递状态通知"
source: "https://ztpop.net/kb/email-delivery-tracking.html"
license: CC-BY 4.0
---

# 邮件投递追踪：Received 头部解析与 DSN 投递状态通知

## 概述

邮件在互联网上传输时经过多个 MTA 中转，每次中转都会在邮件头部追加一个 Received 字段。从最顶端的目标 MTA 向下读取到最底端的发件源 MTA，即完整还原了邮件的投递路径。每个 Received 头部包含 from（上一跳主机名/IP）、by（本跳主机名）、for（收件地址）和分号后时间戳，构成可审计的端到端传输日志。配合 DSN 机制，发件方可获取投递成功、延迟或失败的结构化通知。

## Received 头部逐跳解析

RFC 5321 要求每个 SMTP 中继在转发前必须新增一个 Received 头部字段。解析时从邮件顶端开始向下阅读：第一行是目标 MTA 接收记录，最后一行是发件源 MTA 发送记录。每跳之间的时间差反映了该跳的传输延迟与队列等待时间。如果中间出现较大时间跳变（如超过 300 秒），通常意味着该跳 MTA 进行了 greylisting 或队列积压。比较相邻 Received 字段的 from 和 by IP/主机名可检测伪造路径。

```
# 提取邮件全文的 Received 头部链
cat eml_sample.txt | grep "^Received:" | tac
cat eml_sample.txt | grep "^Received:"

# 提取每跳 IP 和时间
grep "^Received:" eml_sample.txt | grep -oP '\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}' | head -10
grep "^Received:" eml_sample.txt | grep -oP ';.*$' | head -10

# 统计总跳数
grep -c "^Received:" eml_sample.txt
```

## DSN 投递状态通知与增强状态码

RFC 3464 定义了 DSN 的 MIME 结构，核心是一个 message/delivery-status 子部分，包含 per-recipient 的投递状态。关键字段包括 Action（failed/delayed/delivered/relayed）、Status（RFC 3463 增强状态码，格式 X.XXX）和 Remote-MTA。增强状态码第一位表示类别（2=成功、4=临时失败、5=永久失败），第二位表示主题（1=寻址、2=邮箱、3=邮件系统等），第三位为具体细节。例如 5.1.1 表示收件地址不存在，4.4.1 表示连接超时。

```
# Postfix 生成 DSN 日志
grep "dsn=" /var/log/mail.log | awk -F'dsn=' '{print $2}' | awk '{print $1}' | sort | uniq -c | sort -rn

# 解析投递状态通知
python3 -c "
import email, sys
msg = email.message_from_binary_file(open(sys.argv[1], 'rb'))
if msg.is_multipart():
    for part in msg.walk():
        if part.get_content_type() == 'message/delivery-status':
            print(part.get_payload())
" bounce_sample.eml
```

## 踩坑与排错

Received 头部可被伪造——攻击者可在邮件头部预先插入虚假 Received 字段，应只信任目标服务器自身添加的头部和前面跳的认证信息（SPF/DKIM/DMARC）。某些 MTA 不会追加 Received 头部（如内部中继配置了 header\_checks 过滤），导致路径不完整。DSN 通知可能被中间 MTA 阻止或重定向，建议在发件域启用 DMARC rua 聚合报告作为补充追踪手段。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-delivery-tracking.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
