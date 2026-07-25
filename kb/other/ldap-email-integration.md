---
title: "LDAP 与邮件系统集成 — RFC 4510-4519：Postfix LDAP 表查询、Dovecot 认证与多域架构 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/ldap-email-integration.html"
license: CC-BY 4.0
---

# LDAP 与邮件系统集成 — RFC 4510-4519：Postfix LDAP 表查询、Dovecot 认证与多域架构 · ztpop 邮件技术知识库

LDAP 与邮件系统集成 — RFC 4510-4519：Postfix LDAP 表查询、Dovecot 认证与多域架构

## 摘要

LDAP（Lightweight Directory Access Protocol, LDAP v3 由 RFC 4510-4519 系列定义, June 2006）是邮件系统中用于集中存储用户身份、认证凭据、邮件路由和权限策略的目录服务基础协议。与基于 SQL 数据库的用户管理系统相比，LDAP 的树状信息模型（DIT, Directory Information Tree）天然适配组织的层级结构（ou=People → ou=Departments → dc=example,dc=com），其读取优化设计（读取速率通常是写入速率的 10 倍以上）使它在邮件系统这种读多写少的场景中性能优异。本文覆盖 LDAP v3 协议基础（schema、DIT、LDIF 格式）、Postfix 的 LDAP 虚拟别名表（virtual\_alias\_maps）和虚拟域表（virtual\_mailbox\_domains）的查询配置、Dovecot 的 LDAP passdb（密码认证）和 userdb（用户信息检索）的集成方案、多域多租户架构中的 LDAP DIT 设计模式，并以 OpenLDAP 2.6 为例给出基础部署步骤，包括 TLS 加密、访问控制列表（ACL）和双主复制配置。

## 1. LDAP v3 协议基础与 DIT 信息模型

### 1.1 LDAP 目录信息树（DIT）

LDAP 的数据以树状层级结构组织，树根通常由域组件（dc）构成。一个典型的企业邮件系统的 LDAP DIT：

```
dc=example,dc=com
├── ou=People,dc=example,dc=com          # 用户条目
│   ├── uid=john,ou=People,dc=example,dc=com
│   └── uid=jane,ou=People,dc=example,dc=com
├── ou=Groups,dc=example,dc=com          # 邮件组/分发列表
│   └── cn=engineering,ou=Groups,dc=example,dc=com
├── ou=Domains,dc=example,dc=com         # 虚拟域
│   └── dc=example,dc=com?sub?(objectClass=mailDomain)
└── ou=Aliases,dc=example,dc=com         # 邮件别名
    └── uid=postmaster,ou=Aliases,dc=example,dc=com
```

每个条目由一个或多个
`objectClass`
定义其 schema（可包含哪些属性）。RFC 4512（LDAP: Directory Information Models, June 2006）定义了 schema 的基本结构：
`objectClass`
定义条目的类型（如
`inetOrgPerson`
表示人员），
`MUST`
属性为必填字段（如
`cn`
通用名、
`sn`
姓氏），
`MAY`
属性为可选字段（如
`mail`
邮箱地址、
`userPassword`
密码）。RFC 4519（LDAP: Schema for User Applications, June 2006）进一步标准化了 30 个用户相关的属性类型，包括
`uid`
（用户标识符）、
`givenName`
和
`telephoneNumber`
。

### 1.2 LDIF 格式：用户条目的交换格式

```
# LDIF 格式示例：john@example.com 的用户条目
dn: uid=john,ou=People,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: top
objectClass: mailRecipient
uid: john
cn: John Smith
sn: Smith
givenName: John
mail: john@example.com
mailAlternateAddress: john.smith@example.com
userPassword: {SSHA}QjL9k...base64hash...
mailQuota: 524288000
mailHomeDirectory: /var/vmail/example.com/john/
mailHost: mailstore1.example.com
```

