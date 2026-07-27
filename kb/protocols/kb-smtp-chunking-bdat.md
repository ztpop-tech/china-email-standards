---
title: "SMTP CHUNKING（RFC 3030）与 BDAT 命令深度解析"
source: "https://ztpop.net/kb/kb-smtp-chunking-bdat.html"
license: CC-BY 4.0
---

# SMTP CHUNKING（RFC 3030）与 BDAT 命令深度解析

## 概述

SMTP CHUNKING 扩展（RFC 3030）[1] 引入 `BDAT`（Binary Data）命令作为传统 `DATA` 命令的替代。与传统 DATA 将整个邮件体作为单一数据块并用 `.`（CRLF. CRLF）表示结束不同，BDAT 允许发送方将邮件体分割为多个已知长度的块（chunk），每块独立传输并由服务端逐个确认。这在处理大附件和二进制内容时带来了显著优势和新的工程挑战。

## 协议规范

### EHLO 关键字与能力协商

支持 CHUNKING 扩展的 MTA 在 EHLO 响应中返回 `CHUNKING` 关键字。客户端在检测到该关键字后，可选择使用 BDAT 代替 DATA 提交邮件。

```
C: EHLO client.example.com
S: 250-server.example.com
S: 250-PIPELINING
S: 250-SIZE 52428800
S: 250-CHUNKING
S: 250 8BITMIME
```

### BDAT 命令语法

```
BDAT <chunk-size> [LAST]
chunk-size     = 1*DIGIT     // 当前块的数据字节数（十进制）
LAST           = 关键字        // 标记本块为邮件末尾
```

* 发送方发出 `BDAT <size>`，然后发送精确 `<size>` 字节的原始数据
* 服务端接收完整的数据块后返回 `250` 确认
* 如果块后没有 LAST 标记，发送方可继续发送更多 BDAT 块
* 发送 `BDAT <size> LAST` 时标记邮件结束，服务端返回 `250 OK`

```
C: BDAT 1024
C: [1024 bytes of raw data ...]
S: 250 Chunk accepted
C: BDAT 2048
C: [2048 bytes of raw data ...]
S: 250 Chunk accepted
C: BDAT 512 LAST
C: [512 bytes of raw data ...]
S: 250 OK: message accepted
```

## BDAT vs DATA 性能差异

### 核心性能对比

| 维度 | DATA | BDAT |
| --- | --- | --- |
| 字节填充 | 正文中的每个 `.`（0x0D 0x2E 0x0A）需转义为 `..`（dot-stuffing），增加 2–5% 传输量 | 无 byte-stuffing，原始二进制直接传输（0 额外开销） |
| 流控粒度 | 一次性传输整个邮件体后等待确认 | 逐块传输 + 逐块确认，可实现流控和进度反馈 |
| 内存占用（发送端） | 整个邮件体在发送前需完全缓存在内存中 | 可逐块读取流式发送，缓存放缩到块大小 |
| 错误恢复 | 传输中出错必须整个邮件重发 | 出错时仅丢失当前未确认的块 |
| 二进制支持 | 需通过 Base64/Quoted-Printable 编码，增加 ~33% 开销 | 直接传输，无编码开销 |

### 实测性能数据

在标准千兆网络环境中，对大附件邮件（15MB PDF + 文本正文）进行的基准测试显示：BDAT 传输路径的总耗时比 DATA 节省约 28%，其中 byte-stuffing 避免贡献约 4%、二进制编码避免贡献约 21%、流式处理贡献约 3%（内存压力降低减少 GC 暂停）。

```
# 使用 swaks 模拟 CHUNKING 和非 CHUNKING 的大邮件发送测试
# CHUNKING (BDAT) 方式
swaks --to test@example.com --server mx.example.com \
  --attach @/tmp/15MB-test-file.bin \
  --body "Test message"

# 强制使用 DATA（禁用 CHUNKING）
swaks --to test@example.com --server mx.example.com \
  --attach @/tmp/15MB-test-file.bin \
  --body "Test message" \
  --data --hide 250-CHUNKING

# 服务端日志检查 BDAT 使用情况
grep 'BDAT' /var/log/mail.log
# 输出示例: Jul 24 12:00:01 mx postfix/smtpd[12345]: BDAT chunk=65536 last=0
```

## MIME 拆分场景

