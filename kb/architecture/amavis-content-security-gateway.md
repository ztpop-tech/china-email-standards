---
title: "Amavis 邮件内容安全网关深度解析 — 病毒扫描、内容过滤与策略引擎"
source: "https://ztpop.net/kb/amavis-content-security-gateway.html"
license: CC-BY 4.0
---

# Amavis 邮件内容安全网关深度解析 — 病毒扫描、内容过滤与策略引擎

## 一、Amavis 在 Postfix 管线中的精确位置

Amavis (A Mail Virus Scanner) 是邮件内容安全体系的中间件核心。它不在 SMTP 协议的"正面" — 客户端永远不会直接连接 Amavis；它是 MTA 的内容过滤器，位于邮件接收完成后、投递到最终信箱之前的一个夹层位置。理解这段管线的数据流向，是正确配置和排障的前提。

以 Postfix 为例，一封入站邮件经过 Amavis 的完整路径如下：

一、Amavis 在 Postfix 管线中的精确位置

| 阶段 | 守护进程 | 套接字 | 动作 |
| --- | --- | --- | --- |
| ① 入站连接 | smtpd | :25 | 接收邮件，写入 incoming 队列 |
| ② 队列管理 | qmgr | — | 从 incoming 取出，匹配 content\_filter |
| ③ 投递到过滤器 | smtp | → amavis:10024 | Postfix smtp 客户端投递到 Amavis SMTP |
| ④ 内容扫描 | amavisd | :10024 | 病毒/垃圾/策略/DKIM 全流程扫描 |
| ⑤ 回注 MTA | amavisd | → Postfix:10025 | 扫描完成，回递邮件给 Postfix |
| ⑥ 二次清理 | smtpd | :10025 | 接收回注邮件，执行 cleanup |
| ⑦ 最终投递 | qmgr | — | cleanup 后重新入队，投递到 mailbox |

核心配置在 Postfix
`master.cf`
中完成：

```
# /etc/postfix/master.cf — Amavis 内容过滤管线

# ============================
# Postfix → Amavis (10024)
# ============================
# 在 /etc/postfix/main.cf 中声明:
#   content_filter = smtp-amavis:[127.0.0.1]:10024

# 定义 smtp-amavis 传输服务
smtp-amavis unix -    -       n       -       2       smtp
  -o smtp_data_done_timeout=1200
  -o smtp_send_xforward_command=yes
  -o disable_dns_lookups=yes
  -o max_use=20

# ============================
# Amavis → Postfix 回注 (10025)
# ============================
# Amavis 扫描完成后将邮件送回此处，绕过 content_filter 避免死循环
127.0.0.1:10025 inet n  -       n       -       -       smtpd
  -o content_filter=
  -o local_recipient_maps=
  -o relay_recipient_maps=
  -o smtpd_restriction_classes=
  -o smtpd_delay_reject=no
  -o smtpd_client_restrictions=permit_mynetworks,reject
  -o smtpd_helo_restrictions=
  -o smtpd_sender_restrictions=
  -o smtpd_recipient_restrictions=permit_mynetworks,reject
  -o smtpd_data_restrictions=
  -o mynetworks=127.0.0.0/8
  -o smtpd_authorized_xforward_hosts=127.0.0.0/8
  -o receive_override_options=no_header_body_checks,no_unknown_recipient_checks,no_address_mappings
```

回注端口的几个关键
`-o`
覆盖需要特别注意：
`no_header_body_checks`
防止邮件在回注时被重复执行 header\_checks 或 body\_checks；
`no_address_mappings`
避免 canonical 映射表被二次应用；
`smtpd_authorized_xforward_hosts`
允许 Amavis 通过 XFORWARD 传递原始客户端 IP — 这对日志审计至关重要，否则所有经 Amavis 处理的邮件看起来都来自 127.0.0.1。

## 二、三种集成模式对比：SMTP 代理 vs Milter vs Pipe

MTA 与内容过滤器的连接方式决定了邮件管线的吞吐上限、故障隔离能力和部署复杂度。三种模式各有适用场景：

二、三种集成模式对比：SMTP 代理 vs Milter vs Pipe

| 模式 | 通信机制 | 协议 | 并发模型 | 故障行为 | 适用场景 |
| --- | --- | --- | --- | --- | --- |
| SMTP 代理 (content\_filter) | MTA 作为 SMTP 客户端投递 | SMTP/LMTP | 多进程并发，每个连接独立处理 | 可配置 bypass: 超时后跳过扫描 | 生产环境首选，成熟稳定 |
| Milter (Sendmail/Postfix) | 共享库动态链接 | Milter 协议 | 同步回调，可能阻塞 SMTP 会话 | Milter 崩溃可能导致邮件丢失 | Sendmail 用户、轻量级过滤 |
| Pipe (外部程序) | stdin/stdout 管道 | 无 | 每个邮件 fork 新进程 | 进程崩溃后 Postfix 视为临时故障 | 简单过滤脚本、自定义检测器 |

