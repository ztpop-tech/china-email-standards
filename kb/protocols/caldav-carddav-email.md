---
title: "邮件系统 CalDAV/CardDAV 集成 — 日历与通讯录同步"
source: "https://ztpop.net/kb/caldav-carddav-email.html"
license: CC-BY 4.0
---

# 邮件系统 CalDAV/CardDAV 集成 — 日历与通讯录同步

摘要：企业邮件系统不仅是信息交换通道，更是团队协作的中枢——日历共享、会议邀请、通讯录同步是企业日常协作的刚需。CalDAV（RFC 4791）和 CardDAV（RFC 6352）是基于 WebDAV 协议的日历和通讯录同步开放标准，可与邮件系统认证体系（IMAP/LDAP）深度集成，实现与 Thunderbird、Outlook、iOS/macOS 等主流客户端的双向同步。本文完整讲解协议原理、Radicale 开源服务器部署、DNS SRV 自动发现（RFC 6764）、客户端配置以及统一认证桥接方案。

**一、协议栈概览：WebDAV 之上的日历与通讯录标准**

CalDAV 和 CardDAV 均建立在 WebDAV（Web Distributed Authoring and Versioning, RFC 4918）协议之上。WebDAV 扩展了 HTTP/1.1，增加了资源集合（Collection）概念、PROPFIND 属性查询方法、REPORT 报告方法、以及基于 ETag 的乐观锁并发控制。CalDAV 在此基础上定义了日历资源（.ics 文件）的存取、查询和订阅协议。核心数据格式是 iCalendar（RFC 5545），定义了 VEVENT（事件）、VTODO（待办事项）、VJOURNAL（日志）、VFREEBUSY（忙闲状态）、VTIMEZONE（时区）等组件。一个典型的 .ics 日历事件包含 DTSTART（开始时间）、DTEND（结束时间）、SUMMARY（标题）、DESCRIPTION（描述）、LOCATION（地点）、ORGANIZER（组织者）、ATTENDEE（参与者）等属性。

CardDAV 的协议结构与 CalDAV 类似，核心数据格式是 vCard（RFC 6350）。vCard 定义了个人或组织的联系人信息，包括 FN（全名）、N（结构化姓名）、EMAIL、TEL、ADR（地址）、ORG（组织）、TITLE（职位）、PHOTO（照片）、URL 等属性。vCard 4.0（RFC 6350）是目前的最新版本，增加了对多语言标签、社交网络标识符、时区字段的支持，并修正了前代版本的不一致之处。

CalDAV 通过 REPORT 方法支持服务器端查询——客户端可以发送 calendar-query REPORT 请求，指定时间范围（time-range）、文本匹配（text-match）等过滤条件，服务器仅返回符合条件的 VEVENT，而非传输整个日历文件。这对于包含数千个事件的多年日历尤为重要，大幅减少带宽消耗。CardDAV 同样支持 addressbook-query REPORT，允许客户端按姓名、邮件地址等字段搜索通讯录。

**二、DNS SRV 服务发现 (RFC 6764)**

RFC 6764 为 CalDAV 和 CardDAV 定义了 DNS SRV 记录的服务发现机制，使得客户端可以根据用户的邮件地址自动发现日历和通讯录服务器地址，免去手动配置。标准定义的 SRV 记录命名格式如下：

```
_caldavs._tcp.example.com.  86400 IN SRV 10 0 443 caldav.example.com.
_carddavs._tcp.example.com. 86400 IN SRV 10 0 443 carddav.example.com.
```

SRV 记录的各个字段含义：\_caldavs.\_tcp 为服务名称（\_caldavs 为 HTTPS 加密的 CalDAV，\_caldav 为 HTTP 非加密版本；CardDAV 同理）；优先级（Priority）为 10，值越小优先级越高；权重（Weight）为 0，在相同优先级下按权重比例分配流量；端口为 443；目标主机名为实际提供 CalDAV/CardDAV 服务的服务器。域名部分应使用用户邮件地址中 @ 后面的域名部分（即 example.com）。客户端从用户的邮件地址中提取域名，构造 SRV 查询名称，然后向该名称发起 DNS SRV 查询以获取实际服务地址。