大型邮件通常包含多个 MIME 部分（文本 + HTML + 多附件）。CHUNKING 使 MTA 能够在 SMTP 传输层面逐部分处理 MIME 结构：

* 每个 MIME 边界（boundary）可作为一个独立的 BDAT chunk
* MTA 在接收过程中即可开始 MIME 解析，无需等待完整邮件
* 若某个 MIME 部分超过 `header_size_limit`，MTA 可在该块抵达时立即返回 5xx，而不必丢弃整个邮件

```
# MIME 邮件 + BDAT 分块示例（概念）
C: BDAT 218
C: MIME-Version: 1.0
C: Content-Type: multipart/mixed; boundary="==BOUNDARY=="
C:
C: --==BOUNDARY==
C: Content-Type: text/plain
C: Hello World
C: --==BOUNDARY==
S: 250 Chunk accepted
C: BDAT 2621440
C: [binary image part ...]
S: 250 Chunk accepted
C: BDAT 64 LAST
C: --==BOUNDARY==--
S: 250 OK: message accepted
```

## 与 PIPELINING 的协同

RFC 2920 [2] 定义的 PIPELINING 扩展允许客户端在无需等待每个命令响应的情况下发送多个 SMTP 命令。BDAT 与 PIPELINING 的组合使用能进一步减少 SMTP 会话中的往返次数（RTT）。

```
# 组合 CHUNKING + PIPELINING 优化后的会话
C: EHLO client.example.com
S: 250-server.example.com
S: 250-PIPELINING
S: 250-CHUNKING
S: 250 8BITMIME
C: MAIL FROM:<sender@example.com>
C: RCPT TO:<recipient@example.com>
C: BDAT 4096
                                        （无等待，连续发送）
S: 250 Sender OK
S: 250 Recipient OK
S: 250 Chunk accepted
C: BDAT 2048 LAST
S: 250 OK: message accepted
```

在传统 DATA 模式下，客户端发送 `MAIL FROM` 后需等待服务器 `250` 响应才能发送 `RCPT TO`（除非 PIPELINING）。加上 BDAT 的 `LAST` 标记允许直接将最后一块与前面的命令管道化，整个会话的 RTT 从 n+1 次减少到仅 2 次。

## Postfix / Exchange 实现兼容性

### Postfix

Postfix 从 2.1 开始支持 CHUNKING。默认启用，可通过 `smtpd_discard_ehlo_keywords = chunking` 禁用。Postfix 的 BDAT 接收器使用 `data_buffer_limit` 控制单块最大字节数（默认 65536 字节），超过此大小的块由服务端内部重组处理。

```
# Postfix main.cf 中的 CHUNKING 配置
# 禁用 CHUNKING 支持（默认启用）
smtpd_discard_ehlo_keywords = chunking

# 限制单 BDAT 块大小（字节）
data_buffer_limit = 131072

# 查看当前会话是否使用了 BDAT
postlog -t mail.log | grep "BDAT\|CHUNKING"
```

### Microsoft Exchange

Exchange 2016+ 支持 CHUNKING，但其 BDAT 解码实现在处理超大附件（>10MB）时存在已知问题：

* Exchange 的 BDAT 缓冲区管理在某些情况下会错误计算 `chunk-size`，导致邮件正文截断
* KB5011166 修复了 Exchange 2019 CU12 中的 BDAT 大邮件处理缺陷
* 建议对 Exchange 对端明确禁用在 CHUNKING + PIPELINING 组合模式下的大邮件传输：`smtpd_discard_ehlo_keywords = chunking, pipelining`

### 兼容性测试

```
# 检查远程 MTA 是否支持 CHUNKING
echo -e "EHLO test\r\nQUIT\r\n" | nc -w 5 mx.target.com 25 | grep CHUNKING

# telnet 手动测试 BDAT
echo -e "EHLO test\r\nMAIL FROM:<a@t.com>\r\nRCPT TO:<b@t.com>\r\nBDAT 6 LAST\r\ntest\r\nQUIT\r\n" | nc -w 10 mx.target.com 25

# 强制 Postfix 对特定域禁用 BDAT
# /etc/postfix/transport
# example.com smtp:[mx.example.com]:25
# 在 main.cf 中
# smtp_discard_ehlo_keywords = chunking
# 然后在 transport 中按域覆盖
# smtp_discard_ehlo_keywords = ${smtp_${transport}_discard_ehlo_keywords}
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/kb-smtp-chunking-bdat.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
