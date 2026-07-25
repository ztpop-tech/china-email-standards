---
title: "MTA-STS 强制邮件传输加密策略深度解析 — RFC 8461：基于 HTTPS 的 TLS 策略分发与执行"
source: "https://ztpop.net/kb/mta-sts-guide.html"
license: CC-BY 4.0
---

# MTA-STS 强制邮件传输加密策略深度解析 — RFC 8461：基于 HTTPS 的 TLS 策略分发与执行

## 引言：STARTTLS 为什么不够

SMTP 协议诞生于互联网早期，彼时没有人设想邮件传输需要加密。TLS 是后来嫁接到 SMTP 上的，具体机制就是 RFC 3207 定义的 STARTTLS 扩展。它的工作方式很简单：SMTP 客户端先以明文建立连接，发送
`EHLO`
获取服务器能力列表，如果服务器在响应中宣告了
`STARTTLS`
，客户端可以发送
`STARTTLS`
命令触发 TLS 握手升级。这个过程听上去合理，但它有一个致命的假设：信道上的通信内容是可信的。

现实是，处于网络路径上的中间人可以拦截服务器返回的 EHLO 响应，把其中的
`STARTTLS`
标记删除，再转发给客户端。客户端看到的是一个"不支持 STARTTLS"的服务器，于是回退到明文传输。这就是学界所称的
**STRIPTLS 降级攻击**
— 攻击者不需要破解 TLS 密码学，只需要删除一行明文协商消息就够了。RFC 3207 本身定义了 STARTTLS，但它也明确把是否加密的选择权留给了连接双方的内置策略，没有提供任何机制阻止降级。
[RFC 3207]

到 2018 年，IETF 发布了 RFC 8461，正式定义了 MTA Strict Transport Security — 一个从域名所有者角度强制声明"给我的邮件必须走 TLS，而且证书必须可信"的协议框架。它的设计思路直接借鉴了 Web 领域的 HTTP Strict Transport Security（HSTS，RFC 6797），将"策略声明 → 缓存 → 强制检查"的模式搬到了邮件传输场景。

> RFC 8461, Section 1: "The STARTTLS extension to SMTP provides a way for SMTP connections to be protected by TLS, but it is vulnerable to downgrade attacks because it relies on an in-band negotiation mechanism. MTA-STS provides a mechanism for mail domains to declare their ability to receive TLS-protected SMTP connections and to specify whether a sending MTA should refuse to deliver messages when a TLS-secured connection cannot be established."

## 一、MTA-STS 两步发现机制

MTA-STS 的核心是一套双通道策略分发体系：
**DNS TXT 记录宣告策略存在**
，
**HTTPS 端点承载策略内容**
。
[RFC 8461, §3]
两个通道各司其职 — DNS 做轻量级的能力宣告和版本控制，HTTPS 做完整的策略数据分发和完整性保障。

完整流程（发件方 MTA 视角）如下：

1. **第一步 — DNS 查询：**
   发件方 MTA 在投递邮件到
   `example.com`
   时，首先查询
   `_mta-sts.example.com`
   的 TXT 记录。如果记录不存在，MTA 按传统 STARTTLS 逻辑继续投递，不会中断。
2. **第二步 — 版本比对：**
   如果 DNS TXT 返回了有效的 STS 记录，发件方解析其中的
   `id`
   字段，与本地缓存中已存储的策略 ID 比较。如果 ID 一致且缓存未过期，直接使用缓存策略，跳过 HTTPS 拉取。
3. **第三步 — HTTPS 拉取：**
   如果是首次见到该域的策略，或缓存已过期/ID 已变更，发件方通过 HTTPS 请求
   `https://mta-sts.example.com/.well-known/mta-sts.txt`
   。这个 HTTPS 连接的证书必须通过 Web PKI 验证链校验。
   [RFC 8461, §3.2]
4. **第四步 — 策略执行：**
   发件方解析策略 JSON，按
   `mode`
   字段决定后续行为 —
   `none`
   意味着没有强制要求、
   `testing`
   仅报告不拒绝、
   `enforce`
   强制要求证书验证且 MX 主机名精确匹配。