如 CalDAV/CardDAV 服务与[邮件系统部署](/kb/category/ops-architecture.html)在同一域名下（如 mail.example.com），可将 SRV 目标指向同一台服务器。需要在 DNS 提供商的面板中添加对应的 SRV 记录条数（TXT 记录区域不支持 SRV 格式）。对于反向代理部署场景（Nginx/Traefik 前置 HTTPS），SRV 记录中的端口应为反向代理的 HTTPS 端口（通常为 443），后续代理将请求路由到后端 CalDAV/CardDAV 服务。

**三、Radicale 开源 CalDAV/CardDAV 服务器部署**

Radicale 是轻量级的 CalDAV/CardDAV 服务器，Python 实现，支持文件系统后端存储，部署简单，适合中小规模企业部署。安装步骤：

```
apt install radicale
# 或通过 pip
pip3 install radicale
```

Radicale 配置文件 /etc/radicale/config：

```
[server]
hosts = 0.0.0.0:5232

[auth]
type = htpasswd
htpasswd_filename = /etc/radicale/users
htpasswd_encryption = bcrypt

[rights]
type = owner_only

[storage]
type = multifilesystem
filesystem_folder = /var/lib/radicale/collections
```

Radicale 的默认端口为 5232（纯 HTTP），生产和测试中建议使用反向代理添加 HTTPS 支持。Nginx 反向代理配置示例：

```
location /.well-known/caldav {
    return 301 /radicale/;
}
location /.well-known/carddav {
    return 301 /radicale/;
}
location /radicale/ {
    proxy_pass http://127.0.0.1:5232/;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $http_host;
}
```

.well-known 路径的配置实现自动发现——CalDAV/CardDAV 客户端会在连接域名时首先尝试访问 /.well-known/caldav 和 /.well-known/carddav，以获得实际的服务 URL。上述重定向告知客户端通过 /radicale/ 路径访问服务。创建用户和日历：

```
htpasswd -B -c /etc/radicale/users alice

# 通过 curl 创建日历集合
curl -X MKCOL -u alice:password \
  "https://caldav.example.com/radicale/alice/default-calendar/"
```

**四、客户端支持与配置**

Thunderbird 内置了 CalDAV 和 CardDAV 支持，无需额外插件。在 Thunderbird 中添加 CalDAV 日历：打开日历标签页 → 新建日历 → 选择"网络上" → 输入 CalDAV 服务器地址（如 https://caldav.example.com/radicale/alice/default-calendar/）→ 输入用户名和密码完成配置。添加 CardDAV 通讯录：打开通讯录标签页 → 新建通讯录 → 选择"CardDAV" → 输入地址和认证信息。Thunderbird 支持订阅多个日历（个人日历、团队日历、节假日日历），不同日历以颜色区分显示。

Microsoft Outlook 本身不支持 CalDAV/CardDAV 协议（它使用专有的 MAPI/EWS 或 Microsoft 365 协议）。但可通过第三方插件实现：CalDAV Synchronizer（开源，GitHub）是最流行的 Outlook CalDAV/CardDAV 桥接插件，作为 Outlook COM 加载项运行，双向同步 Outlook 日历/联系人到 CalDAV/CardDAV 服务器。安装 CalDAV Synchronizer 后，在 Outlook 的"CalDAV Synchronizer"功能区中配置服务器 URL、用户名、密码和同步间隔（建议 5-15 分钟）。插件会创建 Outlook 本地文件夹与 CalDAV 服务器的映射，自动将 Outlook 中的日历事件同步到服务器。

iOS 和 macOS 原生支持 CalDAV/CardDAV。iOS 上：设置 → 日历 → 账户 → 添加账户 → 其他 → 添加 CalDAV 账户，输入服务器地址、用户名和密码。系统日历 App 和通讯录 App 自动使用该账户进行同步。macOS 上：系统偏好设置 → 互联网账户 → 添加其他账户 → CalDAV 或 CardDAV，输入对应信息。iOS/macOS 的 CalDAV 实现较为完整，支持会议邀请（iMIP）、忙闲查询（FreeBusy）、提醒通知等功能。

**五、认证桥接：与邮件系统统一认证**

在生产环境中，CalDAV/CardDAV 的用户认证应与邮件系统（IMAP/LDAP）统一，避免用户维护多套密码。Radicale 支持多种认证后端，包括：（1）LDAP 认证：通过 radicale\_auth\_ldap 插件，Radicale 可使用 LDAP 绑定验证用户密码，与邮件系统共用 OpenLDAP 或 Active Directory 用户目录。配置示例：

