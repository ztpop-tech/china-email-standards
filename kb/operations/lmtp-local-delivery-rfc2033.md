---
title: "LMTP 本地邮件投递协议深度解析 — RFC 2033：从 SMTP 到本地交付的轻量 MTA"
source: "https://ztpop.net/kb/lmtp-local-delivery-rfc2033.html"
license: CC-BY 4.0
---

# LMTP 本地邮件投递协议深度解析 — RFC 2033：从 SMTP 到本地交付的轻量 MTA

邮件系统搭建时，MTA（如 Postfix）负责接收与转发，但「把信写进用户邮箱文件」这一步——最终投递（final delivery）——该用什么协议？直接用 SMTP 把信递给本地存储引擎并不合适：SMTP 的队列与临时/永久失败语义是为「跨网络传输」设计的。RFC 2033 定义 LMTP（Local Mail Transfer Protocol），作为 SMTP 的精简子集，专门用于同一主机或可信网络内的最终投递[1]。

## SMTP 作为投递协议的局限

SMTP (RFC 5321) 是存储转发传输协议：它维护队列，对临时失败返回 4xx 并重试，对永久失败返回 5xx 并退信[2]。但当一封信要投递给同一域内 5 个收件人、其中 1 个邮箱已满时，SMTP 的「整体成功/失败」模型会迫使整批重试或整批退信，无法精确表达「4 成功 1 失败」。最终投递需要的是逐收件人结果。

## RFC 2033 LMTP 语义

LMTP 复用 SMTP 的对话骨架（`LHLO` 代替 `EHLO`、`MAIL`、`RCPT`、`DATA`），但去掉了队列：它不重试、不缓冲。关键差异在数据结束后的响应——LMTP 对每个 `RCPT TO` 分别回一个响应码[1]。

```
S: 220 lmtp.example.com LMTP ready
C: LHLO client
S: 250-example.com
S: 250-8BITMIME
S: 250 PIPELINING
C: MAIL FROM:<alice@example.com>
S: 250 OK
C: RCPT TO:<bob@local>
S: 250 OK            <- 逐收件人响应
C: RCPT TO:<full@local>
S: 550 5.2.2 Mailbox full   <- 仅该收件人失败
C: DATA
S: 354 Go ahead
...
C: .
S: 250 OK
```

这样投递代理能精确知道哪些收件人成功落库，哪些需单独处理（如生成退信给发件人）。

## LMTP 与 SMTP 的关键差异

| 维度 | SMTP (RFC 5321) | LMTP (RFC 2033) |
| --- | --- | --- |
| 用途 | 跨网络传输 / 中继 | 本地最终投递 |
| 队列 | 有，支持重试 | 无，立刻响应 |
| 响应粒度 | 每封邮件整体 | 每个 RCPT 独立 |
| 命令 | EHLO | LHLO |
| 部署范围 | 不可信网络 | 可信主机 / 内网 |

## Postfix → Dovecot LMTP 部署

生产邮件系统常用 Postfix 收信、Dovecot 存信，二者通过 LMTP 衔接（优于传统的 LDA 管道）：

```
# postfix main.cf
virtual_transport = lmtp:unix:private/dovecot-lmtp
# dovecot.conf
protocols = imap lmtp
service lmtp {
  unix_listener /var/spool/postfix/private/dovecot-lmtp { mode = 0600 user = postfix }
}
```

LMTP 在投递时可触发 Sieve 过滤（见 [Sieve 过滤语言](/kb/sieve-filter-rfc5228.html)），实现「落库前分拣」。相较 LDA 进程，LMTP 支持并发投递与配额检查，更适配大规模邮件服务器。

## 可靠性要点

* **仅在可信边界使用**：LMTP 无认证/加密，必须限于本机 socket 或内网，绝不能暴露到公网。
* **配额即失败**：邮箱满时 LMTP 回 5xx，Postfix 据此生成退信，需监控配额避免误退。
* **与 Sieve 配合**：最终投递阶段执行过滤，保证所有客户端视图一致。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/lmtp-local-delivery-rfc2033.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
