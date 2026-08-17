---
title: "Postfix 3.10 与 OpenSSL 3.5 后量子加密：ML-KEM 邮件传输防护实践"
source: "https://ztpop.net/kb/postfix-310-openssl35-post-quantum.html"
license: CC-BY 4.0
---

# Postfix 3.10 与 OpenSSL 3.5 后量子加密：ML-KEM 邮件传输防护实践

## 背景：Harvest-now-decrypt-later 威胁与邮件传输

「先收割、后解密」（Harvest-now-decrypt-later，HNDL）是后量子时代最主要的邮件安全威胁模型：攻击者现在记录加密的 SMTP 会话流量，待未来量子计算机成熟后离线破解。对邮件系统而言，这意味着今天通过 STARTTLS 协商的传统密钥交换（如 X25519、ECDHE-RSA）保护的邮件内容，可能在数年后被批量解密。

传统邮件传输链路两大弱点放大该风险：SMTP STARTTLS 是机会主义加密（大量流量仍可能在无加密或弱加密状态下传输），且密钥交换算法依赖经典密码学（无法抵御 Shor 算法）。应对 HNDL 的核心手段是混合密钥交换（hybrid key exchange）：将经典 ECDH 与后量子 KEM 结合，即使量子计算破解了其中一种，另一种仍能保证会话密钥安全。

## 技术原理：ML-KEM 与 X25519MLKEM768 混合协商

ML-KEM（Module-Lattice Key Encapsulation Mechanism）是 NIST 于 2024-08-13 正式标准化的后量子密钥封装机制（FIPS 203），基于格密码（Module-LWE）问题，提供 IND-CCA2 安全。参数集 ML-KEM-768 提供 256 位经典/后量子混合安全强度，与 AES-256 相当。

在 TLS 1.3 中，IETF 定义了混合密钥交换组 X25519MLKEM768（draft-kwiatkowski-tls-ecdhe-mlkem），将 X25519（经典 ECDH）与 ML-KEM-768 封装并行执行，两者输出经组合函数派生会话密钥。TLS 1.3 组协商保证不支持的对端自动回退 X25519，兼容性良好。

OpenSSL 3.5.0（2025-04-08 发布）将 X25519MLKEM768 设为默认 TLS keyshare 之一（与 X25519 并列），并把混合 PQC KEM 组加入默认支持的组列表并优先协商——这是主流 TLS 库首次将后量子密钥交换默认启用。

## Postfix 3.10 的落地

Postfix 3.10（2025-02 发布）通过与 OpenSSL 3.5 的集成，将 ML-KEM 后量子密钥交换带入邮件传输层：

- **tls_eecdh_auto_curves**：控制 TLS 椭圆曲线组列表（含 X25519MLKEM768 等混合组）；为空时使用 OpenSSL 默认配置。
- **tls_ffdhe_auto_groups**：控制 TLS 有限域 DH 组列表；为空时使用 OpenSSL 默认配置。
- **TLSRPT（SMTP TLS Reporting，RFC 8460）**：Postfix 3.10 新增支持，可通过 DNS _smtp._tls 策略接收对方每日 TLS 连接成功/失败汇总报告，用于发现降级攻击或配置错误。
- **RFC 8689（SMTP Require TLS Option）**：支持 TLS-Required: no 消息头，允许对不敏感邮件在无法强制 TLS 时仍请求投递（如 TLSRPT 摘要报告本身）。
- **smtpd_hide_client_session**：新增隐私设置，可隐藏 Received 头中客户端会话详细信息（适用于 MUA 提交服务）。

Postfix 3.10 的「支持后量子加密」本质是前向兼容——编译时链接 OpenSSL 3.5+，即可自动获得默认启用的 X25519MLKEM768 协商能力，管理员通过上述两个参数可显式控制或观察组选择。

## 部署配置

### 前置条件