`userPassword`
属性支持多种密码存储格式前缀：
`{CRYPT}`
（Unix crypt）、
`{SSHA}`
（Salted SHA-1，OpenLDAP 默认）、
`{SHA256}`
（Salted SHA-256）、
`{ARGON2}`
（OpenLDAP 2.5+ 通过 argon2.so 模块）。昆仑邮件系统的 LDAP 集成强制要求
`{SSHA256}`
或
`{ARGON2}`
作为密码存储格式，禁止使用
`{CRYPT}`
（其 DES 基础算法已被彩虹表攻击在 3.2 小时内突破 7 字符密码空间）。

## 2. Postfix LDAP 表查询配置

### 2.1 LDAP 虚拟域查询（virtual\_mailbox\_domains）

Postfix 通过查找表（lookup table）机制集成 LDAP。每个查找表对应一个
`/etc/postfix/ldap-*.cf`
配置文件，Postfix 的
`proxymap(8)`
服务负责缓存查询结果（默认缓存 3600 秒）。虚拟域表配置（
`/etc/postfix/ldap-virtual-domains.cf`
）：

```
server_host = ldapi://%2Fvar%2Frun%2Fldapi
search_base = ou=Domains,dc=example,dc=com
query_filter = (&(objectClass=mailDomain)(dc=%s))
result_attribute = dc
version = 3
bind = yes
bind_dn = cn=postfix,ou=Services,dc=example,dc=com
bind_pw =
```

查询逻辑：当 Postfix 接收到发往
`@example.com`
的邮件时，
`%s`
被替换为
`example.com`
（域名部分），LDAP 查询在
`ou=Domains`
下搜索
`(&(objectClass=mailDomain)(dc=example.com))`
的条目。如果返回结果，说明该域是本地的，邮件交由虚拟投递代理处理。

### 2.2 LDAP 虚拟别名查询（virtual\_alias\_maps）

虚拟别名表（
`/etc/postfix/ldap-virtual-aliases.cf`
）：

```
server_host = ldapi://%2Fvar%2Frun%2Fldapi
search_base = ou=People,dc=example,dc=com
query_filter = (&(|(mail=%s)(mailAlternateAddress=%s))(objectClass=inetOrgPerson))
result_attribute = mail
version = 3
bind = yes
bind_dn = cn=postfix,ou=Services,dc=example,dc=com
bind_pw =
```

这个查找表支持两种匹配：(1) 直接主邮箱匹配（
`mail=%s`
）——当用户
`john@example.com`
存在时返回自己的地址；(2) 别名匹配（
`mailAlternateAddress=%s`
）——当
`john.smith@example.com`
被查询时返回
`mail`
属性的主地址。Postfix 的
`main.cf`
配置引用这些表：

```
virtual_mailbox_domains = ldap:/etc/postfix/ldap-virtual-domains.cf
virtual_alias_maps = ldap:/etc/postfix/ldap-virtual-aliases.cf
```

### 2.3 高可用：多 LDAP 服务器与故障转移

`server_host`
支持多服务器列表（空格分隔），Postfix 按顺序尝试：

```
server_host = ldap://ldap1.example.com ldap://ldap2.example.com ldap://ldap3.example.com
```

Postfix 3.5+ 支持
`timeout`
和
`retry_delay`
参数（以秒为单位）：

```
timeout = 5
retry_delay = 60
```

当第一个 LDAP 服务器在 5 秒内无响应，Postfix 标记其为故障并尝试下一个服务器。故障服务器在 60 秒后被重新探测。

## 3. Dovecot LDAP 认证集成

### 3.1 passdb：用户密码验证

Dovecot 的 passdb 配置（
`/etc/dovecot/dovecot-ldap.conf.ext`
）定义了如何通过 LDAP 验证用户密码：

```
hosts = /var/run/ldapi
dn = cn=dovecot,ou=Services,dc=example,dc=com
dnpass = 
auth_bind = no
base = ou=People,dc=example,dc=com
pass_filter = (&(objectClass=inetOrgPerson)(|(uid=%n)(mail=%u)))
pass_attrs = uid=user,userPassword=password,\
  mailHomeDirectory=userdb_home,\
  mailQuota=userdb_quota_rule=*:bytes=%$
```

