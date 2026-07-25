---
title: "邮件客户端自动发现协议完整指南"
source: "https://ztpop.net/kb/email-autodiscovery-protocol-complete-guide.html"
license: CC-BY 4.0
---

# 邮件客户端自动发现协议完整指南

## 1. 引言

邮件客户端自动发现（Auto Discovery）是指邮件客户端仅凭用户输入的邮件地址和密码，自动推断出 IMAP/POP3/SMTP 服务器地址、端口、加密方式和认证方法的过程。这项机制对用户体验至关重要——用户无需理解「IMAP 和 POP3 有什么区别」「垃圾邮件过滤是端口 587 还是 465」等技术细节。

邮件领域的自动发现并未统一为单一标准。目前业界存在六大主流机制：Exchange Autodiscover、Mozilla Autoconfig（含 ISPDB）、SRV 记录发现（RFC 6186）、iOS/macOS 配置文件、Android EAS 自动发现以及 GroupWise/第三方专有协议。各机制的优先级、适用范围和部署复杂度差异显著[1][2]。

## 2. Exchange Autodiscover

Autodiscover 是由微软为 Exchange/Outlook 设计的自动配置协议，在 Outlook 2007 及更高版本中作为唯一配置入口。其核心流程如下[3]：

### 2.1 发现顺序

Autodiscover 客户端依次尝试以下 URL，直至获取有效响应：

1. `https://Autodiscover.<domain>/Autodiscover/Autodiscover.xml`（首选）
2. `https://<domain>/Autodiscover/Autodiscover.xml`（次选）
3. SRV 记录 `_autodiscover._tcp.<domain>`（A 标签指向 HTTPS 服务器）

如果上述 HTTPS 请求均失败（如证书无效），Outlook 会 fallback 到 HTTP（不安全）并提示用户确认。

### 2.2 请求/响应格式

Autodiscover 使用 SOAP over HTTPS，请求体为：

```
POST /Autodiscover/Autodiscover.xml HTTP/1.1
Host: autodiscover.example.com
Content-Type: text/xml; charset=utf-8

<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006">
  <Request>
    <EMailAddress>user@example.com</EMailAddress>
    <AcceptableResponseSchema>http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a</AcceptableResponseSchema>
  </Request>
</Autodiscover>
```

成功响应包含协议、服务器、端口、SSL 标志和认证类型等关键配置：

```
<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006">
  <Response>
    <Account>
      <AccountType>email</AccountType>
      <Action>settings</Action>
      <Protocol>
        <Type>IMAP</Type>
        <Server>imap.example.com</Server>
        <Port>993</Port>
        <DomainRequired>off</DomainRequired>
        <LoginName>user@example.com</LoginName>
        <SPA>off</SPA>
        <SSL>on</SSL>
        <AuthRequired>on</AuthRequired>
      </Protocol>
      <Protocol>
        <Type>SMTP</Type>
        <Server>smtp.example.com</Server>
        <Port>587</Port>
        <DomainRequired>off</DomainRequired>
        <LoginName>user@example.com</LoginName>
        <SPA>off</SPA>
        <SSL>on</SSL>
        <AuthRequired>on</AuthRequired>
      </Protocol>
    </Account>
  </Response>
</Autodiscover>
```

### 2.3 部署注意事项

* **HTTPS 证书必须有效**：Autodiscover 端点证书的 CN/SAN 必须包含 Autodiscover.<domain>，且不被客户端信任链拒绝
* **CSO (Client-Side Object) 缓存**：Outlook 会将 Autodiscover 结果缓存在本地注册表中（约 24 小时），变更后需手动清除缓存
* **重定向支持**：Autodiscover 支持 HTTP 301/302 重定向到另一 HTTPS 端点，允许集中式配置服务器

## 3. Mozilla Autoconfig 与 ISPDB

Mozilla Thunderbird 自 3.0 起引入了 Autoconfig 机制，被 SeaMonkey、Postbox 等客户端广泛采用。它与 Exchange Autodiscover 的对等概念是：ISPDB（Internet Service Provider Database）[4]。

### 3.1 发现顺序

1. **本地 ISPDB 数据库**：Thunderbird 内置的配置列表
2. **远程 ISPDB**：`https://autoconfig.thunderbird.net/v1.1/<domain>`
3. **域内 Autoconfig URL**：`https://autoconfig.<domain>/mail/config-v1.1.xml?emailaddress=user@example.com`
4. **域内 HTTP 回退**：`http://autoconfig.<domain>/mail/config-v1.1.xml`

### 3.2 Autoconfig XML 格式