5. **第五步 — 策略缓存：**
   发件方将策略 JSON 本地存储，有效期由
   `max_age`
   字段决定。在缓存有效期内，不再发起 HTTPS 拉取。缓存过期后重新走 DNS → HTTPS 流程。

## 二、DNS TXT 记录：轻量级策略宣告

DNS TXT 记录是 MTA-STS 的入口。它有两个字段都必须出现：
[RFC 8461, §3.1]

二、DNS TXT 记录：轻量级策略宣告

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| `v=STSv1` | 协议版本标识，必须为 STSv1（当前唯一版本） | `v=STSv1` |
| `id=NNNNNNNNN` | 策略序号，1–32 位数字。发件方用它判断策略是否更新 | `id=2024070400` |

**序号递增机制**
是 MTA-STS 版本控制的核心。RFC 8461 要求发件方 MTA 将 DNS TXT 中返回的
`id`
与缓存策略中的
`id`
做字典序比较：如果新 ID 比缓存 ID 大（按字符串比较），认为策略已更新，需要重新拉取 HTTPS 策略文件。这意味着域所有者每次修改策略 JSON 后，不仅要更新 HTTPS 端点上的文件，还要同步递增 DNS TXT 中的
`id`
值。
[RFC 8461, §4.1]

在实践中，一种可靠的做法是将策略序号关联到日期：

```
_mta-sts.example.com.  IN  TXT  "v=STSv1; id=2024070400;"
```

这里
`2024070400`
表示 2024 年 7 月 4 日第 0 次修改。一天内多次修改时递增末尾序号（01, 02, ...）。查询命令：

```
dig TXT _mta-sts.example.com +short
# 输出示例:
# "v=STSv1; id=2024070400;"
```

注意几个容易踩的坑：TXT 记录的分号后面可以有空格，也可以没有，RFC 8461要求发送方解析时必须兼容两种格式。记录中不能存在除
`v`
和
`id`
之外的标签，否则整个记录应当视为无效。记录中标签的顺序不固定，但
`v=STSv1`
必须存在。

## 三、HTTPS 策略文件：JSON 策略正文

策略 JSON 文件托管在域名的特定路径下：
`https://mta-sts./.well-known/mta-sts.txt`
。这个路径是固定的，不可更改。
[RFC 8461, §3.2]
发件方 MTA 通过 HTTPS GET 请求获取，响应的
`Content-Type`
必须为
`text/plain`
，HTTP 状态码必须为
`200`
。

用 curl 模拟发件方 MTA 拉取策略：

```
curl -v https://mta-sts.example.com/.well-known/mta-sts.txt
```

策略 JSON 的完整字段定义如下：
[RFC 8461, §3.2, §4.1]

三、HTTPS 策略文件：JSON 策略正文

| 字段 | 类型 | 必需 | 说明 |
| --- | --- | --- | --- |
| `version` | string | 是 | 固定值 `"STSv1"` |
| `mode` | string | 是 | `"enforce"` / `"testing"` / `"none"` |
| `mx` | array of strings | 是 | 允许接收邮件的 MX 主机名列表，证书 SAN 必须精确匹配其中之一 |
| `max_age` | integer | 是 | 策略缓存存活时间，单位秒。范围 86400–31557600 |

一个完整的策略文件示例：

```
{
  "version": "STSv1",
  "mode": "enforce",
  "mx": [
    "mx1.example.com",
    "mx2.example.com"
  ],
  "max_age": 604800
}
```

### 3.1 mode 字段：三种运行模式

[RFC 8461, §4.1]
定义了三种模式，决定了收件域对 TLS 的强制程度：

3.1 mode 字段：三种运行模式

| mode | 行为 | 适用阶段 |
| --- | --- | --- |
| `none` | 声明该域不支持 MTA-STS。发件方即使之前缓存了 enforce 策略也应停止强制检查。一般用于彻底退出 MTA-STS | 退出 |
| `testing` | TLS 验证失败仅记录日志/发送 TLS 报告，不拒绝投递。相当于静默监控期 | 部署初期 |
| `enforce` | TLS 握手失败 或 证书主机名不匹配 → 发件方 MTA **必须拒绝投递** 并返回 DSN 通知发件人 | 稳定运行 |