`pass_filter`
支持两种登录方式：(1)
`uid=%n`
——用户以用户名登录（如
`john`
）时，
`%n`
展开为用户名部分；(2)
`mail=%u`
——用户以完整邮箱地址登录（如
`john@example.com`
）时，
`%u`
展开为完整用户名。Dovecot 执行
`pass_filter`
搜索找到用户条目后，提取
`userPassword`
属性值并与用户提供的密码比对（格式为
`{SSHA}...`
时 Dovecot 使用对应的哈希算法验证）。

`pass_attrs`
将 LDAP 属性映射到 Dovecot 内部字段：
`uid=user`
映射用户名，
`userPassword=password`
映射密码，
`mailHomeDirectory=userdb_home`
映射用户的邮件存储目录路径，
`mailQuota=userdb_quota_rule=*:bytes=%$`
将 LDAP 中的
`mailQuota`
（字节数）映射为 Dovecot 的配额规则格式。

### 3.2 userdb：用户信息检索

userdb 用于在用户已通过认证后检索用户信息（如邮箱路径、配额、UID/GID）：

```
# /etc/dovecot/dovecot-ldap.conf.ext（userdb 部分）
user_attrs = \
  mailHomeDirectory=home,\
  mailQuota=quota_rule=*:bytes=%$,\
  mailHost=host
user_filter = (&(objectClass=inetOrgPerson)(|(uid=%n)(mail=%u)))
```

Dovecot 主配置中启用 LDAP：

```
# /etc/dovecot/conf.d/10-auth.conf
!include auth-ldap.conf.ext

# /etc/dovecot/conf.d/auth-ldap.conf.ext
passdb {
  driver = ldap
  args = /etc/dovecot/dovecot-ldap.conf.ext
}
userdb {
  driver = ldap
  args = /etc/dovecot/dovecot-ldap.conf.ext
}
```

### 3.3 auth\_bind 模式（用户自绑定）

`auth_bind = yes`
是另一种认证模式：Dovecot 使用用户提供的 DN 和密码直接尝试绑定（bind）LDAP 服务器，由 LDAP 服务器的绑定操作完成密码验证，而不从 LDAP 拉取
`userPassword`
哈希到本地比较：

```
auth_bind = yes
auth_bind_userdn = uid=%n,ou=People,dc=example,dc=com
```

这种模式的优点是密码哈希永不离开 LDAP 服务器，安全性高于
`auth_bind = no`
（后者会将哈希传输到 Dovecot 进行本地验证）。缺点是无法使用 Dovecot 的密码缓存和 SASL 代理机制。对于部署了 LDAP 集群、密码存储格式为
`{ARGON2}`
或
`{SSHA512}`
的环境，
`auth_bind = yes`
是更安全的选项。

## 4. 多域架构中的 LDAP DIT 设计

### 4.1 扁平分域模型（每域独立子树）

对于托管多个独立域名的邮件系统（如 example.com、company.cn、school.edu），最常见的 DIT 设计是在根下为每个域创建独立的组织单元子树：

```
dc=example,dc=com
├── ou=example.com
│   ├── uid=john,ou=example.com,dc=example,dc=com
│   └── uid=jane,ou=example.com,dc=example,dc=com
├── ou=company.cn
│   └── uid=wang,ou=company.cn,dc=example,dc=com
└── ou=school.edu
    └── uid=smith,ou=school.edu,dc=example,dc=com
```

Postfix 虚拟域查询需要在
`search_base`
中覆盖所有域子树：

```
search_base = dc=example,dc=com
query_filter = (&(objectClass=mailDomain)(|(dc=%s)(associatedDomain=%s)))
```

这种设计的查询复杂度为 O(log n)（LDAP B-Tree 索引），在 10 万个用户条目规模下，
`objectClass=inetOrgPerson`
和
`uid`
的联合索引使查询响应时间保持在 5ms 以内（OpenLDAP 2.6 + lmdb 后端，Intel Xeon 处理器）。

### 4.2 分层组织模型（组织 - 部门 - 用户）

对于大型企业，多域只是维度之一，组织单元层级（部门、团队）需要独立建模。典型方案是在域子树下嵌套 OU 层级：