```
<?xml version="1.0" encoding="UTF-8"?>
<clientConfig version="1.1">
  <emailProvider id="example.com">
    <domain>example.com</domain>
    <displayName>Example Mail</displayName>
    <displayShortName>Example</displayShortName>

    <incomingServer type="imap">
      <hostname>imap.example.com</hostname>
      <port>993</port>
      <socketType>SSL</socketType>
      <authentication>password-cleartext</authentication>
      <username>%EMAILADDRESS%</username>
    </incomingServer>

    <outgoingServer type="smtp">
      <hostname>smtp.example.com</hostname>
      <port>587</port>
      <socketType>STARTTLS</socketType>
      <authentication>password-cleartext</authentication>
      <username>%EMAILADDRESS%</username>
    </outgoingServer>
  </emailProvider>

  <webMail>
    <loginPage>https://mail.example.com</loginPage>
    <loginPageFavicon>https://mail.example.com/favicon.ico</loginPageFavicon>
  </webMail>
</clientConfig>
```

关键占位符：`%EMAILADDRESS%`（完整邮箱地址）、`%EMAILLOCALPART%`（@ 之前部分）、`%REALNAME%`（显示名称）。强烈建议使用 `%EMAILADDRESS%` 作为登录名，与 OAuth 2.0 的认证形式保持一致。

### 3.3 ISPDB 贡献

ISPDB（<https://autoconfig.thunderbird.net>）是 Mozilla 维护的公共配置数据库，邮箱服务商可提交 PR 将自己的域配置纳入。Thunderbird 用户输入邮箱后先查本地/远程 ISPDB，若命中则零配置完成。这为中小型邮件服务商提供了无需运营基础设施的自动发现途径。

提交方法：`git clone https://github.com/thunderbird/ispdb`，在 `mail/` 目录下创建 `example.com.xml`，PR 合并后所有 Thunderbird 用户即可自动发现。

## 4. SRV 记录发现（RFC 6186）

RFC 6186 定义了通过 DNS SRV 记录实现邮件客户端自动发现的标准化方案[2]。这是最轻量的机制，无需 HTTPS 服务器——只需 DNS 区域配置。

### 4.1 记录格式

```
; IMAP over TLS
_imaps._tcp.example.com. 3600 IN SRV 10 1 993 imap.example.com.

; IMAP with STARTTLS
_imap._tcp.example.com.  3600 IN SRV 10 1 143 imap.example.com.

; POP3 over TLS
_pop3s._tcp.example.com. 3600 IN SRV 10 1 995 pop3.example.com.

; POP3 with STARTTLS
_pop3._tcp.example.com.  3600 IN SRV 10 1 110 pop3.example.com.

; SMTP Submission (STARTTLS)
_submission._tcp.example.com. 3600 IN SRV 10 1 587 smtp.example.com.

; SMTP Submission (TLS)
_submissions._tcp.example.com. 3600 IN SRV 10 1 465 smtp.example.com.
```

### 4.2 客户端查询行为

RFC 6186 §3 规定，客户端应优先尝试 SRV 发现，仅在无响应或超时时 fallback 到传统域名猜测（如 imap.example.com）[2]。优先级（Priority）值越低优先级越高，相同优先级时按权重（Weight）比例分配。

### 4.3 局限性

* SRV 记录仅提供服务器地址和端口，不包含登录名格式、OAuth 端点等元信息
* 客户端对 SRV 的支持度不一——Apple Mail、K-9 Mail 支持良好，Outlook 桌面版不支持
* 无法表达「支持 OAuth 2.0」等高级特性

## 5. iOS/macOS 配置文件

Apple 提供 .mobileconfig 配置文件，这是 iOS 和 macOS 原生邮件客户端的零配置方案。管理员可通过 MDM 或网页分发配置文件，其中嵌入了完整的邮件服务器参数[5]。

### 5.1 配置文件结构

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>EmailAccountDescription</key>
      <string>公司邮箱</string>
      <key>EmailAccountName</key>
      <string>用户显示名</string>
      <key>EmailAccountType</key>
      <string>EmailTypeIMAP</string>
      <key>EmailAddress</key>
      <string>user@example.com</string>
      <key>IncomingMailServerAuthentication</key>
      <string>EmailAuthPassword</string>
      <key>IncomingMailServerHostName</key>
      <string>imap.example.com</string>
      <key>IncomingMailServerPortNumber</key>
      <integer>993</integer>
      <key>IncomingMailServerUseSSL</key>
      <true/>
      <key>IncomingMailServerUsername</key>
      <string>user@example.com</string>
      <key>OutgoingMailServerAuthentication</key>
      <string>EmailAuthPassword</string>
      <key>OutgoingMailServerHostName</key>
      <string>smtp.example.com</string>
      <key>OutgoingMailServerPortNumber</key>
      <integer>587</integer>
      <key>OutgoingMailServerUseSSL</key>
      <true/>
      <key>OutgoingMailServerUsername</key>
      <string>user@example.com</string>
      <key>OutgoingPasswordSameAsIncoming</key>
      <true/>
    </dict>
  </array>
  <key>PayloadDisplayName</key>
  <string>企业邮件配置</string>
  <key>PayloadIdentifier</key>
  <string>com.example.email-profile</string>
  <key>PayloadRemovalDisallowed</key>
  <false/>
  <key>PayloadType</key>
  <string>Configuration</string>
  <key>PayloadUUID</key>
  <string>(UUID 字符串)</string>
  <key>PayloadVersion</key>
  <integer>1</integer>