### 3.2 max\_age 的取舍

`max_age`
控制策略在发件方缓存中的存活时间。这是一个需要权衡的参数：
[RFC 8461, §4.1]

* **短周期（如 86400，即 1 天）：**
  策略故障可以快速恢复。如果错误发布了 enforce 策略导致投递中断，发件方在 24 小时内就会重新拉取纠正后的策略。缺点是发件方需要频繁发起 HTTPS 请求，对大型邮件服务商来说增加了 HTTPS 端点负载。
* **长周期（如 604800，即 7 天）：**
  减少 HTTPS 拉取频率，降低策略服务器的压力。但当策略有误时，恢复需要更长时间，因为发件方在缓存过期前不会重新拉取。
* **极长周期（如 31557600，即约 1 年）：**
  这种做法不推荐。一旦策略文件或 HTTPS 证书出现问题，长达一年的缓存失效窗口意味着所有发件方都会锁定在过时或错误的策略上。

推荐值：
**testing 阶段设为 86400（1 天）**
，方便快速迭代；
**enforce 阶段设为 604800（7 天）**
，在稳定性与缓存效率之间取得平衡。Google 的公开 MTA-STS 策略使用了 86400，Microsoft 的 Office 365 域使用了 604800 — 两种选择各有合理性，取决于你对 HTTPS 基础设施的自信程度。

## 四、策略验证与证书主机名匹配

当
`mode`
为
`enforce`
时，发件方 MTA 在完成 TLS 握手后需要执行一项关键检查：
**服务器证书的主题别名（Subject Alternative Name, SAN）必须精确匹配策略 JSON 中
`mx`
数组里的某个主机名**
。
[RFC 8461, §4.2]

这个规则的严格程度经常被低估。举一个典型反面案例：

* 策略文件中
  `mx`
  列表：
  `["mx.example.com"]`
* 实际 SMTP 连接的主机：
  `mx.example.com`
  （通过 MX 记录解析得到）
* 服务器 TLS 证书 SAN：
  `*.example.com`

在这个例子中，Wildcard 证书
`*.example.com`
按照 RFC 6125 的主机名匹配规则
**可以**
覆盖
`mx.example.com`
。但如果证书 SAN 是
`mail.example.com`
，而策略文件中列出的是
`mx.example.com`
，验证会失败 — RFC 8461 要求的是精确匹配，不支持别名推断。

另外，策略文件的 HTTPS 端点
`mta-sts.example.com`
自身也需要有效的 TLS 证书。如果该证书过期或不受信任，发件方 MTA 无法获取策略文件，会回退到 STARTTLS 机会加密（或者如果有未过期的缓存策略则使用缓存策略）。
[RFC 8461, §3.4]

## 五、Testing → Enforce 分阶段上线

直接跳入
`enforce`
模式是一种高风险操作。任何一个配置错误（证书 SAN 不匹配、策略文件 404、DNS TXT 记录拼写错误）都可能导致部分发件方 MTA 拒绝向你的域投递邮件。RFC 8461 推荐的部署路径如下：
[RFC 8461, §5]

五、Testing → Enforce 分阶段上线

| 阶段 | 配置 | 持续时间 | 目的 |
| --- | --- | --- | --- |
| 第一阶段 | 部署 DNS TXT 记录，策略 mode = `testing` ，max\_age = 86400 | 2–4 周 | 验证双通道均可达，观察 TLS-RPT 报告 |
| 第二阶段 | 维持 testing 模式，分析 TLS-RPT 报告中的失败事件 | 1–2 周 | 修复证书 SAN 不匹配、TLS 版本不支持等问题 |
| 第三阶段 | 切换至 mode = `enforce` ，max\_age 延长至 604800 | 长期 | 正式启用强制加密策略 |