```
# 1. 安装 OpenSSL 3.5+
# Debian/Ubuntu
apt install openssl libssl-dev
openssl version   # 应显示 OpenSSL 3.5.x

# 2. 编译或安装 Postfix 3.10+
make -f Makefile.init makefiles "CCARGS=-DUSE_TLS -I/usr/include/openssl"
make && make install
```

### main.cf 配置示例

```
# /etc/postfix/main.cf
smtp_tls_security_level = may
smtpd_tls_security_level = may

# 显式指定椭圆曲线组（含混合后量子组 X25519MLKEM768）
tls_eecdh_auto_curves = X25519MLKEM768, X25519, prime256v1
# 有限域 DH 组（留空则使用 OpenSSL 默认）
tls_ffdhe_auto_groups =

smtp_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_mandatory_ciphers = high

# 隐私：隐藏 Received 头中客户端会话详情
smtpd_hide_client_session = yes
```

### 验证协商结果

```
# 查看日志中 TLS 握手协商的曲线组
grep -i "TLS" /var/log/mail.log | grep -i "curve\|kex\|group"

# 测试对端是否支持后量子组
openssl s_client -connect smtp.example.com:25 -starttls smtp \
  -groups X25519MLKEM768 -servername smtp.example.com -brief
```

## TLSRPT（RFC 8460）与 RFC 8689 衔接

TLSRPT（RFC 8460）通过 DNS _smtp._tls TXT 记录声明报告接收地址，发送方将 TLS 连接成功/失败统计以每日摘要回报，帮助发现 STARTTLS 降级攻击或证书验证失败。RFC 8689（Require TLS Option）允许发件方在消息级声明 TLS-Required 头，提供细粒度 TLS 豁免。两者与后量子协商形成互补：后量子保护「会话密钥不被未来破解」，TLSRPT 保护「连接不被降级」，RFC 8689 提供细粒度豁免。

## 兼容性注意事项

- **对端支持度**：X25519MLKEM768 需对端 TLS 栈也支持该组；不支持的对端自动回退 X25519，不会导致连接失败，但后量子保护仅在双方都支持时生效。
- **OpenSSL 版本门槛**：只有链接 OpenSSL 3.5+ 的 Postfix 才具备默认后量子协商；3.2-3.4 需显式配置且非默认。
- **性能开销**：ML-KEM-768 封装/解封计算量大于 X25519 但远小于 RSA 密钥交换；握手耗时增加通常在亚毫秒级，对邮件吞吐影响可忽略。
- **日志与监控**：升级后核查邮件日志确认实际协商组；若大量连接回退 X25519，可通过 TLSRPT 观察趋势。

## 升级路径建议

1. 升级 OpenSSL 至 3.5+ 并重新编译/安装 Postfix 3.10+。
2. 先以默认配置运行观察 1-2 周，核查日志中协商组分布。
3. 确认无异常后，可显式固定 tls_eecdh_auto_curves 优先 X25519MLKEM768。
4. 配置 TLSRPT DNS 记录并订阅报告，持续监控 TLS 失败与降级。
5. 结合 MTA-STS（RFC 8461）或 DANE（RFC 7672）策略发布，形成「后量子 + 强制加密 + 报告」三层防护。

## 权威参考来源

- Postfix 3.10.0 官方发布说明（postfix.org）
- OpenSSL 3.5 NEWS（openssl.org / GitHub）
- RFC 8460：SMTP TLS Reporting（TLSRPT，IETF Standards Track，2018-09）
- RFC 8689：SMTP Require TLS Option（IETF Standards Track，2019-11）
- NIST FIPS 203：Module-Lattice-Based Key-Encapsulation Mechanism（ML-KEM）
- IETF draft-kwiatkowski-tls-ecdhe-mlkem：混合 ECDHE-ML-KEM 密钥交换组
- RFC 8461：SMTP MTA Strict Transport Security (MTA-STS)
- RFC 7672：SMTP Security via Opportunistic DANE TLS