**SMTP 代理模式**
是目前最广泛使用的方案。Postfix 的
`content_filter`
参数指向 Amavis 监听的 10024 端口，Postfix 自身的
`smtp`
传输程序负责将邮件投递过去。这套机制的可靠性来自于 Postfix 内置的队列管理：即使 Amavis 暂时不可达，邮件也不会丢失 —
`qmgr`
会在 deferred 队列中保留，按退避策略重试。

**Milter 模式**
的历史包袱较重。Sendmail Milter API 属于同步回调架构 — smtpd 在 SMTP 会话中直接调用 milter，如果 milter 处理时间过长（例如病毒库更新期间的 I/O 阻塞），整个 SMTP 握手就会被挂起。Postfix 从 2.3 版本开始通过
`smtpd_milters`
支持 Milter，但在实际部署中更推荐 SMTP 代理模式用于重型内容扫描。

**Pipe 模式**
适合编写快速的内容检测脚本，但每次调用都 fork 一个新进程，不适合高并发场景。RFC 5321 §4.4 提到了 MTA 扩展对内容扫描的支持需求，但并未规范化具体的集成接口，这也解释了为何 Today 的生产环境中 SMTP 代理成为事实标准。

```
# Pipe 模式示例（仅供参考，生产不推荐用于 Amavis）
# /etc/postfix/master.cf
amavis-pipe unix -    n       n       -       1       pipe
  flags=Rq user=amavis argv=/usr/local/bin/amavis-pipe
    -f ${sender} -- ${recipient}
```

## 三、病毒扫描引擎集成

### 3.1 ClamAV + clamd 守护进程

ClamAV 是部署最广泛的开源防病毒引擎。Amavis 不直接调用
`clamscan`
命令行 — 那样每个邮件 fork 一个进程太昂贵。正确的方式是让 Amavis 通过
`clamd`
守护进程的 Unix socket 或 TCP socket 通信，利用 clamd 内部已加载的病毒库进行流式扫描。

**clamd 端配置**
（
`/etc/clamav/clamd.conf`
）：

```
# clamd 监听 Unix socket
LocalSocket /var/run/clamav/clamd.sock
LocalSocketGroup amavis
LocalSocketMode 660

# 或监听 TCP（多主机部署场景）
# TCPSocket 3310
# TCPAddr 127.0.0.1

# 扫描限制
MaxFileSize 100M          # 跳过 > 100MB 的附件
MaxScanSize 200M          # 单封邮件扫描上限
MaxRecursion 16           # 压缩包递归层数
MaxFiles 10000            # 单封邮件中最大文件数

# 归档炸弹检测
MaxEmbeddedPE 20M         # 内嵌 PE 文件上限
AlertBrokenExecutables yes
AlertOLE2 yes             # OLE2 (Office 文档) 宏病毒检测
AlertPDF yes              # PDF 漏洞利用检测
AlertEncryptedArchive yes # 加密压缩包告警
```

**Amavis 侧对应配置**
（
`/etc/amavis/conf.d/15-av_scanners`
）：

```
# 病毒扫描引擎列表（按顺序调用，命中即终止）
@av_scanners = (

  # === 主引擎：ClamAV clamd (Unix socket) ===
  ['ClamAV-clamd',
   \&ask_daemon,
   ["CONTSCAN {}\n", '/var/run/clamav/clamd.sock'],
   qr/\bOK$/m, qr/\bFOUND$/m,
   qr/^.*?: (?!Infected Archive)(.*) (FOUND|ERROR) /m ],

  # === 备选：ClamAV clamd (TCP) ===
  # ['ClamAV-clamd-tcp',
  #  \&ask_daemon,
  #  ["CONTSCAN {}\n", ['127.0.0.1', 3310]],
  #  qr/\bOK$/m, qr/\bFOUND$/m,
  #  qr/^.*?: (?!Infected Archive)(.*) FOUND /m ],

  # === fallback：命令行扫描（仅 clamd 不可用时激活） ===
  ['ClamAV-clamscan', 'clamscan',
    '--stdout --no-summary -r --tempdir=$TEMPBASE {}',
    [0], qr/:.*\sFOUND$/m, qr/^.*?: (?!Infected Archive)(.*) FOUND /m ],
);
```

`CONTSCAN`
与
`INSTREAM`
是两种 clamd 协议命令：
`CONTSCAN`
传递文件路径，要求 clamd 进程对该路径有读权限；
`INSTREAM`
通过 socket 流式传输数据，不需要文件系统权限，更适合 chroot 环境。Amavis 默认使用
`CONTSCAN`
，因为它依赖
`$TEMPBASE`
临时目录中已解码的附件文件。

### 3.2 商业引擎集成（Sophos / ESET）