每次修改策略后，
**必须同步更新 DNS TXT 记录中的
`id`
值**
— 这是触发发件方重新拉取策略的唯一信号。如果只更新 HTTPS 策略文件而不更新 DNS ID，已缓存该域策略的发件方不会知道策略变了。

## 六、TLS-RPT：监控闭环

MTA-STS 本身只解决"强制声明"问题，不提供反馈机制。RFC 8460 定义的 SMTP TLS Reporting（TLS-RPT）填补了这个空白。它的工作流向与 MTA-STS 的方向相反：
**发件方 MTA 在投递邮件后，周期性地将 TLS 连接结果报告发送回收件方域**
。
[RFC 8460]

TLS-RPT 也使用 DNS 宣告入口：

```
_smtp._tls.example.com.  IN  TXT  "v=TLSRPTv1; rua=mailto:tls-reports@example.com"
```

报告以 JSON 格式通过邮件发送到
`rua`
地址。报告内容包括：

* 发件方 MTA 的身份
* 每次连接的结果：
  `success`
  /
  `sts-policy-fetch-error`
  /
  `sts-policy-invalid`
  /
  `validation-failure`
* TLS 版本和密码套件
* 证书链详情（可选）
* MTA-STS 策略是否被应用（
  `applied`
  /
  `not-applied`
  ）
* 受影响的消息数量

一份典型的 TLS-RPT 报告片段：

```
{
  "organization-name": "sender.example.net",
  "date-range": {
    "start-datetime": "2026-07-03T00:00:00Z",
    "end-datetime": "2026-07-04T00:00:00Z"
  },
  "policies": [{
    "policy": {
      "policy-type": "sts",
      "policy-string": ["version: STSv1", "mode: enforce"],
      "policy-domain": "example.com"
    },
    "summary": {
      "total-successful-session-count": 1240,
      "total-failure-session-count": 3
    },
    "failure-details": [{
      "result-type": "certificate-host-mismatch",
      "failed-session-count": 3,
      "receiving-mx-hostname": "mx2.example.com"
    }]
  }]
}
```

这个报告揭示了
`mx2.example.com`
上
**发生了 3 次证书主机名不匹配**
— 直接定位到了需要修复的目标。在 testing 阶段，这类报告是无价的排错依据；进入 enforce 阶段后，报告帮助确认策略在实际运行中是否如预期工作。

RFC 8689 对 TLS-RPT 进行了扩展，引入了
**列表模式（list mode）**
让 rua 地址可以指定多个报告接收端点以支持冗余。
[RFC 8689]

## 七、MTA-STS vs DANE：两种信任模型

邮件传输安全的另一条技术路径是 DANE（DNS-Based Authentication of Named Entities），由 RFC 6698 定义、RFC 7672 针对 SMTP 做了专项扩展。两者的核心分歧在于信任锚：
[RFC 7672]

七、MTA-STS vs DANE：两种信任模型

| 维度 | MTA-STS（RFC 8461） | DANE for SMTP（RFC 7672） |
| --- | --- | --- |
| 策略载体 | HTTPS + DNS TXT | DNSSEC 签名的 TLSA 记录 |
| 信任锚 | Web PKI（CA 体系） | DNSSEC 信任链 |
| 证书来源 | 公共 CA 签发的 TLS 证书 | 任意 TLS 证书（包括自签名），指纹绑定 |
| 策略粒度 | 域级（enforce/testing/none） | 端口级（usage: 0=DANE-EE, 1=DANE-TA, 2=PKIX-EE, 3=PKIX-TA） |
| 部署前提 | 控制 DNS + 运营 HTTPS 端点 | 域必须启用 DNSSEC |
| 证书过期处理 | 无需修改 DNS，更换证书后自动生效 | 需更新 TLSA 记录中的证书哈希 |
| 降级防护 | 策略缓存期间强制检查 | DNSSEC 验证失败直接阻断 |
| 生态成熟度 | Google/Gmail、Microsoft 365 已部署 | 主要在欧洲（荷兰、德国、北欧）采用 |

