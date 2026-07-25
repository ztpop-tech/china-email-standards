---
title: "GB/T 37002-2018 电子邮件系统安全技术要求解读"
source: "https://ztpop.net/kb/gbt37002-email-security-standard.html"
license: CC-BY 4.0
---

# GB/T 37002-2018 电子邮件系统安全技术要求解读

GB/T 37002-2018 电子邮件系统安全技术要求解读

GB/T 37002-2018 电子邮件系统安全技术要求深度解读

2026-07-04

ztpop.net 知识库

GB/T 37002-2018《信息安全技术 电子邮件系统安全技术要求》由国家市场监督管理总局与中国国家标准化管理委员会于 2018 年 12 月 28 日联合发布，2019 年 7 月 1 日正式实施，归口全国信息安全标准化技术委员会（SAC/TC 260）。该标准由 国家信息技术安全研究中心、中国电子技术标准化研究院、深圳奥联信息安全技术有限公司、国家信息中心、中国信息安全测评中心 等机构联合起草，全文共 24 页，是截至目前国内唯一专门针对电子邮件系统安全技术的国家标准。

标准覆盖范围广泛：各级政务部门的互联网邮件系统、电子政务外网和内网邮件系统、企事业单位的专网邮件系统，涵盖设计、建设、使用、测试评估全生命周期，同时也直接约束邮件相关产品的设计、制造、测试与服务。对照国际层面，IETF 在邮件安全领域以协议级标准为主（RFC 6376 DKIM、RFC 7208 SPF、RFC 7489 DMARC、RFC 8555 S/MIME 4.0），NIST SP 800-177 提供可信邮件指南——这些标准解决的是"怎么做"的问题，而 GB/T 37002-2018 解决的是"做到什么程度才算安全"的评估框架问题。

一、标准总体架构：两大支柱

GB/T 37002-2018 的内核由两大支柱构成，分别对应"系统应该具备哪些安全能力"和"如何证明这些能力真实有效"两个递进问题：

表：Gbt37002 Email Security Standard

| 支柱 | 核心问题 | 核心内容 |
| --- | --- | --- |
| **安全功能要求**    （第 6 章） | 系统应具备哪些安全能力？ | 标识与鉴别、访问控制、安全审计、数据完整性、数据保密性、通信安全、残余信息保护、接口安全、收发过程保护 |
| **安全保障要求**    （第 7-9 章） | 如何证明安全能力真实有效？ | SSOIS 安全保障目标、TOE 安全功能规范、生命周期保障（配置管理、交付运行、开发、指导性文档、生命周期支持、脆弱性评定） |

这种双支柱结构借鉴了 ISO/IEC 15408（通用准则，CC）的评估方法论——安全功能要求定义了系统的"安全轮廓"（Security Profile），安全保障要求则规定了评估者如何验证这些功能要求已被正确实现。二者缺一不可：一个声称具备访问控制能力的系统，如果无法提供设计文档、测试报告和脆弱性分析来证明，其安全声明就不具备可信度。

二、安全功能要求详解

安全功能要求覆盖邮件系统从用户登录到邮件投递的完整链路，共计七个核心域外加两个扩展域：

2.1 标识与鉴别（Identification & Authentication）

表：Gbt37002 Email Security Standard

| # | 控制项 | 基本级 | 增强级 |
| --- | --- | --- | --- |
| 1 | 用户身份唯一标识 | 要求 | 要求 |
| 2 | 身份鉴别机制 | 用户名+口令 | 多因素鉴别（口令+证书/动态令牌/生物特征） |
| 3 | 口令复杂度策略 | 最小长度 8 位，含大小写字母、数字、特殊字符中至少 3 类 | 最小长度 10 位，含上述全部 4 类，且禁止连续或重复字符 |
| 4 | 口令有效期与历史 | 最长 90 天，不可重复使用近 5 次 | 最长 60 天，不可重复使用近 10 次 |
| 5 | 登录失败锁定 | 连续失败 5 次锁定 30 分钟 | 连续失败 3 次锁定 30 分钟 + 告警 |
| 6 | 会话超时 | 空闲 30 分钟自动退出 | 空闲 15 分钟自动退出 |
| 7 | 鉴别信息存储 | 口令加密存储（至少 SHA-256 + salt） | 口令加密存储（至少 SHA-512 或 SM3 + salt），密钥与数据分离 |
| 8 | 登录通知 | — | 异地登录/新设备登录后向用户发送通知 |