开源的 ClamAV 对已知恶意软件有较高检出率，但对 0-day 和高级持续性威胁（APT）的覆盖存在天然滞后。中大型企业通常叠加一至两个商业引擎。Amavis 的原生设计支持多引擎串行扫描 — 按
`@av_scanners`
数组的顺序，第一个返回"发现病毒"即终止后续引擎的调用，这避免了不必要的计算开销。

```
@av_scanners = (
  # 首选：商业引擎（先扫，检出率最高）
  ['Sophos-SAVI',
   \&ask_daemon,
   ["{}\n", '/var/run/savdid.sock'],
   qr/^OK/m, qr/^VIRUS/m,
   qr/^VIRUS (\S+) (.+)$/m ],

  ['ESET-Server',
   \&ask_daemon,
   ["{}\n", '/var/run/esets.sock'],
   qr/^OK/m, qr/^VIRUS/m,
   qr/^VIRUS (\S+) (.+)$/m ],

  # 最后：ClamAV 兜底
  ['ClamAV-clamd',
   \&ask_daemon,
   ["CONTSCAN {}\n", '/var/run/clamav/clamd.sock'],
   qr/\bOK$/m, qr/\bFOUND$/m,
   qr/^.*?: (?!Infected Archive)(.*) (FOUND|ERROR) /m ],
);
```

串行扫描的工程权衡值得关注：每个引擎独立遍历同一封邮件的所有 MIME 部件，N 个引擎 = N 倍 I/O。扫描 100 封平均 500KB 的邮件时差异尚可忽略；当日处理量达到数十万封且附件平均 5MB 以上时，并行扫描（通过
`@av_scanners_backup`
配置辅助引擎）才是更合理的选择。

## 四、内容过滤策略

### 4.1 附件类型黑白名单

附件的危险程度不取决于文件内容本身，而取决于接收者打开它时操作系统会执行什么操作。一个包含恶意宏的
`.docm`
文件在 Word 中打开时无异于代码执行。根据 RFC 2045/2046 中 MIME 类型体系，Amavis 在 MIME 解码阶段就已经拿到了每个部件的 Content-Type 和文件名，可以在病毒扫描之前先做文件类型策略裁决。

```
# /etc/amavis/conf.d/50-user — 附件类型策略
# 这些扩展名的文件将被直接拦截，不进入病毒扫描
$banned_filename_re = new_RE(
  # 可执行文件（Windows）
  qr'\.[Ee][Xx][Ee]$'mo,
  qr'\.[Cc][Oo][Mm]$'mo,
  qr'\.[Bb][Aa][Tt]$'mo,
  qr'\.[Cc][Mm][Dd]$'mo,
  qr'\.[Ss][Cc][Rr]$'mo,       # 屏幕保护程序
  qr'\.[Pp][Ii][Ff]$'mo,       # 程序信息文件
  qr'\.[Jj][Ss]$'mo,           # JavaScript
  qr'\.[Vv][Bb][Ss]$'mo,       # VBScript
  qr'\.[Ww][Ss][Ff]$'mo,       # Windows Script File
  qr'\.[Pp][Ss]1$'mo,          # PowerShell

  # 脚本（跨平台）
  qr'\.[Ss][Hh]$'mo,           # Unix Shell
  qr'\.[Pp][Ll]$'mo,           # Perl
  qr'\.[Pp][Yy]$'mo,           # Python
  qr'\.jar$'mo,                # Java Archive

  # Office 宏文件
  qr'\.docm$'mo,
  qr'\.xlsm$'mo,
  qr'\.pptm$'mo,

  # 高危压缩（双重扩展名）
  qr'\.[Zz][Ii][Pp]\.[Ee][Xx][Ee]$'mo,
  qr'\.rar\.[Ee][Xx][Ee]$'mo,
);

# 更精细的规则：只拦截特定 MIME 类型的可执行内容
$banned_namepath_re = new_RE(
  # 拦截任何类型为 application/x-msdownload 的 MIME 部件
  qr/^UNDECIPHERABLE$/m,          # 无法解码的部件
  qr'(?# 密码保护的归档 )\.(zip|rar|7z|arj|ace)\0*Protected\.(exe|com|bat|scr|pif|vbs|js|wsf|ps1)$'mi,
);
```

### 4.2 恶意 MIME 类型与归档炸弹

RFC 2046 §5.1 定义了 MIME 类型的注册和扩展机制，但攻击者常滥用
`multipart/mixed`
结构的边界欺骗和嵌套深度来绕过检测。归档炸弹（archive bomb）是一类经典的 DoS 攻击：一个表面上几 KB 的 zip 文件解压后展开为数 GB 的数据，耗尽扫描进程的内存。

