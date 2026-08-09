---
title: "Stalwart 邮件服务器部署实操指南：从安装到生产级配置（2026）"
source: "https://ztpop.net/kb/stalwart-mail-server-deployment-guide.html"
license: CC-BY 4.0
---

# Stalwart 邮件服务器部署实操指南：从安装到生产级配置（2026）

本文是《[新一代开源邮件基础设施盘点：KumoMTA、Stalwart 与 mail-auth（2026）](/kb/open-source-mail-infrastructure-2026.html)》的配套实操篇，面向有意将 Stalwart 投入生产部署的运维工程师。Stalwart 最新稳定版为 **v0.16.16**（2026-08-02 发布），是当前首个同时支持 DKIM2（draft-ietf-dkim-dkim2-spec）与 DMARCbis（RFC 9989/9990/9991）的开源邮件服务器实现[[1]](#ref-1)。

## 一、系统要求与前置条件

Stalwart 由 Rust 编写，原生支持 Linux、macOS、FreeBSD 与 Windows。根据官方文档[[2]](#ref-2)：

Stalwart 资源需求（官方数据）

| 场景 | 内存 | 说明 |
| --- | --- | --- |
| 空闲状态 | ≈ 100 MB | 轻量级，适合资源受限环境 |
| 5–10 用户典型部署 | 1 GB RAM | 推荐起步配置 |
| 高流量企业环境 | 4+ GB RAM | 数千并发连接场景 |
| 默认并发连接上限 | 8192（全部协议共享） | 可配置降低以节省内存 |

CPU 需求与并发量正相关；x86\_64 与 ARM64（鲲鹏/飞腾等信创平台）均支持，Rust 的跨架构编译能力使其在信创硬件上具备天然优势。

部署前需准备：域名（MX 记录指向本服务器）、TLS 证书（或使用 ACME 自动申请）、25/465/587/143/993/110/995/4190/8080/443 等端口可用。

## 二、安装方式对比

Stalwart 安装方式对比

| 方式 | 适用场景 | 配置管理 | 维护复杂度 |
| --- | --- | --- | --- |
| 官方安装脚本（Linux/macOS/FreeBSD） | 生产服务器直接部署 | YAML/JSON 配置文件 | 低 |
| Docker / Docker Compose | 快速验证/开发环境 | 容器卷持久化配置/数据 | 中 |
| Windows 原生 | Windows Server 开发测试 | 同上 | 低 |
| Kubernetes / Helm | 大规模集群 | 声明式，K8s 管理 | 高 |

生产部署推荐官方安装脚本；开发测试推荐 Docker。

## 三、二进制脚本安装（Linux / macOS / FreeBSD）

官方提供一键安装脚本，下载并执行[[1]](#ref-1)：

```
# 下载并执行安装脚本（默认安装到 /opt/stalwart）
$ curl --proto '=https' --tlsv1.2 -sSf https://get.stalw.art/install.sh -o install.sh
$ sudo sh install.sh

# 指定安装目录
$ sudo sh install.sh /opt/stalwart
```

安装脚本完成以下操作：创建 stalwart 系统用户（非 root）、将二进制文件复制到安装目录、注册 systemd 服务（或 launchd/mail.local）。

安装完成后，启动服务并查看 Bootstrap 引导凭证：

```
# systemd 系统
$ sudo systemctl start stalwart
$ sudo journalctl -u stalwart -n 200 | grep -A8 'bootstrap mode'

# 日志文件备选
$ sudo grep -A8 'bootstrap mode' /var/log/syslog \
    || sudo grep -A8 'bootstrap mode' /var/log/messages

# macOS launchd
$ sudo launchctl kickstart -k system/stalwart.mail
$ sudo log show --predicate 'process == "stalwart"' --last 5m
```

Bootstrap 模式会输出临时管理员账户：

```
username: admin
password: XXXXXXXXXXXXXXXX

Use these credentials to complete the initial setup at the /admin web UI.
http://<hostname>:8080/admin
```

**重要**：Bootstrap 凭证仅在首次引导时有效，配置完成后自动失效。立即访问 Web UI 完成初始设置。

### 3.1 安装 FoundationDB 存储后端版本

如需使用 FoundationDB 作为存储后端（高可用集群场景），安装时加 `--fdb` 参数[[1]](#ref-1)：

```
$ sudo sh install.sh --fdb
```

## 四、Docker 部署

Docker 适合快速验证或隔离部署。官方镜像为 `stalwartlabs/stalwart:v0.16`[[1]](#ref-1)：

```
# 拉取镜像
$ docker pull stalwartlabs/stalwart:v0.16

# 创建持久化卷
$ docker volume create stalwart-etc
$ docker volume create stalwart-data

# 启动容器（暴露全部协议端口）
$ docker run -d --name stalwart \
    --restart unless-stopped \
    -p 443:443 -p 8080:8080 \
    -p 25:25 -p 587:587 -p 465:465 \
    -p 143:143 -p 993:993 \
    -p 110:110 -p 995:995 \
    -p 4190:4190 \
    -v stalwart-etc:/etc/stalwart \
    -v stalwart-data:/var/lib/stalwart \
    stalwartlabs/stalwart:v0.16

# 查看引导凭证
$ docker logs stalwart 2>&1 | grep -A8 'bootstrap mode'

# 重启容器（配置更新后）
$ docker restart stalwart
# 或 docker compose restart stalwart
```

生产环境建议使用 Docker Compose 或 Kubernetes，配置卷持久化与网络策略。

## 五、Web UI 初始配置（Bootstrap 引导）

访问 `http://<服务器IP>:8080/admin`，使用 Bootstrap 凭证登录后，Web UI 提供向导式配置：

1. **管理员账户**：创建永久管理员（替换临时 admin）
2. **域名配置**：添加邮件域名，设置 MX 记录要求
3. **存储后端**：选择 RocksDB（默认）/ PostgreSQL / MySQL / SQLite / FoundationDB / S3 等
4. **证书配置**：ACME 自动申请（推荐）或手动上传 PEM
5. **服务端口**：确认 SMTP/IMAP/JMAP 等协议监听端口

配置完成后，临时 Bootstrap 账户失效，永久管理员接管。重启服务使所有配置生效：

```
$ sudo systemctl restart stalwart   # systemd
$ docker restart stalwart           # Docker
```

## 六、DNS 配置要点

Stalwart 内置 ACME 自动申请 Let's Encrypt 证书，但 DNS 记录需手动配置[[3]](#ref-3)：

Stalwart 生产部署必需 DNS 记录

| 记录类型 | 主机名 | 值 | 用途 |
| --- | --- | --- | --- |
| MX | @ | 10 mail.example.com. | 邮件接收 |
| A / AAAA | mail | 服务器 IP | MX 指向 |
| TXT（SPF） | @ | v=spf1 mx -all | 发件授权（RFC 7208） |
| TXT（DMARC） | \_dmarc | v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com | 收件方认证（RFC 7489） |
| TXT（DKIM） | selector.\_domainkey | Stalwart Web UI 生成 | DKIM 签名（RFC 6376） |
| TXT（MTA-STS） | \_mta-sts | v=STSv1; id=1 | 强制 TLS 策略（RFC 8461） |
| TXT（TLS-RPT） | \_smtp.\_tls | v=TLSRPTv1; rua=mailto:tlsrpt@example.com | TLS 报告（RFC 8460） |

Stalwart 支持 `stalwart-cli` 命令行工具查看自动生成的 DNS 记录[[1]](#ref-1)：

```
$ stalwart-cli query domain
$ stalwart-cli get domain <id> --fields dnsZoneFile
```

## 七、内置邮件认证体系配置

Stalwart v0.16.x 是 2026 年对邮件认证新标准支持最完整的开源实现[[4]](#ref-4)。所有认证功能在 Web UI 中一键启用，无需外接 OpenDKIM/OpenDMARC。

### 7.1 DKIM2 签名（draft-ietf-dkim-dkim2-spec）

Stalwart 是首个在生产代码中实现 DKIM2 监管链签名机制的邮件服务器。DKIM2 新增特性[[5]](#ref-5)：

* **Message-Instance + DKIM2-Signature 双头部**：解决转发链中签名被剥离的顽疾
* **chain of custody（监管链）**：ARC 链整合，转发场景下签名不被破坏
* **Recipe 代数签名**：内容变更可被追踪（编辑日历邀请/邮件转发场景）
* **f= 标志（forwarded）**：明确标识「合理转发」场景，区别于伪造

Stalwart Web UI → Domains → 选择域名 → DKIM Keys，可生成 RSA 2048 或 Ed25519（RFC 8463）密钥对，并自动将公钥发布为 DNS TXT 记录。

### 7.2 DMARCbis 支持（RFC 9989/9990/9991）

Stalwart v0.16.x 已支持 DMARCbis 全部三个 RFC[[4]](#ref-4)：

* **RFC 9989**：DMARCbis 核心规范（取代 RFC 7489），新增 `np=`（不存在子域策略）、`psd=`（公共后缀域标志）、`t=`（测试模式，降低一级执行策略）标签，移除 pct/rf/ri，引入 DNS Tree Walk 策略发现
* **RFC 9990**：DMARCbis 聚合报告格式，XML namespace 更新为 dmarc-2.0，policy_published 回显 np 等标签配置
* **RFC 9991**：DMARCbis 失败报告（基于 ARF 格式，Updates RFC 6591），强化隐私保护——失败报告不得包含邮件正文，仅可含部分头部字段

配置入口：Web UI → Domains → DMARC Policy。建议从 `p=none` 开始（仅监控），至少运行 2–4 周后再逐步升级到 `p=quarantine` 最终到 `p=reject`，步骤详见《[部署 DMARCbis 的最小配置步骤与迁移路线](/kb/faq/dmarcbis-faq-10.html)》。

### 7.3 ARC 认证（RFC 8617）

Stalwart 自动处理 ARC 链：转发邮件时自动插入 ARC-Set 与 ARC-Message-Signature 头部；接收时验证 ARC 验签并保留 `cv=pass` 链，使 DMARC 校验失败邮件（如转发导致的 From 对齐问题）仍可被放行[[6]](#ref-6)。使用 [ARC 校验器](/tools/arc-validator.html)可诊断转发链完整性。

### 7.4 SPF / DANE / MTA-STS

Stalwart SMTP 入站验证内建 SPF（RFC 7208）校验，支持 DANE（RFC 6698）TLSA 记录与 MTA-STS（RFC 8461）强制 TLS 策略。使用 [SPF 深度诊断工具](/tools/spf-deep-diagnose.html)验证配置合规性。

## 八、存储后端选型

Stalwart 存储分为三层：数据存储（账户/域/配置）、Blob 存储（邮件正文/附件）、搜索索引[[2]](#ref-2)。各层均支持多种后端：

Stalwart 存储后端对照（官方文档）

| 后端 | 适用规模 | 类型 | 备注 |
| --- | --- | --- | --- |
| RocksDB（默认） | 小型–中型 | 嵌入式 KV | 安装即用，无需额外服务 |
| SQLite | 小型 | 嵌入式关系型 | 最轻量 |
| PostgreSQL | 中型–大型 | RDBMS | 推荐生产使用 |
| MySQL / MariaDB | 中型–大型 | RDBMS | 企业存量环境 |
| FoundationDB | 大型/高可用 | 分布式 KV | 需单独安装，`--fdb` 版 |
| S3 兼容（MinIO/阿里云 OSS） | 任意规模 | 对象存储 | Blob 存储层，兼容 AWS S3 API |
| Redis | 缓存/队列 | 内存 KV | 队列/缓存，不作主存储 |

全文搜索支持 17 种语言，可对接内置引擎、Meilisearch、Elasticsearch/OpenSearch 或 PostgreSQL/MySQL 全文索引。

## 九、从 Postfix + Dovecot 迁移步骤对照

Stalwart 可替代「Postfix（SMTP）+ Dovecot（IMAP/POP3）+ OpenDKIM（签名）+ OpenDMARC（验证）+ Rspamd（过滤）」多组件栈，提供单一二进制统一管理。以下迁移步骤[[7]](#ref-7)供参考：

1. **评估阶段**：在测试环境安装 Stalwart，确认协议兼容性（IMAP4rev2/rev1、JMAP、Sieve 均已支持）；使用 [域名健康评分工具](/tools/domain-health-score.html)评估当前域名认证状态
2. **DNS 预配置**：在 DNS 添加 Stalwart 的 MX 记录，但主 MX 仍指向旧服务器；配置 SPF/DKIM/DMARC/MTA-STS 记录指向新服务器 IP（并行运行期）
3. **用户迁移**：导出 Dovecot 邮件存储（Maildir/mbox）到 Stalwart 支持的格式；导入账户数据（Stalwart 支持 SQL 目录 / LDAP / 内置数据库）
4. **切换 MX**：修改 DNS 将 MX 主记录切换到 Stalwart；旧服务器保留作为备份 MX（优先级 20）
5. **验证阶段**：使用 [SPF 诊断](/tools/spf-deep-diagnose.html)、[DMARC 报告解析器](/tools/dmarc-xml-parser.html)、[parsedmarc 自托管教程](/kb/parsedmarc-self-hosted-guide.html)验证认证体系运行正常
6. **下线旧组件**：确认投递无误后，下线 Postfix/Dovecot/OpenDKIM/OpenDMARC/Rspamd

Stalwart 官方提供从 Dovecot、 Cyrus、Exchange 的迁移指南[[7]](#ref-7)，建议在正式迁移前完整阅读。

## 十、信创环境注意事项

Stalwart 在信创环境（鲲鹏/飞腾/海光等 ARM64 平台、麒麟/统信 OS）部署时需关注以下事项：

* **Rust 跨平台编译**：Stalwart 提供 Linux x86\_64 与 ARM64 预编译二进制，信创平台建议从源码编译（`cargo build --release --target aarch64-unknown-linux-gnu`）以获得最佳性能
* **AGPL-3.0 许可**：内部自用与 SaaS 提供不受传染；商业闭源产品集成需评估许可证约束[[4]](#ref-4)
* **国密算法**：Stalwart 当前版本（v0.16.x）不含 SM2/SM3/SM4 国密支持；信创合规场景需自行评估 GB/T 37002-2026[[8]](#ref-8)的要求缺口
* **依赖审计**：Rust crate 依赖链需纳入供应链安全评估

## 十一、常见问题

### Q1：Bootstrap 模式密码丢失怎么办？

进入恢复模式（Recovery Mode）重新生成管理员凭证，详见官方恢复模式文档[[1]](#ref-1)。

### Q2：端口 25 被占用导致 SMTP 无法监听？

Linux 系统通常要求 root 权限才能绑定 25 端口；Stalwart 安装脚本会自动处理权限。如仍失败，检查 `journalctl -u stalwart` 中的端口绑定错误信息。

### Q3：Docker 部署如何持久化 TLS 证书？

将宿主机的证书卷挂载到容器内 `/etc/stalwart/certs/`；或使用 Stalwart ACME 自动申请（Let's Encrypt），证书保存在 `/etc/stalwart/certs/acme/` 中。

### Q4：Stalwart v0.16.x 与旧版 v0.15.x 有何重大差异？

v0.16.x 引入声明式配置（YAML/JSON）替代旧版 TOML，数据库 Schema 有变更；从 v0.15.x 升级需阅读官方升级文档[[1]](#ref-1)。

## 十二、相关工具

Stalwart 生产部署中，推荐配合以下工具验证配置状态：

* [SPF 深度诊断工具](/tools/spf-deep-diagnose.html)：验证 SPF 记录语法、lookup 次数、ptr 误用
* [DMARC XML 报告解析器](/tools/dmarc-xml-parser.html)：解析 Stalwart 发出的 RUA 聚合报告
* [ARC 校验器](/tools/arc-validator.html)：验证 Stalwart 转发生成的 ARC 链
* [域名健康评分](/tools/domain-health-score.html)：8 项聚合检查（SPF/DKIM/DMARC/MTA-STS/BIMI/DNSBL 等）
* [parsedmarc 自托管教程](/kb/parsedmarc-self-hosted-guide.html)：DMARC/TLS-RPT 报告解析开源方案

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/stalwart-mail-server-deployment-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