**部署示例——Postfix+Dovecot 多因素认证配置：**

```
# /etc/dovecot/conf.d/10-auth.conf
# 启用 SASL 二层认证：先验证口令，再验证 OTP
auth_mechanisms = plain login

# /etc/dovecot/conf.d/auth-passwdfile.conf.ext
# 使用 Argon2id 替代 SHA-256 存储口令哈希
passdb {
  driver = passwd-file
  args = scheme=ARGON2ID username_format=%u /etc/dovecot/users.db
}

# PAM OTP 集成：第二因素
# /etc/pam.d/dovecot
auth required pam_unix.so
auth required pam_google_authenticator.so

# Postfix SASL 配置
# /etc/postfix/main.cf
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_auth_enable = yes
smtpd_tls_auth_only = yes  # 禁止明文传输认证信息
smtpd_sasl_security_options = noanonymous, noplaintext
```

2.2 访问控制（Access Control）

标准要求邮件系统实现基于角色的细粒度访问控制（RBAC），核心要点：

• 必须通过身份鉴别后方可访问授权功能，不可跳过认证环节直接访问资源。

• 访问控制策略需覆盖用户对自身邮箱的访问、管理员对系统的管理操作、第三方应用对 API 接口的调用三个维度。

• 增强级额外要求：访问控制粒度到达单个邮件夹/单封邮件级别，管理员操作需双人授权（如删除用户邮箱需两个管理员确认）。

• 默认拒绝原则：未明确授权的访问一律拒绝。

**部署示例——Dovecot ACL 实现邮件夹级权限：**

```
# /etc/dovecot/conf.d/90-acl.conf
mail_plugins = $mail_plugins acl

plugin {
  acl = vfile:/etc/dovecot/global-acls:cache_secs=300
  acl_shared_dict = file:/var/lib/dovecot/shared-mailboxes.db
}

# /etc/dovecot/global-acls
# 限制管理员对用户邮件的只读审计（不可删除/修改）
user=admin@example.com lr

# 用户邮箱目录下 dovecot-acl 文件示例
# 共享文件夹：市场部可读写，其他部门只读
owner user=alice lrwstipekxa
authenticated lr
group=marketing lrwstipek
group-override=marketing
```

2.3 安全审计（Security Audit）

安全审计是 GB/T 37002-2018 中条文最密集的章节之一，标准分五个子类规定审计要求：

表：Gbt37002 Email Security Standard

| 审计类别 | 必审字段 | 留存期 |
| --- | --- | --- |
| **管理员行为审计** | 操作时间、管理员账户、登录 IP、地理位置、登录方式、操作内容与结果 | ≥6 个月 |
| **用户登录审计** | 登录时间、邮件用户账户、登录 IP、地理位置、登录方式 | ≥6 个月 |
| **发信行为审计** | 发送时间、收件人、邮件主题、投递状态、是否撤回 | ≥6 个月 |
| **收信行为审计** | 收取时间、发件人、邮件主题、阅读状态 | ≥6 个月 |
| **账户配置变更审计** | 时间、操作账户、修改内容、修改结果 | ≥6 个月 |

增强级额外要求审计日志具备防篡改能力（如写入 WORM 介质或使用区块链哈希链）、审计记录实时告警、日志发送至独立审计服务器（syslog-ng/rsyslog over TLS）。

**部署示例——Postfix + rsyslog 实现结构化邮件审计：**

