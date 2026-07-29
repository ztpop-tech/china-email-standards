---
title: "Milter 邮件过滤架构深入：从协议原理到自定义策略"
source: "https://ztpop.net/kb/milter-filter-architecture.html"
license: CC-BY 4.0
---

# Milter 邮件过滤架构深入：从协议原理到自定义策略

## 1. Milter 协议的历史与设计哲学

Milter（Mail Filter）协议最初由 Sendmail, Inc. 在 2000 年前后设计并实现，其设计动机源于对 MTA（Mail Transfer Agent）单体架构的反思：传统的 Sendmail 将反垃圾检查、病毒扫描、内容过滤等所有邮件处理逻辑紧密耦合在 MTA 二进制内部，任何一项过滤逻辑的修改或升级都需要重新编译或重启 MTA，这在生产环境中带来了显著的可用性风险。

Milter 协议通过定义一套标准化的进程间通信（IPC）接口，将邮件过滤逻辑从 MTA 进程中解耦到独立的过滤进程（Milter 守护进程）中。MTA 在 SMTP 会话的各个关键阶段向所有已注册的 Milter 发送回调通知，Milter 进程对每个阶段做出 accept（接受）、reject（拒绝）、discard（静默丢弃）、tempfail（临时失败）或 continue（继续，不作决策）五种响应之一。这种架构模式在概念上对应于分布式系统中的策略决策点（PDP）与策略执行点（PEP）分离——MTA 是 PEP，Milter 是 PDP。

协议在实现层面通过 libmilter 库提供 C 语言 API，通信通道支持两种传输方式：本地 UNIX domain socket（低延迟、高性能）和 TCP socket（支持远程 Milter 部署和多实例负载均衡）。自 Sendmail 8.12 首次引入以来，Milter 协议已成为事实上的邮件过滤中间件标准，被 Postfix、OpenDKIM、OpenDMARC、MIMEDefang 等广泛采用。

## 2. Milter 协议状态机与回调类型

Milter 协议通过一个预定义的回调（callback）集合，将 SMTP 会话的完整生命周期暴露给过滤器进程。每个回调函数名称以 `xxfi_` 为前缀（表示 "extended filter interface"），对应的调用时机和可操作范围如下表所示：

2. Milter 协议状态机与回调类型

| 回调函数 | SMTP 阶段 | 可获取的上下文数据 | 典型用途 |
| `xxfi_connect` | TCP 连接建立 | 客户端 IP 地址、主机名（PTR 记录）、socket 地址族 | IP 信誉查询、DNSBL 实时检查、连接速率限制 |
| `xxfi_helo` | EHLO/HELO 命令后 | HELO 参数字符串（声称的主机名） | HELO 语法合规性验证、PTR 反向一致性检查 |
| `xxfi_envfrom` | MAIL FROM 命令后 | 信封发件人地址（reverse-path）、ESMTP 参数（如 SIZE、BODY） | SPF 验证、发件人黑名单、空发件人检测（bounce） |
| `xxfi_envrcpt` | RCPT TO 命令后（每个收件人独立回调） | 信封收件人地址（forward-path）、ESMTP 参数 | 灰名单检查（triplet 匹配）、收件人地址验证（lda 存在性） |
| `xxfi_header` | DATA 阶段——每条消息头行独立回调 | 消息头名称和原始值（未解码） | 消息头注入（DKIM 签名前添加 Authentication-Results）、消息头模式匹配 |
| `xxfi_eoh` | 消息头结束——头与体之间的空行后 | 完整的消息头块（所有已收到的头行） | 综合头分析、DMARC 验证入口点、头完整性检查 |
| `xxfi_body` | 消息体数据块（每块独立回调） | 消息体数据块（可能被分片传输） | 实时内容扫描、嵌入式 URL 提取、附件 MIME 解析 |
| `xxfi_eom` | 消息体结束（CRLF.CRLF） | 完整的邮件（头+体）上下文 | 最终决策点——签名注入、修改、拒绝；沙箱引擎调用 |
| `xxfi_close` | 连接关闭 | 本连接全生命周期的累积上下文 | 释放连接级资源、写入统计日志、更新计数器 |

### 2.1 协议交互时序示例

在一次完整的 SMTP 会话中，Milter 回调的执行序列严格遵循 SMTP 协议的状态机转换。以下是带日志输出的完整回调时序：