```
dc=company,dc=cn
├── ou=People
│   ├── ou=Engineering
│   │   ├── uid=zhang,ou=Engineering,ou=People,dc=company,dc=cn
│   │   └── uid=li,ou=Engineering,ou=People,dc=company,dc=cn
│   └── ou=Sales
│       └── uid=wang,ou=Sales,ou=People,dc=company,dc=cn
├── ou=Groups
│   └── cn=all-staff,ou=Groups,dc=company,dc=cn
└── ou=Domains
    └── dc=company,dc=cn?sub?(objectClass=mailDomain)
```

在 Dovecot 的
`pass_filter`
中，由于用户可能位于任意深度的 OU 子树中，
`search_base`
需要设到
`ou=People,dc=company,dc=cn`
并使用子树搜索（LDAP scope
`sub`
，Dovecot 默认行为）。当用户数超过 10 万时，建议在
`pass_filter`
中避免使用非索引属性（如
`givenName`
）作为过滤条件——只使用
`uid`
、
`mail`
等已建立 equality 索引的属性。

## 5. OpenLDAP 基础部署

### 5.1 安装与初始配置

```
# Debian/Ubuntu
# apt install slapd ldap-utils
# dpkg-reconfigure slapd   # 设置管理员密码、域组件等

# CentOS/RHEL 8+
# dnf install openldap-servers openldap-clients
# systemctl enable --now slapd
```

导入邮件 schema（在
`slapd.conf`
或
`cn=config`
中）：

```
# 加载 cosine.schema, inetorgperson.schema（基础用户 schema）
# ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/cosine.ldif
# ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/ldap/schema/inetorgperson.ldif
```

创建基础 DIT（LDIF 文件
`base.ldif`
）：

```
dn: dc=example,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
o: Example Corporation
dc: example

dn: ou=People,dc=example,dc=com
objectClass: organizationalUnit
ou: People

dn: ou=Groups,dc=example,dc=com
objectClass: organizationalUnit
ou: Groups
```

```
# ldapadd -x -D "cn=admin,dc=example,dc=com" -W -f base.ldif
```

### 5.2 TLS 加密

OpenLDAP 的 TLS 配置（通过
`cn=config`
动态配置）：

```
# ldapmodify -Y EXTERNAL -H ldapi:///
dn: cn=config
changetype: modify
add: olcTLSCertificateFile
olcTLSCertificateFile: /etc/letsencrypt/live/ldap.example.com/fullchain.pem
-
add: olcTLSCertificateKeyFile
olcTLSCertificateKeyFile: /etc/letsencrypt/live/ldap.example.com/privkey.pem
-
add: olcTLSProtocolMin
olcTLSProtocolMin: 3.3
```

`olcTLSProtocolMin: 3.3`
限制最低 TLS 1.2（OpenLDAP 2.5+ 使用 3.3 表示 TLS 1.2）。生产环境建议启用 LDAPS（
`ldaps://`
端口 636）和 StartTLS（
`ldap://`
端口 389 + 扩展操作）。Postfix 和 Dovecot 的连接 URI 应使用
`ldaps://`
或
`ldapi://`
（Unix socket，不经过 TCP 网络）。

### 5.3 访问控制（ACL）

基础 ACL 规则（限制
`userPassword`
属性的可见性）：

```
# cn=config 的 olcAccess 属性
# 规则 1: 管理员和用户自己可以读取/修改自己的条目
{0}to * by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage
     by * break
# 规则 2: 用户自己可以修改 userPassword，认证用户可以读取通用属性
{1}to attrs=userPassword
     by self write
     by anonymous auth
     by * none
# 规则 3: 认证用户可以读取所有非敏感属性
{2}to *
     by users read
     by * none
```

ACL 规则按优先级数字（
`{0}, {1}, {2}`
）顺序评估，首个匹配的规则生效。规则 {1} 限制
`userPassword`
属性——只有用户自己可以写入（修改密码），匿名用户仅用于绑定认证（不能读取），其他人无权访问。

## 6. LDAP 复制与高可用

### 6.1 双主复制（Multi-Master Replication）