```
# /etc/rsyslog.d/30-mail-audit.conf
# 将邮件日志以 JSON 结构化格式发送至审计服务器
module(load="omfwd")
template(name="MailAuditJSON" type="list") {
    constant(value="{")
    constant(value="\"timestamp\":\"")     property(name="timereported" dateFormat="rfc3339")
    constant(value="\",\"hostname\":\"")   property(name="hostname")
    constant(value="\",\"program\":\"")    property(name="programname")
    constant(value="\",\"message\":\"")    property(name="msg" format="json-encode")
    constant(value="\"}\n")
}

# 仅审计关键邮件事件
if $programname startswith "postfix" and
   ($msg contains "status=sent" or
    $msg contains "status=bounced" or
    $msg contains "status=deferred" or
    $msg contains "sasl_username=") then {
    action(type="omfwd" target="10.0.1.100" port="6514"
           protocol="tcp" template="MailAuditJSON"
           StreamDriver="gtls" StreamDriverMode="1"
           StreamDriverAuthMode="x509/name"
           StreamDriverPermittedPeers="audit-server.example.com")
}

# 本地日志留存不少于 180 天（标准要求的 6 个月）
$MailLogRetention 180
```

2.4 数据完整性（Data Integrity）

标准从三个维度要求数据完整性保护：

**存储完整性：**
邮件在磁盘上的存储应具备完整性校验能力，防止静默数据损坏和篡改。基本级可采用文件系统级校验（如 ZFS checksum），增强级要求每条邮件记录附带单独的 HMAC 签名。

**传输完整性：**
SMTP/LMTP 传输链路应使用 TLS 1.2 及以上版本（RFC 8446 TLS 1.3 优先），国密场景下使用 TLCP（GB/T 38636-2020）替代。IMAP/POP3 同样需要加密传输。

**数字签名：**
增强级要求对发出的邮件支持 S/MIME 数字签名（RFC 8551），收件方可验证邮件在传输过程中未被篡改。国密体系下使用 SM2 签名算法（GB/T 32918.2-2016）替代 RSA，SM3 哈希（GB/T 32905-2016）替代 SHA-256。

**部署示例——Postfix S/MIME 签名与 DKIM 双重保护：**

```
# /etc/postfix/main.cf
# DKIM（RFC 6376）— 域级完整性验证
milter_default_action = accept
milter_protocol = 6
smtpd_milters = inet:localhost:8891
non_smtpd_milters = inet:localhost:8891

# /etc/opendkim.conf
Domain   example.com
KeyFile  /etc/opendkim/keys/202607.private
Selector 202607
Canonicalization relaxed/simple
Mode     sv
# 使用 ed25519 替代 RSA（RFC 8463）
SignatureAlgorithm ed25519-sha256

# Dovecot S/MIME 客户端证书集成
# /etc/dovecot/conf.d/10-ssl.conf
ssl_cert =
```

2.5 数据保密性（Data Confidentiality）

保密性要求覆盖"传输中"（in transit）和"静态存储"（at rest）两个状态：

•
**传输保密性：**
SMTP、IMAP、POP3、ManageSieve 等所有邮件协议端口必须启用 TLS 加密。基本级接受 TLS 1.2，增强级强制 TLS 1.3 或启用 MTA-STS（RFC 8461）+ DANE（RFC 7672）防止降级攻击。

•
**存储保密性：**
增强级要求邮件在服务端磁盘上以加密形态存储。可使用 LUKS/dm-crypt 全盘加密或应用层加密（如 S/MIME 服务端加密存储）。

•
**端到端加密：**
增强级建议支持端到端邮件加密——发件人使用收件人公钥加密邮件正文，邮件服务端无法解密——这与 S/MIME 信封加密（RFC 8551）和 PGP（RFC 9580）的目标一致。

```
# /etc/postfix/main.cf — 强制 TLS 传输
smtpd_tls_security_level = may               # 公共入站：接受TLS
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_mandatory_ciphers = high

smtp_tls_security_level = dane               # 出站：优先DANE验证
smtp_tls_CApath = /etc/ssl/certs
smtp_tls_session_cache_database = btree:/var/lib/postfix/smtp_scache

# MTA-STS 策略（RFC 8461）
# https://mta-sts.example.com/.well-known/mta-sts.txt
# version: STSv1
# mode: enforce
# mx: mail.example.com
# max_age: 86400
```

2.6 通信安全（Communication Security）

除传输加密外，通信安全章节还覆盖以下层面的保护：