```
# TCP 连接建立
12:34:56.001 milter[12345]: xxfi_connect(hostname="mx.sender.example", addr=203.0.113.42)

# EHLO 命令
12:34:56.120 milter[12345]: xxfi_helo(helohost="mx.sender.example")

# MAIL FROM 命令
12:34:56.250 milter[12345]: xxfi_envfrom(sender="<sender@example.net>", esmtp_args=["SIZE=45678"])

# RCPT TO 命令
12:34:56.380 milter[12345]: xxfi_envrcpt(recipient="<user@example.org>")

# DATA 命令 —— 消息头逐行回调
12:34:56.500 milter[12345]: xxfi_header(name="From", value="sender@example.net")
12:34:56.501 milter[12345]: xxfi_header(name="To", value="user@example.org")
12:34:56.502 milter[12345]: xxfi_header(name="Subject", value="=?UTF-8?B?...?=")
12:34:56.503 milter[12345]: xxfi_eoh()

# 消息体分块传输
12:34:56.600 milter[12345]: xxfi_body(chunk=0, len=4096)
12:34:56.610 milter[12345]: xxfi_body(chunk=1, len=2048)

# 消息体结束
12:34:56.720 milter[12345]: xxfi_eom() → SMFIS_CONTINUE

# 连接关闭
12:34:56.850 milter[12345]: xxfi_close()
```

### 2.2 Milter 协议标志位

每个 Milter 在注册时通过协议标志位（protocol flags）声明自己的能力，MTA 据此决定向该 Milter 发送哪些回调。关键标志位包括：

* `SMFIF_ADDHDRS`：Milter 可在 xxfi\_eom 中通过 smfi\_addheader() 向邮件注入新消息头。
* `SMFIF_CHGBODY`：Milter 可在 xxfi\_eom 中通过 smfi\_replacebody() 修改邮件消息体。
* `SMFIF_ADDRCPT`：Milter 可在 xxfi\_eom 中通过 smfi\_addrcpt() 添加额外的收件人（如 BCC 归档地址）。
* `SMFIF_DELRCPT`：Milter 可在 xxfi\_eom 中通过 smfi\_delrcpt() 删除收件人。
* `SMFIF_QUARANTINE`：Milter 可将邮件标记为隔离状态。
* `SMFIF_CHGHDRS`：Milter 可修改或删除已有的消息头。

精确声明标志位不仅避免 MTA 向不需要某些数据的 Milter 发送不必要的回调（减少 IPC 流量），还向 MTA 声明该 Milter 是否会对邮件内容做出修改——非修改性 Milter（如纯粹的评估器）不声明修改类标志位，MTA 可以并行化其处理。

## 3. Postfix Milter 集成配置

Postfix 通过 `smtpd_milters`（作用于 SMTPD 守护进程接收的外部邮件）和 `non_smtpd_milters`（作用于通过 sendmail 命令提交的内部邮件）两个配置参数管理 Milter 列表。Postfix 对 Milter 的支持始于 2.3 版本，并在后续版本中持续增强，目前支持的 Milter 协议版本为 6（兼容 Sendmail 8.14+ 的完整协议能力集）。

Postfix main.cf 的完整生产级 Milter 配置：

```
# main.cf — 生产级 Milter 配置
# 按优先级顺序排列 Milter 链
smtpd_milters =
    unix:/var/run/opendkim/opendkim.sock,
    unix:/var/run/opendmarc/opendmarc.sock,
    inet:127.0.0.1:8893

non_smtpd_milters =
    unix:/var/run/opendkim/opendkim.sock

# Milter 连接超时——控制 MTA 等待 Milter socket 就绪的时间
milter_connect_timeout = 10s

# Milter 命令超时——特别是 xxfi_eom 中调用外部沙箱/API 的耗时上限
milter_command_timeout = 60s

# Milter 内容超时——消息体传输期间的总超时
milter_content_timeout = 300s

# 当 Milter 不可用时的默认行为：tempfail = 临时拒绝（安全优先）
milter_default_action = tempfail

# 启用协议版本 6，支持所有 SMFIF_* 宏能力
milter_protocol = 6

# Milter 宏扩展——将 SMTP 上下文通过宏变量传递给 Milter
milter_macro_daemon_name = $myhostname
milter_macros_connect = j _ {daemon_name} {if_name} {if_addr}
milter_macros_helo = {tls_version} {cipher} {cipher_bits} {cert_subject} {cert_issuer}
milter_macros_mailfrom = i {auth_type} {auth_authen} {auth_author} {mail_addr}
milter_macros_rcptto = {rcpt_addr} {rcpt_host} {rcpt_mailer}
milter_macros_data = i
```