MTA-STS 的优势在于
**入网门槛低**
：不需要启用 DNSSEC，只需要控制域名的 DNS 记录和运行一个 HTTPS 端点。这在当前的互联网生态中几乎为零成本 — 几乎所有邮件域都已经有 Web 服务器和 TLS 证书。相比之下，DANE 要求域启用 DNSSEC，而在截止 2026 年的全球部署率中，DNSSEC 验证率仍然低于 40%（基于 APNIC 统计数据）。

DANE 的优势在于
**安全性更强**
：它不依赖 CA 体系，不需要信任任何第三方。域所有者通过 DNSSEC 签名直接宣告自己的 TLS 证书指纹或 CA 公钥，攻击者即使控制了某个 CA 也无法绕过。NIST SP 800-177 Rev.1 也指出 DANE 在理论上比基于 CA 的方案具有更强的安全属性。
[NIST SP 800-52 Rev.2]

两者不是互斥关系。推荐做法是
**MTA-STS 先行 + DANE 补强**
：先用 MTA-STS 快速覆盖大部分发件方（尤其是 Google 和 Microsoft 生态），同步推进 DNSSEC 启用，最终同时部署 MTA-STS 和 DANE。发件方 MTA 在同时遇到两种策略时，通常会同时执行两种验证（两者失败任意一个即拒收）。
[RFC 8461, §6]

## 八、Postfix MTA-STS 集成

在发件方侧（出站 MTA），Postfix 通过外部守护进程实现 MTA-STS 策略查询。主流的集成方案是
**mta-sts-daemon**
（由 Google 维护的开源项目），配合 Postfix 的
`smtp_tls_policy_maps`
指令。

**安装 mta-sts-daemon（Debian/Ubuntu）：**

```
apt install mta-sts-daemon
```

**Postfix main.cf 配置：**

```
# MTA-STS 策略查找
smtp_tls_policy_maps = socketmap:unix:/run/mta-sts/daemon.sock:mta-sts

# 启用 TLS 安全级别为 dane（允许 MTA-STS 和 DANE 覆盖）
smtp_tls_security_level = dane

# MTA-STS 策略缓存目录
smtp_tls_policy_cache = btree:/var/lib/mta-sts/policy_cache

# TLS 日志级别（testing 阶段建议设为 1）
smtp_tls_loglevel = 1

# 要求 TLSv1.2 及以上
smtp_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

# 强制证书验证（enforce 模式下生效）
smtp_tls_verify_cert_match = nexthop, dot-nexthop
```

配置完成后重启 Postfix 并确保 mta-sts-daemon 以 systemd 服务形式运行：

```
systemctl restart postfix
systemctl enable --now mta-sts-daemon
systemctl status mta-sts-daemon
```

验证 mta-sts-daemon 是否正常工作：

```
# 查看 MTA-STS 策略缓存
ls /var/lib/mta-sts/

# 测试特定域的 MTA-STS 策略（需安装 mta-sts-query 工具）
mta-sts-query example.com

# 查看日志确认策略获取过程
journalctl -u mta-sts-daemon -f
```

### 收件方侧（入站 MTA）配置

对于收件方，Postfix 本身不需要额外配置 MTA-STS — 策略由 DNS 和 HTTPS 端点承载。但 TLS 服务器配置需要确保：

```
# 收件方 Postfix main.cf 配置（TLS 服务端部分）
smtpd_tls_cert_file = /etc/letsencrypt/live/mx.example.com/fullchain.pem
smtpd_tls_key_file  = /etc/letsencrypt/live/mx.example.com/privkey.pem

# 要求 TLSv1.2 及以上
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

# 推荐密码套件（NIST SP 800-52 Rev.2 指南）
smtpd_tls_ciphers = high
smtpd_tls_mandatory_ciphers = high

# 启用 TLS 日志
smtpd_tls_loglevel = 1
```

NIST SP 800-52 Rev.2 对 TLS 服务器配置提供了更详细的密码套件指导，其中指出应优先使用支持 AEAD 的密码套件（如 TLS\_ECDHE\_RSA\_WITH\_AES\_256\_GCM\_SHA384），禁用所有基于 CBC 模式的套件以避免 Padding Oracle 攻击。
[NIST SP 800-52 Rev.2, §3.3.3]