•
**邮件过滤：**
系统应支持按域、IP、发件人地址的收发白名单/黑名单。增强级额外要求支持 SPF/DKIM/DMARC 验证和基于内容的反垃圾引擎。

•
**防恶意代码：**
系统应对邮件附件进行病毒扫描。增强级要求支持沙箱行为分析。

•
**抗抵赖：**
发送邮件的行为不可否认。增强级通过数字签名实现发送方抗抵赖。

•
**邮件撤回：**
基本级支持组织内部邮件在接收方未阅读时撤回。增强级支持已读邮件的撤回通知及全链路撤回记录。

2.7 接口安全（Interface Security）

标准对邮件系统对外 API 的安全约束要点：

* 第三方应用调用邮件系统接口前必须通过身份鉴别（OAuth 2.0 / API Key / mTLS）
* 接口会话必须设定生命周期（JWT 含 exp 声明，access\_token 有效期 ≤ 2h）
* 对所有接口输入进行合法性检测，防御注入、XSS、CSRF、参数污染等攻击
* 接口资源权限最小化：按最小必要原则限定每个第三方应用可访问的数据范围
* 记录所有接口调用日志，保留期 ≥ 6 个月

2.8 收发过程保护

• 邮件过滤：能接收或拒收指定域的邮件。

• 邮件大小限制：设置单封邮件和单次会话的最大传输大小。

• 投递状态通知：邮件发送/投递成功后向发件人返回投递状态（DSN, RFC 3464）。

• 增强级：支持 SMTP 发信频率限制防止滥用（如单用户每小时 ≤ 500 封）。

三、安全保障要求：SSOIS 框架

安全保障要求定义了邮件系统安全评估的框架——不是"系统应该做什么"，而是"如何证明系统确实做到了"。这套框架在标准中称为 SSOIS（Security Standard of Organizational Information System），由三个递进层级组成：

表：Gbt37002 Email Security Standard

| 评估组件 | 核心内容 | 借鉴来源 |
| --- | --- | --- |
| **安全保障目标** （ASE） | 定义 TOE（评估对象，此处即邮件系统）的安全目标、安全环境假设、威胁模型、组织安全策略 | ISO/IEC 15408-1 ASE 类 |
| **TOE 安全功能** （ADV + ATE） | 安全功能规范（SFR）、实现表示、TSF 内部结构、覆盖深度与功能测试 | ISO/IEC 15408-2/3 ADV + ATE 族 |
| **生命周期保障** （ALC） | 配置管理、交付与运行、开发安全、指导性文档、生命周期支持、脆弱性评定 | ISO/IEC 15408-3 ALC 类 |

生命周期保障是安全测评中最容易被忽视的一环。标准明确要求邮件系统产品具备：

•
**配置管理（CM）：**
唯一标识每个版本，记录所有变更，确保测评版本与交付版本一致。

•
**交付与运行：**
安全交付流程（防篡改传输、完整性校验），部署指南中明确安全配置基线。

•
**指导性文档：**
管理员手册中必须包含安全功能配置方法、审计日志解读、应急响应流程。

•
**脆弱性评定：**
厂商需提供至少近 12 个月的漏洞修复记录，并进行渗透测试。增强级要求独立的第三方渗透测试报告。

四、安全等级划分：基本级 vs 增强级

GB/T 37002-2018 将邮件系统安全划分为两个等级：
基本级
和
增强级
。两个等级不是简单的"安全加固叠加"关系，而是对应不同的威胁模型和目标使用场景：

表：Gbt37002 Email Security Standard