Milter 列表中的顺序定义了执行优先级——排在前面的 Milter 的回调先被调用。Postfix 的 Milter 链是同步串行的：每一封邮件的每一个回调依次在链中的所有 Milter 上执行，直到某个 Milter 返回非 CONTINUE 响应（如 REJECT）或链条走完。这意味着 Milter 链的总延迟等于所有单个 Milter 回调延迟的累加和，性能优化策略必须以链条总延迟为考虑单位。

## 4. OpenDKIM 与 OpenDMARC 架构深度

OpenDKIM 和 OpenDMARC 是两个最广泛部署的 Milter 应用，分别实现 DKIM（RFC 6376）签名/验证和 DMARC（RFC 7489）策略评估。它们共享相似的架构模式：底层通过 libmilter 实现与 MTA 的通信协议，中层通过 libopendkim/libopendmarc 库封装协议核心逻辑（包括 DNS 公钥检索、密码学计算和策略评估），上层通过配置文件控制运行时行为参数。

### 4.1 OpenDKIM 签名模式配置

```
# /etc/opendkim.conf — 签名+验证双模式
Mode        sv          # s=signing（签名）, v=verifying（验证）
Socket      local:/var/run/opendkim/opendkim.sock
PidFile     /var/run/opendkim/opendkim.pid
UserID      opendkim:opendkim

# 签名表：定义"哪个发件域用哪个签名密钥"的映射关系 (RFC 6376 §3.6)
SigningTable    refile:/etc/opendkim/SigningTable
KeyTable        refile:/etc/opendkim/KeyTable

# /etc/opendkim/SigningTable 示例
# *@example.net   default._domainkey.example.net
# *@example.org   default._domainkey.example.org

# /etc/opendkim/KeyTable 示例
# default._domainkey.example.net   example.net:default:\
#    /etc/opendkim/keys/example.net/default.private

# 规范化算法：relaxed/simple 组合是最广泛兼容的配置
Canonicalization    relaxed/relaxed
# 签名算法：rsa-sha256（推荐）或 ed25519-sha256
SignatureAlgorithm  rsa-sha256
# 签名头的选择——必须包含 From 头（RFC 6376 要求）
SignHeaders     From,Subject,Date,To,Cc,Message-ID
```

### 4.2 OpenDMARC 验证配置与拒收行为

```
# /etc/opendmarc.conf
Socket      local:/var/run/opendmarc/opendmarc.sock
PidFile     /var/run/opendmarc/opendmarc.pid
UserID      opendmarc:opendmarc

# 核心行为：当 DMARC 结果为 fail 且策略为 p=reject 时，
# OpenDMARC 直接向 MTA 返回 SMFIS_REJECT，在 SMTP 阶段拒绝邮件
RejectFailures  true

# SPF 相关：是否忽略 SPF 结果、是否需要自验证
SPFIgnoreResults    false
SPFSelfValidate     true

# 聚合报告（RUA）的生成和发送配置
HistoryFile     /var/run/opendmarc/opendmarc.dat
FailureReports      true
FailureReportsSentBy    dmarc-noreply@example.net

# 对于不要求拒收的 DMARC fail，在邮件头中添加 Authentication-Results
# 供下游 spam filters（如 SpamAssassin）使用
AuthservID      mx.ztpop.net
```

## 5. 自定义 Python Milter 开发

Python 生态中，`pymilter` 库提供了 libmilter 的完整 Python 绑定，使开发者能够用纯 Python 编写生产级的 Milter 过滤器。与 C 语言原生 libmilter 相比，Python Milter 在开发效率上具有显著优势，但每个回调的执行延迟会多出 Python 解释器开销（通常在微秒级），在高于 100 msg/s 的吞吐量场景中建议使用 C 语言或 Go 实现作为替代。

以下是一个完整的自定义 Milter 实现——连接级速率限制与消息头注入：