### 策略 HTTPS 端点搭建（Nginx）

Nginx 配置示例，为 mta-sts 子域提供策略文件服务：

```
server {
    listen 443 ssl http2;
    server_name mta-sts.example.com;

    ssl_certificate     /etc/letsencrypt/live/mta-sts.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mta-sts.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    root /var/www/mta-sts;

    location /.well-known/mta-sts.txt {
        default_type text/plain;
    }
}
```

## 九、常见排错

### 9.1 DNS TXT 记录不存在或被忽略

症状：TLS-RPT 报告中显示
`no-policy-found`
或根本没有 MTA-STS 相关结果。

排查步骤：

```
# 查询 DNS TXT 记录
dig TXT _mta-sts.example.com

# 如果返回 NXDOMAIN 或空结果，确认记录名是否正确
# 常见错误：把记录挂在 example.com 下而非 _mta-sts 子域

# 正确的 DNS 配置（BIND 格式）
_mta-sts.example.com.  IN  TXT  "v=STSv1; id=2024070400;"

# 检查记录是否已传播
dig TXT _mta-sts.example.com @8.8.8.8
dig TXT _mta-sts.example.com @1.1.1.1
```

### 9.2 HTTPS 端点不可达

症状：TLS-RPT 报告中出现
`sts-policy-fetch-error`
。

```
# 测试 HTTPS 端点可达性
curl -v https://mta-sts.example.com/.well-known/mta-sts.txt

# 常见问题：
# 1. 证书过期或不受信任 → 检查证书链
openssl s_client -connect mta-sts.example.com:443 -servername mta-sts.example.com

# 2. Content-Type 不对 → 必须是 text/plain
curl -I https://mta-sts.example.com/.well-known/mta-sts.txt
# 期望：Content-Type: text/plain

# 3. 防火墙/负载均衡拦截 → 从外部 IP 测试
curl -v --resolve mta-sts.example.com:443:1.2.3.4 \
  https://mta-sts.example.com/.well-known/mta-sts.txt
```

### 9.3 证书 SAN 不匹配

这是 enforce 模式下最常见的拒绝原因。症状：
`certificate-host-mismatch`
错误。

```
# 验证 MX 主机的证书 SAN 是否覆盖策略文件中列出的主机名
echo | openssl s_client -connect mx1.example.com:25 -starttls smtp 2>/dev/null \
  | openssl x509 -noout -text | grep -A 1 "Subject Alternative Name"

# 示例输出应该包含策略 mx 列表中的所有主机名：
# DNS:mx1.example.com, DNS:mx2.example.com

# 如果用的是 Wildcard 证书 *.example.com，确认 MX 主机名落在 Wildcard 匹配范围内
```

一个常见的配置陷阱：MX 记录返回
`mail.example.com`
，DNS 解析将其 CNAME 到
`mx1.hosting-provider.com`
，实际 SMTP 连接到达
`mx1.hosting-provider.com`
但该主机的证书 SAN 里没有
`mail.example.com`
。解决方法是直接从 MX 记录指向证书 SAN 覆盖的最终主机名，或让托管商在证书 SAN 中加入你的域主机名。

### 9.4 DNS ID 与策略文件不同步

修改了 HTTPS 策略文件但忘记更新 DNS TXT 中的 id → 发件方使用旧的缓存策略 → 新策略不生效。这是运维中最常被遗漏的步骤。
[RFC 8461, §4.1]

```
# 检查 DNS 和 HTTPS 是否一致
# 步骤 1: 查询当前的 DNS id
dig TXT _mta-sts.example.com +short

# 步骤 2: 查询 HTTPS 策略文件的最后修改时间
curl -sI https://mta-sts.example.com/.well-known/mta-sts.txt | grep Last-Modified

# 如果 Last-Modified 在 DNS id 对应时间之后，说明不同步
```

### 9.5 DNS TXT 记录解析问题