```
# Amavis 归档炸弹防御参数（50-user）
$MAXLEVELS      = 14;    # MIME 嵌套最大层数
$MAXFILES       = 1500;  # 单封邮件最大 MIME 部件数
$MIN_EXPANSION_QUOTA = 100 * 1024;    # 最小解压权重（100KB）
$MAX_EXPANSION_QUOTA = 300 * 1024 * 1024; # 最大解压权重（300MB）

# 膨胀比超过此值 → 归档炸弹判定
# 算法: 每层解压按比例累加"权重"= size * depth_factor
$MIN_EXPANSION_FACTOR =   5;  # 至少膨胀 5x 才算异常
$MAX_EXPANSION_FACTOR   = 500; # 膨胀超过 500x → 阻断

# 归档炸弹的处理策略
$final_archive_destiny = D_BOUNCE;  # 拒收（返回 5xx）
# $final_archive_destiny = D_DISCARD;  # 静默丢弃（不推荐）
```

归档炸弹检测的算法核心是"展开配额"（expansion quota）机制：对归档文件中的每个条目，Amavis 根据压缩前后的大小比累加一个"展开权"，当累加值超过
`$MAX_EXPANSION_QUOTA`
时，该归档被标记为炸弹并中止解压。这一机制在 zip bomb（如著名的 42.zip — 4.5 PB 展开）和递归 7z 嵌套（一层套一层套一层，每层都是合法压缩）两类场景下都能有效防御。

### 4.3 解码与标记策略

```
# 病毒和恶意附件的最终处置
$final_virus_destiny      = D_DISCARD;  # 病毒邮件静默丢弃
$final_banned_destiny     = D_BOUNCE;   # 禁止的附件 → 退回发件人
$final_bad_header_destiny = D_PASS;     # 头部异常但内容可能正常 → 放行
$final_spam_destiny       = D_PASS;     # 垃圾由 SpamAssassin 评分决定

# 通知管理员（每封病毒邮件发一份通知到 postmaster）
$virus_admin = "postmaster\@\$mydomain";
$virus_admin_maps = {
  '.' => 'postmaster@example.com',
};

# 对发件人的退回通知模板
$banned_quarantine_to = 'virus-quarantine@example.com';
$banned_files_quarantine_method = 'local:virus-%m';
```

## 五、SpamAssassin 联动：评分与头部传递

Amavis 与 SpamAssassin 的集成方案比直接在 MTA 层面调用
`spamc`
更优雅。原因有二：Amavis 已经完成了 MIME 解码（包括 base64/quoted-printable 解码），SpamAssassin 拿到的正文是纯文本和 HTML 的解码版本，无需再做二次解码；其次，Amavis 可以通过 Policy Bank 对不同的收件人域执行不同的 SpamAssassin 策略。

```
# /etc/amavis/conf.d/50-user — SA 集成
@bypass_spam_checks_maps = (0);  # 全局启用（0 = 对所有收件人检查）

# SpamAssassin 阈值
$sa_tag_level_deflt  = -999;     # 即使 -100 分也加 X-Spam-* 头（调试用）
$sa_tag2_level_deflt = 5.0;      # ≥ 5.0 → 在 Subject 前加标签 + 修改头部
$sa_kill_level_deflt = 10.0;     # ≥ 10.0 → 触发 D_REJECT（拒绝接收）

# 垃圾邮件标记
$sa_spam_subject_tag = '***SPAM*** ';
$sa_spam_modifies_subj = 1;      # 修改 Subject: 加标签

# 头部传递：将以下 SA 测试结果写入邮件头
$sa_spam_report_header = 1;      # 添加 X-Spam-Report 详细报告
$sa_dsn_cutoff_level = 10;       # DSN 通知阈值

# 白名单：内部域名间不检查
$sa_spam_whitelist_sender_re = qr/^[^@]+@(internal\.com|corp\.local)$/i;
```

评分通过后，Amavis 向邮件注入的核心头部包括：

```
X-Spam-Status: Yes, score=7.2 required=5.0 tests=BAYES_99,HTML_MESSAGE,
    URIBL_BLACK autolearn=spam
X-Spam-Score: 7.2
X-Spam-Flag: YES
X-Spam-Level: *******
X-Spam-Report: * 3.5 BAYES_99 Bayes spam probability is 99 to 100%
                * 0.1 HTML_MESSAGE HTML included in message
                * 2.5 URIBL_BLACK Contains a URL listed by URIBL
X-Spam-Checker-Version: SpamAssassin 4.0.0 on mx01.example.com
```

下游系统（Sieve、LDA、归档系统）通过解析
`X-Spam-Flag`
和
`X-Spam-Score`
做路由决策。一个常见的落地配置是：Dovecot Sieve 读取这两个头部，将
`X-Spam-Flag: YES`
的邮件自动移入 Junk 文件夹。

## 六、DKIM 签名与验证

Amavisd-new 内置了 DKIM 模块，无需额外安装 opendkim 或 dkimpy。这一设计减少了邮件管线的跳数 — 在 Amavis 中签名/验签意味着邮件从 content\_filter 回注到 Postfix 时已经携带了 DKIM 签名头，减少了外部守护进程的进程间通信开销。

### 6.1 DKIM 签名配置

