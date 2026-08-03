---
title: "Apache James 3.9.0 新特性解读：Java 21 迁移与 Postgres 高性能实现（2026）"
source: "https://ztpop.net/kb/apache-james-390-release-notes.html"
license: CC-BY 4.0
---

# Apache James 3.9.0 新特性解读：Java 21 迁移与 Postgres 高性能实现（2026）

Apache James 以模块化 Mailet 容器架构著称，允许通过组件拼装定制邮件处理流水线。3.9.0 版本（GitHub: apache/james-project，1037 stars / 489 forks）的发布标志着项目进入现代 JVM 时代。以下解读基于官方 CHANGELOG 文件（james-project-3.9.0 tag，2025 年发布）[[1]](#ref-1)。

## 一、重大变更（Breaking Changes）

### 1.1 Java 11 → Java 21 运行时迁移

James 3.9.0 将运行时要求从 Java 11 提升到 **Java 21（LTS）**。Java 21 引入的虚拟线程（Virtual Threads，JEP 444）与结构化并发（JEP 453）为高并发邮件处理提供了新的性能路径，同时获得 Java 21 LTS 的长期安全支持。升级部署前必须确认运行环境 JRE 版本。

### 1.2 javax → jakarta 命名空间迁移

与 Java EE 8 → Jakarta EE 9+ 的行业迁移同步，James 3.9.0 将所有 `javax.*` API 替换为 `jakarta.*`。自定义 Mailet 与集成代码中的 import 语句必须同步更新，否则编译失败。

### 1.3 API 变更

* **CassandraModule 重命名**：所有 `Cassandra*Module` 更名为 `Cassandra*DataDefinition`
* **Mailet API 清理**：不再暴露 mailet config，仅暴露 mailet 名称
* **GenericMailet 构造注入**：config 可通过构造函数绑定（推荐方式）；`init` 仍被调用但将在后续版本移除

### 1.4 移除项

* WhiteList manager（由 Guice DropList 扩展取代）
* JMAP draft 实现（请使用 RFC 8621 正式版）
* habeas warrant mark mailet、Linshare 第三方连接器

## 二、核心亮点：JAMES-2586 高性能 Postgres 实现

**JAMES-2586** 是 3.9.0 最重要的架构级新特性：一套基于 PostgreSQL 的高性能 James 实现，既可用于独立（standalone）场景，也可通过 RabbitMQ、OpenSearch 与 S3 组件横向扩展。这为希望摆脱 Cassandra 运维复杂度的团队提供了新的存储选型。

与既有 Cassandra 实现相比，Postgres 实现降低了基础设施门槛：PostgreSQL 是多数企业已具备的运维能力，无需引入新的分布式数据库。该实现覆盖邮箱存储、用户管理、搜索等核心数据面，配合 OpenSearch 提供全文检索、S3 兼容对象存储提供 Blob 层。

## 三、协议现代化

### 3.1 IMAP PARTIAL 扩展（RFC 9394）

**JAMES-3954** 实现 [RFC 9394](https://datatracker.ietf.org/doc/html/rfc9394) PARTIAL 扩展，为 IMAP FETCH/SEARCH 提供分页语义。RFC 9394 定义了基于位置的范围检索（`PARTIAL` 命令），客户端可在不加载整个邮箱的情况下分页获取邮件元数据，显著降低大邮箱场景的内存与带宽消耗。

### 3.2 SMTP Require TLS 选项（JAMES-3823）

新增 SMTP 强制 TLS 选项（`Require TLS`），与 RFC 3207（STARTTLS）配合，可要求入站/出站会话必须使用 TLS 加密，未协商 TLS 的连接将被拒绝——这是应对明文传输威胁的基础控制项。

### 3.3 SMTP FutureRelease 与 Message Transfer Priorities

* **JAMES-3822**：SMTP FutureRelease 扩展（延迟投递）
* **JAMES-3824**：SMTP Message Transfer Priorities 扩展（消息传输优先级）

### 3.4 JMAP 增强

* **JAMES-4077 / JAMES-4100**：JMAP SearchSnippets（搜索结果片段高亮）实现
* **JAMES-3944**：JMAP FILTER 更多特性（forward/flag/discard 等）
* **JAMES-3962**：JMAP Email/set 对 body part 的特定头部支持
* **JAMES-4143**：JMAP StartWith 过滤器 + 自定义规则头字段

### 3.5 IMAP 共享邮箱与 SSL 热重载

* **JAMES-2182**：IMAP 共享邮箱（shared mailboxes）支持
* **JAMES-3906**：IMAP/SMTP SSL 证书热重载（无需重启服务）
* **JAMES-3954**：IMAP PARTIAL（RFC 9394）
* **JAMES-4069**：IMAP 健康检查端点

## 四、安全加固

James 3.9.0 安全修复清单（官方 CHANGELOG 摘录）

| 项目 | 说明 |
| --- | --- |
| JMX 密码自动检测 | 修复 JMX 密码检测逻辑，防止弱配置 |
| JMX 认证（Spring + Guice） | 为 Spring 与 Guice 两种装配方式设置 JMX 认证过滤器 |
| SMTP DATA 强制 CRLF | 强制 SMTP DATA 事务使用 CRLF 行结束符（RFC 5321 合规） |
| BouncyCastle 1.70 → 1.77 | 修复多个次要 CVE |
| JAMES-4032 DKIM SMTP hook | SMTP 层的 DKIM 签名/验证钩子（RFC 6376） |
| JAMES-4034 SMTP 提交 FROM 校验 | SMTP submission 阶段验证 FROM 头 |
| JAMES-4041 IMAP COPY OOM 修复 | 修复 IMAP COPY 操作内存耗尽 |
| JAMES-4104 webadmin 框架迁移 | 从停止维护的 SparkJava 迁移到活跃 fork |

## 五、可观测性与运维

* **JAMES-3942**：审计追踪（Audit trail）
* **JAMES-3897**：Crowdsec 集成（SMTP/IMAP 恶意 IP 实时封禁）
* **JAMES-3959**：分布式 James 可无 OpenSearch 启动
* **JAMES-4090**：webadmin 关闭指定用户 IMAP 会话
* **JAMES-4091**：列出在线用户端点
* **JAMES-4085**：S3 对象存储 SSE-C 加密（服务端加密-客户密钥）

## 六、升级注意事项

1. **JRE 升级**：确保运行环境为 Java 21 LTS；旧版本 Java 11 无法运行 3.9.0
2. **依赖替换**：自定义 Mailet 中 `javax.*` → `jakarta.*` 全量替换
3. **配置迁移**：CassandraModule 更名影响 Guice 装配代码；检查 `Cassandra*DataDefinition` 新名称
4. **存储评估**：新部署可评估 Postgres 实现（JAMES-2586）替代 Cassandra
5. **JMAP 客户端**：确认客户端兼容 RFC 8621 正式版（draft 已移除）
6. **回归测试**：重点验证 Mailet 流水线、SMTP 认证、IMAP 同步行为

## 七、与 2026 年开源邮件生态的定位

James 3.9.0 与 Rust 系新项目（[Stalwart 部署实操指南](/kb/stalwart-mail-server-deployment-guide.html)）形成差异化：James 面向 JVM 生态与 Mailet 可编程流水线，适合需要深度定制邮件处理逻辑的 Java 团队；Stalwart 以单二进制与内置认证见长。两者与 KumoMTA（高性能外发）共同构成 2026 年开源邮件基础设施的三大路线，详细对照见《[新一代开源邮件基础设施盘点](/kb/open-source-mail-infrastructure-2026.html)》。

在协议层面，James 的 JMAP 支持（RFC 8620/8621）与 IMAP4rev2（RFC 9051）对齐现代客户端趋势，相关协议背景可参考本站《[JMAP 邮件访问协议深度解析](/kb/jmap-protocol-rfc8620.html)》与《[IMAP vs POP3 vs JMAP 选型决策](/kb/imap-pop3-jmap-election.html)》。

## 八、常见问题

### Q1：James 3.9.0 是否支持 SMTPUTF8（EAI）？

James 的 SMTP 栈支持国际化邮件扩展（RFC 6531 体系），但需在配置中显式启用 SMTPUTF8 能力声明；具体以官方文档为准。

### Q2：3.9.0 与 3.7.x 长期支持版的选择？

3.7.6 是 3.7 系列的维护终点（2024-01），3.9.0 是当前主版本。生产环境建议评估 3.9.0 的 Java 21 迁移成本后升级，3.7 系列已不再获得新特性。

### Q3：Postgres 实现能否与 Cassandra 混用？

两种存储实现是独立的装配方案（Guice 模块），不可在同一实例混用；迁移需通过 IMAP 同步或导出导入完成。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/apache-james-390-release-notes.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