</dict>
</plist>
```

### 5.2 分发方式

* **MDM 推送**：通过 Apple MDM 协议静默安装
* **网页下载**：HTTP(S) 链接点击安装（iOS 12.1+ 需 HTTPS）
* **AirDrop**：本地近场分发

配置文件可以锁定部分字段（如服务器地址不可修改），适合集中管理场景。但 iOS 14.5+ 引入的「邮件私密保护」会覆盖部分邮件跟踪保护设置，需注意兼容性。

## 6. 跨平台自动配置最佳实践

### 6.1 推荐组合策略

覆盖所有主流客户端的最优策略是「三层配置」：

| 层 | 机制 | 覆盖客户端 | 部署成本 |
| --- | --- | --- | --- |
| 1 | DNS SRV (RFC 6186) | Apple Mail, K-9, Thunderbird (fallback) | 低（仅 DNS） |
| 2 | Mozilla Autoconfig (HTTPS) | Thunderbird, Postbox, SeaMonkey | 中（单 XML 文件） |
| 3 | Exchange Autodiscover (HTTPS) | Outlook 桌面版 | 中高（HTTP API） |
| (补充) | .mobileconfig 下载 | iOS/macOS 原生邮件 | 低（单文件托管） |

### 6.2 服务器侧实现（Nginx 示例）

```
# 统一的自动发现反向代理配置
server {
    listen 443 ssl http2;
    server_name autoconfig.example.com autodiscover.example.com;

    ssl_certificate     /etc/ssl/certs/autodiscover.pem;
    ssl_certificate_key /etc/ssl/private/autodiscover.key;

    # Thunderbird Autoconfig (RFC-style domain-based)
    location /mail/config-v1.1.xml {
        alias /var/www/autoconfig/example.com.xml;
        default_type application/xml;
    }

    # Exchange Autodiscover SOAP endpoint
    location /Autodiscover/Autodiscover.xml {
        proxy_pass http://127.0.0.1:8080/autodiscover;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # iOS/macOS .mobileconfig distribution
    location /profile.mobileconfig {
        alias /var/www/mobileconfig/email-profile.mobileconfig;
        default_type application/x-apple.aspen-config;
    }
}
```

### 6.3 优先级冲突处理

如果同一个域名同时部署了多种自动发现机制，客户端的行为因平台而异：

* Outlook：仅使用 Autodiscover，忽略 SRV
* Thunderbird：优先远程 ISPDB，其次 Autoconfig URL，最后本地数据库
* Apple Mail：优先 SRV，其次域名猜测，不支持 Autoconfig

因此，不同机制间不必保持配置完全一致——SRV 可以只返回 IMAP 基础信息，Autodiscover 可以附带更丰富的 OAuth 设置。但服务器地址和端口务必一致，否则用户邮箱可能在切换客户端时出现配置断裂。

## 7. 故障排查工具

### 7.1 测试 DNS SRV

```
# 使用 dig 验证 SRV 记录
dig _imaps._tcp.example.com SRV +short
# 期望输出: 10 1 993 imap.example.com.

dig _submission._tcp.example.com SRV +short
# 期望输出: 10 1 587 smtp.example.com.
```

### 7.2 测试 Autodiscover

```
# 模拟 Outlook Autodiscover 请求
curl -k -X POST \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006">
  <Request><EMailAddress>user@example.com</EMailAddress>
    <AcceptableResponseSchema>http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a</AcceptableResponseSchema>
  </Request>
</Autodiscover>' \
  https://autodiscover.example.com/Autodiscover/Autodiscover.xml -o autodiscover-response.xml
```

### 7.3 测试 Autoconfig

```
curl -s https://autoconfig.example.com/mail/config-v1.1.xml | xmllint --format -
# 确认 XML 结构完整，主机名可解析
```

## 参考文献

1. RFC 6186 — Use of SRV Records for Locating Email Submission/Access Services. IETF, March 2011. Section 3 (SRV Record Definitions), Section 4 (Client Behavior).
2. RFC 8314 — Cleartext Considered Obsolete: Use of TLS for Email Submission and Access. IETF, January 2018. Section 3 (Submission and Access Protocol Ports), Section 4 (Implicit vs Explicit TLS).
3. Exchange Autodiscover Protocol — Microsoft Documentation. MS-ASDS: Exchange Autodiscover and SOAP Response Format. Section 2.2.1.1 (Discovery Sequence).
4. Mozilla Thunderbird Autoconfiguration — Mozilla Developer Network. Thunderbird Automatic Configuration Documentation. ISPDB Schema v1.1.
5. Apple Configuration Profile Reference — Apple Developer Documentation. Payload Management and Email Payload. Section EmailAccount (IMAP/POP3 Settings).
6. RFC 2595 — IMAP/POP AUTHorize Extension for Simple Challenge/Response. IETF, June 1999. Section 2 (TLS negotiation for IMAP/POP3).

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-autodiscovery-protocol-complete-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