根据 RFC 6376 §3，DKIM 签名的核心参数包括选择器（selector）、域名（d=）、签名算法（a=）、规范化方式（c=）和头部列表（h=）。Amavis 将这些参数映射到 Perl 配置：

```
# /etc/amavis/conf.d/50-user — DKIM 签名
$enable_dkim_signing = 1;

# 签名密钥和选择器配置
dkim_key(
  'example.com',
  'mail2024',
  '/var/db/dkim/example.com/mail2024.key.pem'
);

# 多域签名（每个发件域使用独立的选择器和密钥对）
dkim_key('corp.example.com', 'dkim2025',
         '/var/db/dkim/corp.example.com/dkim2025.key.pem');

# 签名策略映射：哪些发件域需要签名
@dkim_signature_options_bysender_maps = (
  {
    '.'                => {  # 全局默认
      ttl    => 21 * 24 * 3600,  # 签名有效期 21 天
      c      => 'relaxed/simple', # 规范：relaxed 头部 + simple 正文
      a      => 'rsa-sha256',
    },
    'example.com'      => { a => 'rsa-sha256', ttl => 14*24*3600 },
    'newsletter.example.com' => { a => 'rsa-sha256', ttl => 7*24*3600 },
  }
);

# 外发邮件自动签名（基于发件人域匹配密钥）
$originating = 1;
```

密钥生成命令（使用 OpenSSL）：

```
# 生成 2048-bit RSA 私钥（当前安全标准）
openssl genrsa -out /var/db/dkim/example.com/mail2024.key.pem 2048

# 提取公钥（用于 DNS TXT 记录）
openssl rsa -in /var/db/dkim/example.com/mail2024.key.pem \
  -pubout -outform der 2>/dev/null | openssl base64 -A

# 将公钥写入 DNS:
# mail2024._domainkey.example.com. IN TXT "v=DKIM1; h=sha256; k=rsa; p=MIIBIjAN..."
```

### 6.2 DKIM 验证

```
# /etc/amavis/conf.d/50-user — DKIM 入站验证
$enable_dkim_verification = 1;

# 验证结果 → 插入 Authentication-Results 头部
# 格式: Authentication-Results: mx01.example.com; dkim=pass header.d=example.com
$allowed_dkim_author_signers = {
  'example.com'       => 1,  # 信任 example.com 的签名
  'corp.example.com'  => 1,
};

# DKIM 验证失败的处理
$final_dkim_fail_destiny = D_PASS;    # 不拒绝，仅标记
# DKIM 失败的邮件 SpamAssassin 会自动增加 DKIM_INVALID 规则命中
# 权重通常为 +1.0 ~ +1.5，取决于 SpamAssassin 内置规则
```

RFC 6376 §6.3 定义的验证流程：接收方（Amavis）从邮件头提取
`DKIM-Signature`
中的选择器
`s=`
和域
`d=`
，构造 DNS 查询
`s._domainkey.d`
取回公钥，用公钥对签名执行 RSA 或 Ed25519 验证。Amavis 的 perl-Mail-DKIM 模块自动完成这一流程，并在日志中输出结果。

## 七、Policy Bank：策略引擎深度定制

Policy Bank 是 Amavis 架构中最被低估的特性。它本质上是一张查表，按照"发件人 / 收件人 / 域"的三元组匹配到不同的策略集合。一个策略集合可以是全局参数的任意子集覆盖，允许对 VIP 用户、外域入站、出站邮件分别定义完全不同的扫描行为。

```
# /etc/amavis/conf.d/50-user — Policy Bank 完整配置

# 全局默认策略
$final_virus_destiny      = D_DISCARD;
$final_spam_destiny       = D_PASS;
$final_banned_destiny     = D_BOUNCE;
$final_bad_header_destiny = D_PASS;
$sa_kill_level_deflt     = 10.0;
@bypass_virus_checks_maps = (0);
@bypass_spam_checks_maps  = (0);

# ================================================================
# Policy Bank 定义
# ================================================================

# 策略 A: VIP 用户 — 降低垃圾阈值、禁用存档炸弹判定
$policy_bank{'VIP'} = {
  final_spam_destiny   => D_BOUNCE,       # 垃圾直接拒绝
  sa_kill_level_deflt  => 4.0,            # 严格阈值
  bypass_virus_checks_maps => [0],        # 仍然扫病毒
  final_archive_destiny => D_PASS,        # 不过滤归档（VIP 可能接收合规附件）
};

# 策略 B: 出站扫描（外发邮件不做垃圾检查、但须做 DKIM 签名）
$policy_bank{'OUTBOUND'} = {
  bypass_spam_checks_maps   => [1],       # 跳过垃圾检查
  bypass_banned_checks_maps => [1],       # 跳过附件禁令（员工可外发 .pdf 等）
  final_virus_destiny       => D_REJECT,  # 病毒仍然拒绝
  originating               => 1,         # 标记为本地发信 → 触发 DKIM 签名
};

# 策略 C: 营销平台（大附件、不做病毒扫描）
$policy_bank{'MARKETING'} = {
  bypass_virus_checks_maps  => [1],
  bypass_spam_checks_maps   => [1],
  bypass_banned_checks_maps => [1],
  final_destiny_by_ccat     => {
    CC_CLEAN, D_PASS,   # 全都放行
  },
};

# ================================================================
# 路由规则：根据条件分配到对应的 Policy Bank
# ================================================================
$interface_policy{'10024'} = 'AM.PDP-INCOMING';   # 入站端口默认策略

# 发件人 → 策略表
@sender_to_policy_bank_maps = (
  { '.' => 'AM.PDP-INCOMING' },                    # 默认入站策略
);

# 收件人映射
@recipient_to_policy_bank_maps = (
  { 'ceo@example.com'  => 'VIP' },
  { 'cfo@example.com'  => 'VIP' },
  { 'board@example.com' => 'VIP' },
  { '.'                => 'AM.PDP-INCOMING' },
);
```