OpenLDAP 的 syncrepl 协议（RFC 4533, Content Synchronization Operation）支持多主复制。配置示例（LDIF 格式，应用至
`cn=config`
的
`olcDatabase={1}mdb`
子树）：

```
# 在 ldap1.example.com 上配置复制到 ldap2
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcSyncRepl
olcSyncRepl: rid=001
  provider=ldaps://ldap2.example.com
  binddn="cn=replicator,dc=example,dc=com"
  bindmethod=simple
  credentials=
  searchbase="dc=example,dc=com"
  type=refreshAndPersist
  interval=00:00:00:30
  retry="60 10 300 +"
```

`type=refreshAndPersist`
使用持久连接模式，变更实时推送（而非定期轮询）。
`retry="60 10 300 +"`
的含义：连接断开后，每 60 秒重试，重试间隔以 10 的倍数递增，最多重试 300 次后放弃。昆仑邮件系统的生产 LDAP 集群使用 3 节点双主复制架构，任意一个节点故障时，Postfix 和 Dovecot 通过 LDAP URI 列表自动切换到存活的节点，邮件服务的 LDAP 查询零中断。

### 6.2 性能监控与调优

LDAP 查询性能直接影响邮件系统的 SMTP 接收延迟和 IMAP 登录响应时间。关键监控指标：

```
# 通过 cn=Monitor 获取 OpenLDAP 统计（需加载 back_monitor 模块）
# ldapsearch -x -D "cn=admin,dc=example,dc=com" -W \
    -b "cn=Monitor" -s base "(objectClass=*)" monitorCounter
#
# 关注指标:
#   monitorCounter.ops.completed.operations  — 已完成操作总数
#   monitorCounter.entries                   — 当前条目数
#   monitorCounter.connections.current       — 当前连接数
#   monitorCounter.bytes.sent                — 发送字节数/秒
```

索引优化：为高频查询的属性建立 equality 和 presence 索引：

```
# cn=config 的 olcDbIndex 属性
olcDbIndex: objectClass eq
olcDbIndex: uid eq,pres
olcDbIndex: mail eq,pres
olcDbIndex: mailAlternateAddress eq,pres
olcDbIndex: member eq
olcDbIndex: dc eq
```

`eq`
（equality）用于精确匹配查询（
`uid=john`
），
`pres`
（presence）用于存在性检查（
`uid=*`
）。
`sub`
（substring）索引仅在实际需要前缀或后缀匹配时才添加（如
`uid=joh*`
），因为子串索引会显著增加数据库大小和写入开销。

### 参考文献

1. RFC 4510 — Lightweight Directory Access Protocol (LDAP): Technical Specification Road Map (IETF, June 2006). Defines the LDAP v3 specification suite.
2. RFC 4511 — LDAP: The Protocol (IETF, June 2006). Core protocol operations: Bind, Search, Modify, Add, Delete, ModifyDN, Unbind.
3. RFC 4512 — LDAP: Directory Information Models (IETF, June 2006). Schema definitions: objectClass, attribute types, matching rules, DIT structure.
4. RFC 4519 — LDAP: Schema for User Applications (IETF, June 2006). Standardized attribute types for user entries.
5. RFC 4533 — LDAP: Content Synchronization Operation (IETF, June 2006). syncrepl replication protocol specification.
6. OpenLDAP 2.6 Administrator's Guide —
   <https://www.openldap.org/doc/admin26/>
   . Sections on SASL, TLS, access control, replication.
7. Postfix LDAP Readme —
   <https://www.postfix.org/LDAP_README.html>
   . LDAP table configuration and query syntax.
8. Dovecot LDAP Authentication —
   <https://doc.dovecot.org/configuration_manual/authentication/ldap/>
   . passdb and userdb configuration reference.
9. GB/T 37002-2018 — 信息安全技术 电子邮件系统安全技术要求. 第 6.2.1 节 用户管理（LDAP 目录服务作为集中身份管理基础组件）.
10. NIST SP 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management (NIST, June 2017). Section 5.1.1.2 Memorized Secret Verifiers — password storage requirements.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ldap-email-integration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