```
[auth]
type = ldap
ldap_url = ldap://ldap.example.com:389
ldap_base = ou=users,dc=example,dc=com
ldap_attribute = uid
ldap_filter = (objectClass=inetOrgPerson)
```

（2）IMAP 认证：通过 IMAP 服务器验证用户密码。Radicale 使用 IMAP LOGIN 命令验证凭据是否有效：连接到 IMAP 服务器 → 发送 LOGIN 命令 → 如果 IMAP 响应 OK，则认证通过；如果 IMAP 响应 NO，则拒绝。这种方式的优点是无需额外维护用户数据库，完全复用邮件服务器的用户体系。配置示例：

```
[auth]
type = remote_user
# 或使用自定义 IMAP 认证钩子
# 通过 X-Forwarded-User 头传递已验证的用户名
```

（3）HTTP 基本认证 + 反向代理集成：使用 Nginx/Apache 在前端处理 LDAP/IMAP 认证（通过 ngx\_http\_auth\_ldap\_module 或 Apache mod\_authnz\_ldap），验证通过后将用户名通过 HTTP 头传递给 Radicale。Radicale 配置 type = http\_x\_remote\_user，从请求头中读取已验证的用户名。

**六、会议邀请与忙闲查询（FreeBusy）**

CalDAV 支持两个关键的企业协作功能：会议邀请（iTIP/iMIP）和忙闲状态查询（FreeBusy）。iTIP（iCalendar Transport-Independent Interoperability Protocol, RFC 5546）定义了会议邀请的交换方式——组织者通过 .ics 附件发送会议邀请邮件，参与者收到邮件后在 CalDAV 客户端中接受或拒绝邀请，响应通过邮件返回给组织者。iMIP（iCalendar Message-Based Interoperability Protocol, RFC 6047）是将 iTIP 绑定到电子邮件传输的具体实现。在 Radicale 中，会议邀请支持需要在客户端（如 Thunderbird）中配置邮件账户，客户端发送包含 VEVENT 的 .ics 附件。忙闲状态查询是 CalDAV 的扩展功能，允许在创建会议时查询参与者的忙闲时间段。通过 VFREEBUSY 组件实现：客户端查询参与者的 CalDAV 服务器，获取在指定时间范围内已安排的事件摘要（仅含时间不含详情）。Radicale 通过支持 calendar-multiget REPORT 来提供忙闲查询数据。

**七、昆仑邮件系统中的 CalDAV/CardDAV 集成**

昆仑邮件系统 内置了完整的 CalDAV/CardDAV 服务模块，与邮件系统的 IMAP/LDAP 认证体系原生集成。管理员在后台"协作服务"界面中启用 CalDAV 和 CardDAV 服务后，系统自动为所有用户创建个人日历和通讯录集合，用户无需额外配置即可在客户端中使用同一组邮件账号凭据访问日历和通讯录。系统支持共享日历（团队日历）——团队管理员可以创建团队共享日历，向团队成员授予只读或读写权限，实现会议室的预订管理和团队排班等功能。

系统还内置了 DNS SRV 自动发现记录的自动生成提示——管理员在后台查看"域名配置检查"时，系统会自动检测 CalDAV/CardDAV DNS 记录是否完整，并对缺失项给出具体配置建议。这种端到端的集成方式免去了管理员自行部署 Radicale 并进行认证桥接的繁琐步骤。

**八、参考文献**

[1] RFC 4791 - Calendaring Extensions to WebDAV (CalDAV). IETF, March 2007. https://datatracker.ietf.org/doc/rfc4791/

[2] RFC 6352 - CardDAV: vCard Extensions to Web Distributed Authoring and Versioning (WebDAV). IETF, August 2011. https://datatracker.ietf.org/doc/rfc6352/

[3] RFC 6764 - Locating Services for CalDAV and CardDAV via DNS SRV. IETF, February 2013. https://datatracker.ietf.org/doc/rfc6764/

[4] RFC 5545 - Internet Calendaring and Scheduling Core Object Specification (iCalendar). IETF, September 2009. https://datatracker.ietf.org/doc/rfc5545/

[5] RFC 6350 - vCard Format Specification. IETF, August 2011. https://datatracker.ietf.org/doc/rfc6350/

[6] GB/T 37002-2023 - 信息安全技术 电子邮件系统安全技术要求. 国家标准化管理委员会, 2023.

[7] Radicale 项目文档. https://radicale.org/

了解更多邮件技术实践，请访问知识库或联系

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/caldav-carddav-email.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