如果 DNS TXT 记录中存在换行或引号问题，发件方可能无法正确解析。RFC 8461 要求发件方将 TXT 记录中的所有字符串片段拼接后再解析。
[RFC 8461, §3.1]

```
# 验证 TXT 记录的原始格式
dig TXT _mta-sts.example.com

# 期望看到单条完整的记录，而非被 DNS 协议分片的长字符串
# 如果不确定，检查 DNS 托管商是否正确处理了 TXT 记录的引号
```

## 十、策略规划与安全考虑

### 10.1 证书自动续期与策略联动

MTA-STS 的有效性依赖于三个证书链的持续有效：策略端点 HTTPS 证书、每台 MX 主机的 TLS 证书。如果使用 Let's Encrypt 等 90 天有效期的证书，建议：

* 使用 certbot 的自动续期钩子在证书更新后调用 mta-sts-daemon 刷新策略缓存
* 将 max\_age 设置为可接受证书故障的最长时间（例如 604800 = 7 天，意味着如果 on-prem 证书因故障未能续期，发件方仍可能使用过期的缓存策略最多 7 天）
* 为策略 HTTPS 端点的证书设置比 MX 证书更早的续期预警

### 10.2 策略冗余与回退

RFC 8461 允许策略中列出多个 MX 主机，这天然实现了冗余。但如果某个 MX 下线且未及时从策略中移除，发件方会在 enforce 模式下拒绝向该 MX 投递，但可能通过其他 MX 重试（取决于发件方 MTA 的实现）。

回退到
`mode: none`
是紧急情况下的安全阀。发件方 MTA 看到
`none`
后会在一个
`max_age`
周期内停止对该域的 MTA-STS 检查，回退到传统 STARTTLS 行为。但这个过程受缓存周期限制 — 已在 enforce 缓存期的发件方不会立即收到 none 信号。

### 10.3 对抗中间人降级

MTA-STS 的防御面是有限的。它解决了 STARTTLS 的 STRIPTLS 问题，但无法防御以下攻击：

* 攻击者在首次 DNS TXT 查询时屏蔽记录 — 发件方认为该域没有 MTA-STS 策略，直接走 STARTTLS 机会加密。
  [RFC 8461, §8.1]
* 攻击者控制了受信任的 CA 并签发伪造证书 — 因为 MTA-STS 使用 Web PKI 作为信任锚。
  [RFC 8461, §8.2]
* 攻击者能够同时拦截 DNS 和 HTTPS 流量 — 在全局范围可以降级到无 MTA-STS 的状态。

对于需要对抗国家级中间人攻击的场景，DANE + DNSSEC 提供了更强的安全保障。MTA-STS 的定位是
**以零或极低成本为全体邮件流提供有效的降级防护**
，而非为高价值目标提供完美安全保障。
[RFC 8461, §8]

## 总结

MTA-STS 为邮件传输安全提供了一条低门槛、高回报的技术路径。它的核心价值在于填上了 STARTTLS 机会加密的最大漏洞 — 中间人降级攻击 — 且不需要像 DANE 那样依赖尚未普及的 DNSSEC 基础设施。

推荐的部署路线：先建立 DNS TXT 和 HTTPS 策略端点，在 testing 模式下运行 2–4 周，通过 TLS-RPT 报告确认没有异常后切换到 enforce。同时规划 DNSSEC 启用和 DANE 部署作为中长期安全增强。

**参考来源：**
IETF RFC 8461 — SMTP MTA Strict Transport Security (MTA-STS)；IETF RFC 8460 — SMTP TLS Reporting；IETF RFC 8689 — SMTP TLS Reporting Extension for Multiple RUA Destinations；IETF RFC 7672 — SMTP Security via Opportunistic DANE TLS；IETF RFC 3207 — SMTP Service Extension for Secure SMTP over TLS；IETF RFC 6125 — Representation and Verification of Domain-Based Application Service Identity；NIST SP 800-52 Rev.2 — Guidelines for the Selection, Configuration, and Use of TLS Implementations。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mta-sts-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