| 对比维度 | 基本级 | 增强级 |
| --- | --- | --- |
| **适用场景** | 普通企事业单位内部邮件系统，威胁主要来自外部攻击者和内部误操作 | 政务部门、关键信息基础设施运营者、处理敏感数据（个人信息/商业秘密/国家秘密）的系统 |
| **威胁模型** | 攻击者具有基本攻击能力，但资源有限 | 攻击者具备较高攻击能力和资源，包括 APT 组织 |
| **身份鉴别** | 用户名+口令 | 多因素认证（口令+证书/OTP/生物特征） |
| **密码算法** | 国际算法（RSA-2048、AES-128/256、SHA-256） | 支持国密算法（SM2/SM3/SM4）或等国密+国际算法双栈 |
| **传输加密** | TLS 1.2 | TLS 1.3 或 TLCP（GB/T 38636-2020），DANE + MTA-STS |
| **存储加密** | 可选 | 强制服务端加密存储或端到端加密 |
| **网络隔离** | 逻辑隔离 | 物理或虚拟化隔离，管理面与业务面分离 |
| **审计日志** | 本地存储 ≥ 6 个月 | 实时远程同步 + 防篡改保护 + 留存 ≥ 12 个月 |
| **脆弱性评定** | 厂商自评 | 独立第三方渗透测试 + 持续漏洞管理 |

关键理解：增强级不是"基本级加几个功能"，而是在整体安全保障强度上的等级提升。例如，基本级仅要求"支持审计功能"，增强级则要求"审计记录防篡改、实时告警、远程集中存储"——前者可以被具有系统权限的攻击者清空日志，后者即使系统被攻破，审计记录依然可追溯。

五、与等保 2.0 的映射关系

GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》（等保 2.0）是通用的网络安全防护基线，覆盖安全物理环境、安全通信网络、安全区域边界、安全计算环境、安全管理中心五大维度。邮件系统作为应用系统，在等保测评中属于"安全计算环境"层面的受评对象。

GB/T 37002-2018 与等保 2.0 的关系可以理解为"通用要求"与"领域专项要求"的互补——等保 2.0 告诉邮件系统"和其他系统一样，你需要做这些"，GB/T 37002 进一步指出"作为邮件系统，你还需要额外做到这些"。以下是关键控制项的映射：

表：Gbt37002 Email Security Standard

| GB/T 37002-2018 章节 | GB/T 22239-2019 对应控制点 | 补充关系 |
| --- | --- | --- |
| 标识与鉴别 | 8.1.4.2 身份鉴别（第三级 a~h） | 等保要求通用身份鉴别；GB/T 37002 增加邮件特有的登录审计字段(IP/地理位置/登录方式) |
| 访问控制 | 8.1.4.3 访问控制 | 等保要求主体-客体访问控制；GB/T 37002 增加邮件夹级粒度 + 管理员双人授权 |
| 安全审计 | 8.1.4.4 安全审计 | 等保要求通用审计；GB/T 37002 细化到五类邮件特有审计对象 + 6 个月最小留存 |
| 数据完整性 | 8.1.4.6 数据完整性 | 等保要求传输/存储完整性；GB/T 37002 额外要求 DKIM + S/MIME 签名 |
| 数据保密性 | 8.1.4.7 数据保密性 | 等保要求传输保密性；GB/T 37002 额外要求 TLS 1.3/国密 + 服务端加密存储 |
| 通信安全 | 8.1.3.2 通信传输 | GB/T 37002 增加收件域过滤、发信频率限制、邮件撤回等邮件特有能力 |
| 密码支持 | GB/T 39786-2021 密码应用要求 | 国密 SM2/SM3/SM4 需满足密码应用安全性评估（密评）第三级要求 |

**实操提示：**
在实际等保测评中，邮件系统作为"应用系统"或"安全产品"申报测评时，测评机构会交叉引用 GB/T 37002-2018 补充验证邮件特定安全要求。如果邮件系统通过了 GB/T 37002 增强级评估，通常可直接覆盖等保 2.0 第三级中与邮件系统相关的全部控制项。

六、国密算法与邮件加密的对应关系

GB/T 37002-2018 增强级明确要求支持国密算法体系，这在政务、金融、能源等关键信息基础设施领域是刚性需求。以下为国密算法在邮件系统中的确切映射：

表：Gbt37002 Email Security Standard