```
#!/usr/bin/env python3
"""custom_rate_limit_milter.py — 连接速率限制 Milter

功能：
  - xxfi_connect：基于每个 IP 的滑动窗口连接速率限制（超限返回 tempfail）
  - xxfi_eom：为通过检查的邮件注入追踪头 X-Milter-Processed

依赖：pip install pymilter
"""

import Milter
import time
from collections import defaultdict
from threading import Lock

# 配置参数
RATE_LIMIT = 30          # 每分钟每个 IP 的最大连接数
WINDOW = 60              # 滑动窗口大小（秒）
SOCKET = "inet:8893@localhost"

class RateLimitMilter(Milter.Base):
    """连接速率限制 Milter 实现"""

    # 类级统计存储：{ip_address: [timestamp, timestamp, ...]}
    _connections = defaultdict(list)
    _lock = Lock()

    def __init__(self):
        self.id = Milter.uniqueID()
        self.ip = None

    @Milter.noreply
    def connect(self, hostname, family, hostaddr):
        """xxfi_connect 回调——连接建立即触发"""
        ip = hostaddr[0]
        self.ip = ip

        with self._lock:
            now = time.time()
            cutoff = now - WINDOW
            # 清理过期的时间戳记录（滑动窗口）
            self._connections[ip] = [
                ts for ts in self._connections[ip] if ts > cutoff
            ]
            # 速率检查
            if len(self._connections[ip]) >= RATE_LIMIT:
                self.setreply("451", "4.7.1",
                    "Rate limit exceeded, try again later")
                return Milter.REJECT
            # 记录本次连接
            self._connections[ip].append(now)
        return Milter.CONTINUE

    def eom(self):
        """xxfi_eom 回调——消息结束，注入追踪头"""
        self.addheader("X-Milter-Processed",
            f"RateLimitMilter; ip={self.ip}; id={self.id}")
        return Milter.CONTINUE

    def close(self):
        """xxfi_close 回调——连接关闭，清理连接级变量"""
        self.ip = None
        return Milter.CONTINUE

def main():
    """启动 Milter 守护进程"""
    Milter.factory = RateLimitMilter
    print(f"RateLimitMilter starting on {SOCKET}")
    Milter.runmilter("RateLimitMilter", SOCKET, timeout=30)
    print("RateLimitMilter stopped")

if __name__ == "__main__":
    main()
```

## 6. 性能调优策略

在生产环境中，邮件系统可能配置 5-8 个串行的 Milter 过滤器（如 OpenDKIM 签名 + OpenDKIM 验证 + OpenDMARC + SpamAssassin Milter + 自定义速率限制 Milter + ClamAV Milter + Rspamd Milter），若不进行系统性的性能优化，Milter 链的串行延迟叠加会导致 SMTP 会话延长数秒，影响用户体验并降低 MTA 吞吐量（concurrency 受限）。

核心优化策略分为四个维度：

* **回调范围精简**：通过 SMFIF\_\* 标志位精确声明 Milter 所需的协议阶段，使 MTA 跳过不需要的回调。例如，一个只做 IP 信誉检查的 Milter 应该只注册 `SMFIF_ADDHDRS` 和 `SMFIF_NR_CONNECT`，而不需要接收 xxfi\_body 回调。
* **IPC 通道优化**：Unix domain socket 的 IPC 开销约为 TCP socket 的 75-80%。对于高吞吐量部署（>100 msg/s），使用 Unix socket 并用多工作进程模型并行处理。OpenDKIM 和 OpenDMARC 均支持通过配置文件指定工作进程数或用 daemontools / systemd 启动多个实例，Postfix 的 Milter 连接机制能自动在多个 Milter socket 之间进行负载均衡。
* **DNS 缓存策略**：DKIM 密钥检索、DNSBL 查询、SPF 策略拉取等操作均依赖 DNS 查询，这是 Milter 处理延迟的头号来源。推荐部署本地 DNS 递归解析器（如 unbound）并配置积极的缓存策略；OpenDKIM 内部也具备密钥缓存机制（KeyTable 的 refile 格式本质上也是预加载式缓存）。
* **Milter 宏剪裁**：Postfix 的 milter\_macro\_\* 配置参数决定了 MTA 向 Milter 传递的上下文数据量。仅传递每个 Milter 实际需要的宏变量，避免在 MTA 和 Milter 之间传输冗余的、不会被使用的数据——这些数据虽体积不大，但在高并发场景下的累积效应不容忽视。

本站技术文章采用 CC-BY 4.0 许可，可自由引用，仅需标注来源 [ztpop.net](https://www.ztpop.net)。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/milter-filter-architecture.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