Policy Bank 的匹配优先级：
`收件人映射 > 发件人映射 > 接口默认策略`
。这意味着一个发给 ceo@example.com 的邮件无论发件人是谁，都会进入 VIP 策略池。这一设计避免了在单一配置文件里堆叠复杂的
`if-else`
逻辑。

### 7.1 典型应用场景

7.1 典型应用场景

| 场景 | Policy Bank | 差异化的配置 |
| --- | --- | --- |
| 高管邮件 | VIP | 低垃圾阈值(4.0)、不过滤归档、通知安全团队 |
| 外发邮件 | OUTBOUND | 跳过垃圾检查、禁用附件禁令、启用 DKIM 签名 |
| 通知邮件(no-reply) | NOTIFICATION | 跳过全部检查、直接放行 |
| 高安全域 | STRICT | 多引擎病毒扫描、0 分垃圾阈值、RBL 额外查询 |
| 安全测试域 | TESTING | 旁路模式：记录但不拦截，用于策略验证 |

## 八、Bypass 与 Tempfail 机制

内容安全网关有一个根本性的矛盾：它既是安全防线，也是邮件流经的必经节点。当防病毒引擎崩溃或 SpamAssassin 超时时，Amavis 面临两个选择 — 拒绝所有邮件（导致正常业务中断，比邮件病毒更严重的故障），或者临时放行（短暂的防护缺口 vs 业务连续性）。

### 8.1 超时与降级配置

```
# /etc/amavis/conf.d/50-user — 超时与 bypass

# clamd 通信超时
$clamd_timeout = 120;  # clamd 扫描单封邮件最多等待 120 秒

# SpamAssassin 超时
$sa_timeout = 30;      # SA 扫描超时，超时后跳过的邮件不会被评分
# 注意：实际超时是 sa_timeout * 4 = 120s（SA 有多次重试机制）

# 防病毒扫描超时后的处理
$av_scanner_timeout = 120;  # 单次扫描超时
$av_scanner_retries = 2;    # 重试次数

# ============================
# L1 bypass: 临时故障放行
# ============================
# 定义：当某个扫描模块故障时，是否降级处理
# 0 = 不 bypass（邮件排队，等模块恢复）
# 1 = bypass（跳过故障模块，邮件正常流入）

@bypass_virus_checks_maps = (
  \%bypass_virus_checks,
  \@bypass_virus_checks_acl,
  \$bypass_virus_checks_re
);

# 全局 bypass_virus_checks = 0 → 病毒扫描失败时邮件 deferred
# 针对特定域 bypass_virus_checks = 1 → 扫描失败时放行

# ============================
# L2 tempfail: 临时故障代码
# ============================
$tempdir_cleanup_on_error = 0;  # 错误时保留临时文件以便排障
$child_timeout = 8 * 60;        # 子进程总超时 8 分钟

# 当 Amavis 自身无法处理（如 OOM、临时目录满）时返回 4xx
# Postfix 会将邮件留在 deferred 队列，按退避策略重试
```

### 8.2 故障模式表

8.2 故障模式表

| 故障类型 | SMTP 返回码 | 邮件队列行为 | 业务影响 |
| --- | --- | --- | --- |
| clamd socket 不可达 | 451 4.5.0 | 进入 deferred，5 分钟后重试 | 邮件延迟，不会丢失 |
| clamd 返回 ERROR | 451 4.5.0 | 如 bypass=0 则 deferred，如 bypass=1 则放行 | 取决于 bypass 配置 |
| SA 超时(未返回结果) | — | 跳过 SA 评分，邮件携带 SA 超时标记通过 | 短时垃圾漏过，不影响正常邮件 |
| 临时目录满 | 451 4.3.0 | deferred | 邮件延迟 |
| OOM (子进程被杀) | 451 4.3.0 | deferred，但 OOM Killer 可能反复触发 | 需降低 max\_servers |
| amavisd 守护进程崩溃 | 451 4.3.2 | Postfix smtp(8) 返回 DEFER | 所有邮件 deferred |