| 国密算法 | 标准引用 | 国际对应 | 邮件系统中的应用位置 |
| --- | --- | --- | --- |
| **SM2** （椭圆曲线公钥密码） | GB/T 32918 系列 | ECC / RSA | (1) S/MIME 证书签名与加密 (2) TLS 双向认证中的客户端证书 (3) 邮件数字签名 |
| **SM3** （密码杂凑） | GB/T 32905-2016 | SHA-256 / SHA-3 | (1) 口令哈希存储 (2) DKIM 签名哈希算法 (3) 日志完整性链哈希 (4) 文件完整性校验 |
| **SM4** （分组密码） | GB/T 32907-2016 | AES-128/256 | (1) TLS/TLCP 对称加密 (2) 邮件全文服务端加密存储 (3) 数据库敏感字段加密 (4) 配置文件加密 |
| **TLCP** （传输层密码协议） | GB/T 38636-2020 | TLS 1.3 | SMTP/IMAP/POP3/HTTPS 全协议加密传输 |

**部署示例——OpenSSL 国密补丁启用 TLCP：**

```
# 编译安装支持国密的 OpenSSL（基于 Tongsuo/BabaSSL 分支）
git clone https://github.com/Tongsuo-Project/Tongsuo.git
cd Tongsuo
./config --prefix=/usr/local/tongsuo enable-ntls
make -j$(nproc) && make install

# Postfix 链接国密版 OpenSSL
export LD_LIBRARY_PATH=/usr/local/tongsuo/lib:$LD_LIBRARY_PATH

# /etc/postfix/main.cf — TLCP 国密加密配置
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_ciphers = high
# 指定 SM2 国密证书
smtpd_tls_cert_file = /etc/pki/tls/certs/mail-sm2.crt
smtpd_tls_key_file  = /etc/pki/tls/private/mail-sm2.key

# 验证国密连接
# openssl s_client -connect mail.example.com:465 \
#   -sigalgs SM2:SHA256 -ciphersuites TLS_SM4_GCM_SM3
```

**密码应用安全性评估（密评）注意：**
2021 年发布的 GB/T 39786-2021《信息安全技术 信息系统密码应用基本要求》将密码应用安全分为四个等级。邮件系统在等保三级环境中需满足密评三级要求——即所有密码算法必须使用国密系列或经国家密码管理局认可的算法。这意味着仅使用 TLS 1.3（ECDHE-RSA-AES256-GCM）的国际密码套件无法通过密评。

七、邮件系统测评中的关键控制项与常见问题

结合多轮等保测评与邮件系统安全评估的实践经验，以下是测评中最高频的失分点和对应的整改策略：

表：Gbt37002 Email Security Standard

| # | 高频失分项 | 标准条款 | 整改策略 |
| --- | --- | --- | --- |
| 1 | 未启用 TLS 或使用已废弃版本（SSLv3/TLS 1.0） | 6.1.1.5.5 通信安全 | 禁用 TLS 1.0/1.1，配置 MTA-STS 策略；使用 testssl.sh 或 sslyze 验证所有端口 |
| 2 | 口令策略不符合复杂度要求 | 6.1.1.5.1 标识与鉴别 | 在认证模块强制应用密码复杂度（至少 8 位、3 类字符组合），不可仅靠前端 JS 校验 |
| 3 | 审计日志不完整或可被管理员删除 | 6.1.1.5.3 安全审计 | 将审计日志通过 syslog TLS 实时发送至独立审计服务器；本地日志使用 append-only 属性（chattr +a） |
| 4 | 未实现登录地域异常检测 | 6.1.1.5.1 增强级 | 基于 GeoIP 数据库检测登录 IP 地理位置变化，异地登录触发二次验证或告警 |
| 5 | WebMail 接口未防护 CSRF/XSS | 6.1.1.5.4 接口安全 | 所有表单使用 CSRF Token、Content-Security-Policy 头、输入输出编解码、HttpOnly + Secure Cookie |
| 6 | 未实现 SMTP 发信频率限制 | 6.1.1.5.5 增强级 | 配置 Postfix anvil 服务 + policyd 限制单用户/单 IP 发信频率；告警阈值设为 200 封/小时 |
| 7 | 管理员操作无审批机制 | 6.1.1.5.2 增强级 | 关键操作（删除邮箱、导出数据、修改全局策略）需双人授权或工作流审批 |
| 8 | 未定期进行脆弱性评估 | 第 9 章 生命周期保障 | 每季度至少一次漏洞扫描 + 年度第三方渗透测试 + CVE 持续监控与修复 |

