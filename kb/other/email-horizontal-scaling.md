---
title: "邮件系统水平扩展架构：DNS MX、共享存储与IMAP Proxy"
source: "https://ztpop.net/kb/email-horizontal-scaling.html"
license: CC-BY 4.0
---

# 邮件系统水平扩展架构：DNS MX、共享存储与IMAP Proxy

#### 📑 目录

1. [水平扩展架构总览](#s1)
2. [DNS round-robin MX 负载均衡](#s2)
3. [共享存储方案](#s3)
4. [独立存储+复制方案](#s4)
5. [Authentication 后端负载均衡](#s5)
6. [IMAP Proxy：Haproxy / nginx 转发](#s6)
7. [综合参考架构](#s7)

## 一、水平扩展架构总览

邮件系统的水平扩展（Horizontal Scaling）通过增加服务器节点来提升容量和可用性，而非升级单机硬件（垂直扩展）。RFC 5321 Section 5 定义了多 MX 主机的优先级投递机制，这是邮件系统最原始也是最有效的水平扩展入口。

水平扩展的三个关键维度：  
**1) MTA 层** — 多台 Postfix 实例接收入站/出站邮件  
**2) 存储层** — 邮件存储（Maildir/mdbox）的分布与复制  
**3) 接入层** — IMAP/POP3 客户端的路由与代理

## 二、DNS round-robin MX 负载均衡

### 2.1 MX 优先级与权重

```
# DNS MX 配置示例（双节点 load sharing）
example.com.  IN  MX  10  mx1.example.com.
example.com.  IN  MX  10  mx2.example.com.
example.com.  IN  MX  20  mx3.example.com.
# 优先级 10 的两台 MX 承担相同权重（发件 MTA 随机选择）
# 优先级 20 的 mx3 作为备用（仅前两台不可达时被选）

mx1.example.com.  IN  A  203.0.113.10
mx2.example.com.  IN  A  203.0.113.11
mx3.example.com.  IN  A  203.0.113.12
```

### 2.2 MX 负载均衡的局限性

DNS round-robin 不是真正的负载均衡——它没有对后端健康状态、连接数或当前负载做感知。发件 MTA 的行为不可控：一些 MTA 会始终选择 MX 列表中的第一个 A 记录解析结果（忽略优先级相同的轮询），另一些 MTA 会在失败时立即切换到下一个而不等待重试超时。

RFC 5321 Section 5.1 规定了 MX 选择的随机性和权重偏好，但实际实现差异巨大。RFC 2821 历史版本中的 "MUST try all MX records" 在 RFC 5321 中被弱化为 "SHOULD"。

```
# 检查实际 MX 选择分布（在多个发件 MTA 上执行）
# 通过 pflogsumm 统计目标域对应中继
pflogsumm -d today /var/log/mail.log | grep "relay=mx[12]"
# 可以统计 mx1 与 mx2 接收的连接比例

# 更好的方法：使用 SMTP 连接日志
grep 'connect from' /var/log/mail.log | grep -oP '\[(\d+\.){3}\d+\]' \
  | sort | uniq -c | sort -rn | head -10
```

### 2.3 MX 健康检查与自动摘除

```
#!/bin/bash
# MX 存活检查脚本 — 配合 DNS update (RFC 2136) 自动摘除不可用 MX
for mx in mx1 mx2 mx3; do
  if ! nc -zv "$mx.example.com" 25 -w5 2>/dev/null; then
    logger -t mx-health "ALERT: $mx.example.com SMTP port 25 unreachable"
    # 可选: nsupdate 删除此 MX 记录、或切换优先级
  fi
done
```

## 三、共享存储方案

### 3.1 共享存储架构

所有 MTA 节点通过共享文件系统（NFS、GlusterFS、CephFS）访问同一份邮件存储。优势是多节点间无状态——邮件存放在共享存储上，任何节点都可以投递或读取。Dovecot 的 mdbox 格式对共享存储支持较好。

```
# Dovecot NFS 配置 — /etc/dovecot/conf.d/10-mail.conf
mail_location = mdbox:~/Maildir
mail_fsync = always             # NFS 下必须启用 fsync

# Dovecot NFS 专用安全设定 — /etc/dovecot/local.conf
mmap_disable = yes
dotlock_use_excl = yes
mail_nfs_storage = yes
mail_nfs_index = yes
lock_method = dotlock           # NFS 不支持 fcntl/flock

# NFS 挂载选项 — /etc/fstab
nfs.example.com:/mailstore /var/vmail nfs rw,bg,hard,intr,rsize=1048576,wsize=1048576,vers=4.2,timeo=600,retrans=2 0 0
```

### 3.2 共享存储优缺点

表 1：共享存储 vs 独立存储对比

| 维度 | 共享存储（NFS/Ceph） | 独立存储+复制 |
| --- | --- | --- |
| 一致性 | 强一致性（依赖 NFS 语义） | 最终一致性（复制延迟） |
| 延迟 | 网络存储延迟（1–10ms） | 本地磁盘（0.1–1ms） |
| 闲置资源 | 全节点共享，容量利用率高 | 每节点独立，容量一定浪费 |
| 运维复杂度 | 依赖共享存储 HA（NFS Ganesha, Ceph） | 依赖复制同步工具（lsync, drbd） |
| 拆节点风险 | 共享存储故障 = 全站停服 | 单节点故障仅影响该节点用户 |
| 扩容方式 | 扩展共享存储集群 | 增加节点+迁移用户 |
| 推荐场景 | 低用户数（<50,000） | 高用户数（>50,000） |

## 四、独立存储+复制方案

### 4.1 基于用户绑定路由

采用用户→节点映射（用户绑定 + 目录哈希 + 一致性哈希），每个用户的邮箱只属于一个存储节点。IMAP 接入层通过 `doveadm director` 或 Haproxy 按用户哈希路由到正确节点。

```
# Dovecot Director 配置 — /etc/dovecot/dovecot-director.conf
service director {
  unix_listener director-userdb {
    mode = 0660
  }
  fifo_listener director-notify {
    mode = 0600
  }
  service_count = 0
  vsz_limit = 256M
}
director_servers = 203.0.113.10 203.0.113.11 203.0.113.12
director_username_hash = %u     # 按邮箱全地址哈希

# 后端 Dovecot — /etc/dovecot/conf.d/10-director.conf
mail_location = mdbox:~/Maildir
service doveadm {
  inet_listener {
    port = 12345
  }
}
```

### 4.2 存储复制策略

```
# 方案 A: DRBD + 主备复制（块设备级）
# /etc/drbd.d/mailstore.res
resource mailstore {
  on mx1 {
    device    /dev/drbd0;
    disk      /dev/sdb1;
    address   203.0.113.10:7789;
    meta-disk internal;
  }
  on mx2 {
    device    /dev/drbd0;
    disk      /dev/sdb1;
    address   203.0.113.11:7789;
    meta-disk internal;
  }
}

# 方案 B: lsyncd + rsync（文件级准实时同步）
# /etc/lsyncd/lsyncd.conf.lua
settings {
  logfile = "/var/log/lsyncd/lsyncd.log",
  statusFile = "/var/log/lsyncd/lsyncd-status.log",
  delay = 5,              # 5 秒聚合延迟
  maxProcesses = 8
}
sync {
  default.rsyncssh,
  source = "/var/vmail",
  host = "mx2.example.com",
  targetdir = "/var/vmail",
  rsync = {
    archive = true,
    compress = true,
    delete = true,
    _extra = {"--bwlimit=50000"}   # 限制带宽 50MB/s
  }
}

# 方案 C: Dovecot dsync（邮件级双向同步）
# 全量同步（首次）
doveadm backup -u user@example.com -R ssh://mx2/var/vmail

# 增量同步（crontab 每 5 分钟）
doveadm sync -u user@example.com -R ssh://mx2/var/vmail
```

## 五、Authentication 后端负载均衡

### 5.1 Postfix + Dovecot 认证路径

水平扩展场景下，所有 MTA 节点共用同一认证后端。Postfix 通过 Dovecot SASL（`dovecot/.../auth`）做 SMTP 认证，Dovecot 再连接到后端的 LDAP/Auth SQL 数据库。

```
# Dovecot LDAP 配置 — /etc/dovecot/conf.d/auth-ldap.conf.ext
passdb {
  driver = ldap
  args = /etc/dovecot/dovecot-ldap.conf.ext
}
userdb {
  driver = ldap
  args = /etc/dovecot/dovecot-ldap.conf.ext
}

# /etc/dovecot/dovecot-ldap.conf.ext
hosts = ldap1.example.com:389 ldap2.example.com:389
ldap_version = 3
auth_bind = yes
base = dc=example,dc=com
deref = never
scope = subtree
user_attrs = =home=/var/vmail/%u, uid=vmail, gid=vmail
pass_attrs = uid=user, userPassword=password
# Dovecot 自动在多个 LDAP 服务器间做 failover（顺序尝试）
```

### 5.2 LDAP/SQL 连接的负载均衡

```
# 方案 A: Haproxy TCP 代理 LDAP
# /etc/haproxy/haproxy.cfg (LDAP frontend)
frontend ldap-in
  bind *:389
  default_backend ldap-servers
  mode tcp
  option tcpka

backend ldap-servers
  mode tcp
  balance roundrobin
  server ldap1 10.0.1.10:389 check inter 5s fall 3 rise 2
  server ldap2 10.0.1.11:389 check inter 5s fall 3 rise 2
  server ldap3 10.0.1.12:389 check inter 5s fall 3 rise 2

# 方案 B: Pgpool-II / ProxySQL — PostgreSQL / MySQL 认证数据库
# proxySQL 配置示例
mysql_users:
  - username: "vmail"
    password: "secret"
    default_hostgroup: 0

mysql_servers:
  - hostgroup: 0
    hostname: "10.0.1.20"
    port: 3306
  - hostgroup: 0
    hostname: "10.0.1.21"
    port: 3306

mysql_query_rules:
  - rule_id: 1
    active: 1
    match_pattern: "^SELECT"
    destination_hostgroup: 1    # 读从库
  - rule_id: 2
    active: 1
    match_pattern: ".*"
    destination_hostgroup: 0    # 写主库
```

## 六、IMAP Proxy：Haproxy / nginx 转发

### 6.1 为什么需要 IMAP Proxy

当存储层使用独立存储+复制方案时，用户的邮箱固定在特定节点上。IMAP 客户端第一次连接时可能被路由到错误的节点，此时 IMAP Proxy 需要将连接**转发**到正确的后端节点（Proxy Protocol / 基于用户的 routing）。

### 6.2 Haproxy IMAP Proxy 配置

```
# /etc/haproxy/haproxy.cfg — IMAP proxy with sticky sessions
frontend imaps-in
  bind *:993 ssl crt /etc/ssl/haproxy/haproxy.pem no-sslv3
  mode tcp
  option tcplog
  default_backend imap-backends
  # 启用 PROXY Protocol v2 传递原始客户端 IP
  # 后端 Dovecot 需要 haproxy_trusted_networks 接收

backend imap-backends
  mode tcp
  balance roundrobin
  # 基于用户哈希做粘性路由
  # 需要 Haproxy 2.4+ 支持 IMAP 协议解析
  server dovecot1 10.0.2.10:143 check inter 10s fall 3 rise 2 send-proxy-v2
  server dovecot2 10.0.2.11:143 check inter 10s fall 3 rise 2 send-proxy-v2
  server dovecot3 10.0.2.12:143 check inter 10s fall 3 rise 2 send-proxy-v2
```

### 6.3 nginx Stream IMAP Proxy

```
# /etc/nginx/nginx.conf — stream IMAP proxy
stream {
  upstream imap_backend {
    least_conn;
    server 10.0.2.10:143 max_fails=3 fail_timeout=30s;
    server 10.0.2.11:143 max_fails=3 fail_timeout=30s;
    server 10.0.2.12:143 max_fails=3 fail_timeout=30s;
  }

  # IMAP (TLS)
  server {
    listen 993 ssl;
    proxy_pass imap_backend;
    proxy_protocol on;               # 转发客户端真实 IP
    ssl_certificate     /etc/ssl/certs/imap-proxy.pem;
    ssl_certificate_key /etc/ssl/private/imap-proxy.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_session_cache   shared:IMAP:10m;
    ssl_session_timeout 10m;
  }

  # IMAP (plain text, 仅限内网)
  server {
    listen 143;
    proxy_pass imap_backend;
    proxy_protocol on;
  }
}
```

### 6.4 Dovecot Proxy Protocol 配置

当 IMAP Proxy 使用 PROXY Protocol 传递客户端 IP 时，Dovecot 必须信任代理服务器：

```
# /etc/dovecot/conf.d/10-master.conf
service imap-login {
  inet_listener imap {
    port = 143
  }
  inet_listener imaps {
    port = 993
    ssl = yes
  }
  # IMAP proxy 必须信任的前置代理地址段
  haproxy_trusted_networks = 10.0.0.0/8, 172.16.0.0/12
}

# 如使用 PROXY Protocol v2，需启用
# /etc/dovecot/conf.d/20-login.conf
haproxy_trusted_networks = 10.0.0.0/8, 172.16.0.0/12
# Dovecot 自动检测 PROXY Protocol header
```

### 6.5 会话粘性高级方案

纯 TCP 代理无法感知用户身份。如需精确的路由（用户 → 正确的存储节点），需要 Dovecot Director 集群或应用层路由：

```
# Dovecot Director 负责用户映射
# 客户端 → Haproxy (port 143) → Dovecot Director (port 2000) → 后端 Dovecot (port 11000)
#
# Director 控制流:
# 1. 客户端连接 Director
# 2. Director 根据 username_hash 决定目标后端
# 3. 连接转发到目标后端的 11000 端口
# 4. 后端使用 PROXY Protocol 接收

# 后端 Dovecot 监听 11000（非标准端口，避免直接暴露）
service imap-login {
  inet_listener imap-ext {
    port = 11000
  }
}
```

## 七、综合参考架构

### 7.1 中等规模（50,000–200,000 用户）参考拓扑

```
                        ┌─────────────────────────┐
                        │    DNS MX (RR + Pri)     │
                        │  mx1/mx2/mx3.example.com │
                        └────────┬────────┬────────┘
                                 │        │
              ┌──────────────────┘        └──────────────────┐
              ▼                                               ▼
     ┌──────────────────┐                       ┌──────────────────┐
     │  Haproxy (SMTP)  │                       │  Haproxy (SMTP)  │
     │  port 25/smtp    │                       │  port 25/smtp    │
     └────────┬─────────┘                       └────────┬─────────┘
              │                                          │
     ┌────────▼─────────┐                       ┌────────▼─────────┐
     │  Postfix mx1     │                       │  Postfix mx2     │
     │  + Rspamd milter │                       │  + Rspamd milter │
     └────────┬─────────┘                       └────────┬─────────┘
              │                                          │
              └──────────┬───────────┬───────────────────┘
                         │           │
                ┌────────▼───┐ ┌─────▼────────┐
                │ LDAP/SQL   │ │ Auth Backend │
                │ (HAproxy)  │ │ (Pgsql HA)   │
                └────────────┘ └──────────────┘
                         │
              ┌──────────▼─────────────────────────┐
              │   Haproxy / nginx IMAP Proxy        │
              │   port 993 (TLS) + 143 (plain)      │
              │   + PROXY Protocol                  │
              └────┬──────────────┬─────────────────┘
                   │              │
          ┌────────▼───┐  ┌──────▼────────┐
          │ Dovecot 1  │  │  Dovecot 2    │  ... (N 节点)
          │ Storage    │  │  Storage      │
          │ + dsync    │  │  + dsync      │
          └────────────┘  └───────────────┘

                        ┌──────────────────┐
                        │  Ceph / DRBD     │
                        │  (复制 + 备份)   │
                        └──────────────────┘
```

### 7.2 容量规划参考

表 2：水平扩展容量参考

| 节点数 | 用户数 | 存储方案 | 每日邮件量 | IMAP Proxy 规格 |
| --- | --- | --- | --- | --- |
| 2 | < 10,000 | NFS 共享 | < 50 万 | Haproxy (2 vCPU, 4 GB) |
| 3–4 | 10,000–50,000 | DRBD 主备 | 50–200 万 | Haproxy (4 vCPU, 8 GB) |
| 5+ | 50,000–200,000 | 独立 + dsync | 200–1000 万 | nginx stream (8 vCPU, 16 GB) |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-horizontal-scaling.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