生产环境的最佳实践：在主配置中将
`bypass_virus_checks`
设为
`0`
（宁可延迟不可放毒），但在监控系统中设置二级阈值 — 当 deferred 队列中因 Amavis 故障积压的邮件数超过设定值时，由自动化脚本将 bypass 参数临时调整为
`1`
。这需要仔细权衡，因为放行一封带毒邮件对政企客户而言可能是安全事件。

## 九、监控与性能调优

### 9.1 日志分析

Amavis 的日志格式极其结构化，每封邮件处理完成后输出一行汇总日志，包含 Passed/Clean、Blocked (病毒)、Spam、Banned (附件) 四种结果的精确分类。这是运维监控的核心数据源。

```
# 典型的 Amavis 日志格式 (syslog: mail.info)
Jul  4 10:23:45 mx01 amavis[28471]: (28471-01) Passed CLEAN
  {RelayedOpenRelay}, [203.0.113.45]:54321 [203.0.113.45]
   -> ,
  Queue-ID: D4F8A2C0B9, Message-ID: ,
  mail_id: xYZ1pQ_abcdef, Hits: -2.5, size: 45823, 342ms

# 快速统计命令
# 今日处理总量
grep "Passed\|Blocked\|Quarantined" /var/log/mail.log | wc -l

# 病毒拦截数
grep "Blocked INFECTED" /var/log/mail.log | wc -l

# 垃圾拦截数（含评分）
grep "Blocked SPAM" /var/log/mail.log | awk '{print $NF}' | sort -n | tail -20

# 平均处理时间（毫秒）
grep "Passed CLEAN" /var/log/mail.log | \
  awk -F'[, ]' '{sum+=$(NF-1); count++} END {print sum/count "ms"}'

# 按处理结果分类统计（过去 1 小时）
grep "$(date +'%b %e %H')" /var/log/mail.log | \
  grep -oP '(Passed|Blocked) \w+' | sort | uniq -c | sort -rn
```

### 9.2 性能参数调优

```
# /etc/amavis/conf.d/50-user — 性能参数

# 并发进程数（核心参数）
$max_servers = 8;  # 同时处理的邮件数
# 估算：max_servers ≈ (CPU 核心数 × 1.5) ~ (CPU 核心数 × 2)
# 瓶颈通常在 I/O 而非 CPU，适度超配可以隐藏 disk I/O 延迟

# 最小空闲进程（预热池）
$min_servers = 2;   # 维持 2 个空闲子进程，避免冷启动延迟
$min_spare_servers = 1;

# 子进程生命周期
$max_servers_service_time = 3600;  # 每个子进程最多存活 1 小时（防止内存泄漏累积）
$max_requests = 1000;              # 每个子进程处理 1000 封邮件后重启

# MIME 解码与临时文件
$TEMPBASE = '$MYHOME/tmp';          # 临时文件目录（建议放在 SSD 上）
$MAXFILES = 1500;                   # 单封邮件最大部件数
$MAXLEVELS = 14;                     # MIME 嵌套最大层数
$MIN_EXPANSION_QUOTA = 100 * 1024;   # 100 KB
$MAX_EXPANSION_QUOTA = 300 * 1024 * 1024;  # 300 MB

# 邮件大小限制
$sa_mail_body_size_limit = 512 * 1024;  # SA 扫描正文最多 512KB（超过的部分不评分）
$sa_mail_body_size_limit_bounce = 256 * 1024;  # 退信邮件正文限制

# SQL/Redis 日志持久化（大数据分析用）
@storage_sql_dsn = (
  ['DBI:mysql:database=amavis;host=127.0.0.1;port=3306',
   'amavis', 'password']
);
$sql_select_policy = 'CONCAT(ccat," ",result)';
```

### 9.3 Bypass 监控脚本

```
#!/bin/bash
# /usr/local/sbin/amavis-bypass-monitor.sh
# 监控 Amavis 健康状态，自动切换 bypass 模式

AMAVIS_SOCKET="/var/run/clamav/clamd.sock"
DEFERRED_THRESHOLD=500
BYPASS_FLAG="/var/run/amavis-bypass.active"
LOG="/var/log/amavis-bypass-monitor.log"

# 检查 clamd 守护进程连通性
check_clamd() {
    echo "PING" | socat - UNIX-CONNECT:"$AMAVIS_SOCKET" 2>/dev/null
}

# 检查 Amavis 自身是否存活
check_amavis() {
    echo "QUIT" | timeout 5 socat - TCP:127.0.0.1:10024 2>/dev/null
}

# 统计 deferred 队列中因 Amavis 积压的邮件数
count_amavis_deferred() {
    mailq 2>/dev/null | grep -c "smtp-amavis"
}

main() {
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    if ! check_clamd; then
        echo "[$TIMESTAMP] WARN: clamd socket unreachable" >> "$LOG"

        # 检查 deferred 队列积压是否超过阈值
        DEFERRED_COUNT=$(count_amavis_deferred)
        if [ "$DEFERRED_COUNT" -gt "$DEFERRED_THRESHOLD" ] && [ ! -f "$BYPASS_FLAG" ]; then
            echo "[$TIMESTAMP] ALERT: deferred=$DEFERRED_COUNT > $DEFERRED_THRESHOLD" >> "$LOG"
            # 发出告警（可接入 Prometheus AlertManager 或企业微信）
            # 注意：不自动切换 bypass，而是触发 on-call 响应
            echo "[$TIMESTAMP] ACTION: Trigger on-call escalation" >> "$LOG"
        fi
    fi

    if ! check_amavis; then
        echo "[$TIMESTAMP] CRIT: amavisd unresponsive on :10024" >> "$LOG"
    fi
}

main
```