**部署示例——Postfix 发信频率限制配置：**

```
# /etc/postfix/main.cf
# 启用 anvil 服务（连接/速率统计）
anvil_status_update_time = 600s
smtpd_client_connection_rate_limit = 30    # 单IP每时间窗口最大连接数
smtpd_client_message_rate_limit = 100      # 单IP每时间窗口最大邮件数
smtpd_client_recipient_rate_limit = 200    # 单IP每时间窗口最大收件人数
smtpd_client_event_limit_exceptions = $mynetworks

# /etc/postfix/master.cf
# policyd 策略守护进程——基于 SASL 用户限制
policy  unix  -       n       n       -       0       spawn
  user=nobody argv=/usr/local/bin/policyd.pl

smtpd_recipient_restrictions =
    ...
    check_policy_service unix:private/policy

# policyd 基本限速逻辑（Perl 示例）
# 单 SASL 用户每 300 秒最多发送 50 封邮件
# 超过阈值返回 DEFER_IF_PERMIT "Rate limit exceeded"
```

八、标准实施建议与评估路线

对于计划依据 GB/T 37002-2018 进行邮件系统合规建设的组织，建议按以下阶段推进：

表：Gbt37002 Email Security Standard

| 阶段 | 任务 | 预计周期 |
| --- | --- | --- |
| **阶段 1：差距分析** | 对照标准条款逐项检查当前邮件系统，制作安全功能矩阵对照表，识别缺失项和不符合项 | 2-3 周 |
| **阶段 2：加固实施** | 部署 TLS 1.2+ 加密、配置口令策略、搭建独立审计服务器、实施 SPF/DKIM/DMARC | 4-8 周 |
| **阶段 3：国密改造** | （增强级）引入 SM2/SM3/SM4 密码套件、替换 TLS 为 TLCP、改造 S/MIME 国密兼容 | 8-12 周 |
| **阶段 4：制度配套** | 编制邮件系统安全管理制度（含口令管理、审计日志审阅、应急响应、变更管理、脆弱性管理流程） | 2-4 周 |
| **阶段 5：测评验证** | 委托具有资质的测评机构进行 GB/T 37002-2018 符合性测评或等保测评（带邮件专项验证） | 3-4 周 |
| **阶段 6：持续运维** | 季度漏洞扫描、年度渗透测试、日志定期审阅、策略持续优化 | 持续 |

与通用安全标准不同，邮件系统安全要求具有强领域特征：通用标准不会告诉你"审计日志需要包含发件人、收件人、投递状态"，也不会要求"邮件系统接口必须防止 CSRF"。这些细节写在 GB/T 37002-2018 的具体条文中，这也是将其作为邮件系统安全专项评估依据的价值所在。

结语

GB/T 37002-2018 是目前国内邮件系统安全领域最完整的规范性文件。它不只是合规清单——它的核心价值在于提供了一套可验证、可评估的安全能力框架。对照这份标准进行系统设计和测评，本质上是在回答一个根本问题：当有人声称"我们的邮件系统是安全的"时，这句话到底意味着什么。

从等保 2.0（GB/T 22239-2019）到密评（GB/T 39786-2021）再到本标准的增强级要求，中国的邮件系统安全标准体系已经形成一个层层递进的防护金字塔：等保定框架、密评定算法、37002 定领域深度。对于在政务、金融、能源等行业部署邮件系统的组织，建议至少在基本级达标，涉及敏感信息处理的系统向增强级看齐。

邮件安全从来不是单一产品的安全——它是一个链路安全问题，覆盖从用户设备到传输管道再到服务端存储的全过程。GB/T 37002-2018 的价值就在于把这些链路点映射为可度量、可审计、可改进的技术控制项。

[← 上一篇：邮件安全事件应急响应](/kb/email-incident-response.html)
[下一篇：邮件数据防泄漏（DLP）策略 →](/kb/email-dlp-strategy.html)

上海辰童科技有限公司

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gbt37002-email-security-standard.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