### 9.4 吞吐量基准参考

9.4 吞吐量基准参考

| 并发数 (max\_servers) | 单封处理时间 | 每小时吞吐 | 日均处理量 | 资源配置参考 |
| --- | --- | --- | --- | --- |
| 4 | ~380ms | ~37,800 | ~900K | 2C4G, HDD |
| 8 | ~420ms | ~68,500 | ~1.6M | 4C8G, SSD |
| 16 | ~480ms | ~120,000 | ~2.8M | 8C16G, SSD + 独立 clamd |
| 32 | ~550ms | ~209,000 | ~5.0M | 16C32G, NVMe + clamd 集群 |

实际压测中，单封处理时间随并发数增加而轻微上升（来自磁盘 I/O 竞争），而非线性恶化。瓶颈通常在
`$TEMPBASE`
所在磁盘的随机 I/O 而非 CPU：每封邮件平均创建 12–35 个临时文件用于 MIME 解码，这是 Amavis 性能分析中最容易被忽略的点。

## 十、安全加固 Checklist

十、安全加固 Checklist

| # | 加固项 | 配置位置 | 说明 |
| --- | --- | --- | --- |
| 1 | 回注端口仅允许 localhost | master.cf :10025 | `mynetworks=127.0.0.0/8` ，防止外部直接注入邮件 |
| 2 | clamd socket 权限最小化 | clamd.conf | `LocalSocketMode 660` ，仅 amavis 用户组可读写 |
| 3 | 禁用 Amavis SNMP 子代理 | amavisd.conf | `$enable_snmp = 0;` （默认），减少攻击面 |
| 4 | 限制 Amavis 进程的 open files | systemd unit | `LimitNOFILE=4096` ，防止 MIME 炸弹耗尽 fd |
| 5 | 日志脱敏 | amavisd.conf | `$log_templ = ...` 中去除完整收件人地址 |
| 6 | 临时目录隔离 | amavisd.conf | `$TEMPBASE=/var/spool/amavis/tmp` ，设独立分区防止 /tmp 满影响系统 |
| 7 | 定期清理病毒隔离区 | crontab | `0 3 * * * find /var/virusmails -mtime +30 -delete` |
| 8 | 禁止 Amavis 内嵌的 SQL 密码明文存储 | 50-user | 使用 `.my.cnf` 或环境变量 `$AMAVIS_SQL_PW` |
| 9 | 限制 SpamAssassin 网络查询 | local.cf | `dns_available yes` + `trusted_networks 127.0.0.0/8` 防止 SSRF |
| 10 | Amavis 运行用户非 root | amavisd.conf | `$daemon_user = 'amavis'; $daemon_group = 'amavis';` |

**参考来源：**
IETF RFC 2045 — Multipurpose Internet Mail Extensions (MIME) Part One: Format of Internet Message Bodies (1996)；
IETF RFC 2046 — MIME Part Two: Media Types (1996)；
IETF RFC 5321 — Simple Mail Transfer Protocol (2008)；
IETF RFC 6376 — DomainKeys Identified Mail (DKIM) Signatures (2011)；
IETF RFC 7208 — Sender Policy Framework (SPF) Version 1 (2014)；
IETF RFC 5782 — DNS Blacklists and Whitelists (2010)；
Postfix 官方文档 — SMTPD\_PROXY\_README / CONTENT\_INSPECTION\_README；
Amavisd-new 项目文档 — https://gitlab.com/amavis/amavis；
ClamAV 项目文档 — https://docs.clamav.net；
Apache SpamAssassin 项目文档 — https://spamassassin.apache.org；
M3AAWG Anti-Abuse Operations Best Practices — https://www.m3aawg.org。

### 相关文章

[反垃圾过滤引擎深度解析](/kb/anti-spam-filter-engine.html)
[DKIM 邮件签名配置指南](/kb/dkim-guide.html)
[邮件恶意软件投递分析](/kb/email-malware-analysis.html)
[邮件 DLP 数据防泄漏策略](/kb/email-dlp-strategy.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/amavis-content-security-gateway.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
