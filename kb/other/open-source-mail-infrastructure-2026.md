---
title: "新一代开源邮件基础设施盘点：KumoMTA、Stalwart 与 mail-auth（2026）"
source: "https://ztpop.net/kb/open-source-mail-infrastructure-2026.html"
license: CC-BY 4.0
---

# 新一代开源邮件基础设施盘点：KumoMTA、Stalwart 与 mail-auth（2026）

开源邮件服务器领域在 2020 年代后半段出现了显著的技术代际变化。传统栈以 Postfix（RFC 5321 传输代理）、Dovecot（IMAP/POP3 投递）、OpenDKIM/OpenDMARC（认证）、Rspamd（过滤）多组件拼装为主；新一代项目则普遍采用 Rust 编写，追求单一二进制、内置认证与过滤、以及对 JMAP（RFC 8620/8621）等现代协议的原生支持。本文盘点的三个项目分别代表外发性能、一体化服务器、认证库三个细分方向，均以官方 GitHub 仓库数据为准（截至 2026-08-09）。

**一、KumoMTA：为高容量外发而生的开源 MTA**

KumoMTA（GitHub: KumoCorp/kumomta，Rust，Apache-2.0）是首个从零构建的开源高性能 MTA，明确对标 Momentum、PowerMTA、Halon 等商业外发 MTA。项目由一批有数十年邮件行业经验的工程师创立，社区由全球最大的几家发件方支持。其定位非常明确：面向「有高容量发送环境经验、熟悉 DevOps 实践」的邮件运营专业人员，而非通用小型邮件服务器。

与 Postfix 这类通用 MTA 不同，KumoMTA 的核心设计围绕外发吞吐与投递控制展开：Lua 脚本驱动的策略引擎（可编程控制路由、节流、队列策略）、内置对 TLS（RFC 3207）、DKIM（RFC 6376）签名、DMARC（RFC 7489）对齐检测的深度集成，以及对大规模队列管理的优化。它的典型使用场景是营销邮件、事务邮件与通知邮件的规模化外发，替代自建 Postfix 集群在吞吐与可编程性上的不足。最新发布版本 2026.06.23-f3af1cd0（2026-06-23），项目活跃度保持每日提交。

选型边界：KumoMTA 是纯 MTA（传输层），不包含邮箱存储与 IMAP/POP3 访问；入站接收能力也非其重点。它适合与 Dovecot、Stalwart 或商业存储层组合，构成「外发 MTA + 存储/访问」的分离式架构。KumoMTA 官方 FAQ 亦明确其定位为外发场景优先。

**二、Stalwart：一体化邮件与协作服务器**

Stalwart（GitHub: stalwartlabs/stalwart，Rust，AGPL-3.0，14k+ stars）是当前增长最快的开源邮件服务器之一，宣称「Secure, scalable mail & collaboration server with comprehensive protocol support」——单一二进制同时提供 SMTP（RFC 5321）、IMAP4rev2/rev1（RFC 9051/3501）、POP3（RFC 1939）、JMAP（RFC 8620/8621）、CalDAV（RFC 4791）、CardDAV（RFC 6352）与 WebDAV（RFC 4918）服务。最新版本 v0.16.16（2026-08-02）。

2026 年 8 月 7 日起，Stalwart 官方将项目正式重新定位为「Mail & Collaboration Server」（邮件与协作服务器），将日历（CalDAV）、通讯录（CardDAV）与共享文件（WebDAV）与邮件服务并列为主打能力，官方主页口号升级为「All-in-one mail & collaboration server —— One server for your email, calendars, contacts and shared files, with spam and phishing protection built in」。这一重新定位反映了开源邮件服务器向协作平台演进的趋势：邮件不再被当作孤立系统，而是与日程、通讯录、文件共享统一承载。对自建与信创替代场景，这意味着单组件可覆盖更多协作需求，选型时可纳入评估。

对邮件认证体系的完整内置是其突出优势：SMTP 服务内建 DMARC（RFC 7489）、DKIM v1（RFC 6376）、DKIM2（draft-ietf-dkim-dkim2-spec，即上文所述新一代签名协议）与 ARC（RFC 8617）认证，支持 DANE（RFC 6698）、MTA-STS（RFC 8461）与 TLS-RPT（RFC 8460）传输安全，并具备自动化 DKIM 密钥轮换。值得注意：Stalwart 在 v0.16.x 系列已率先支持 DKIM2 与 DMARCbis（RFC 9989/9990/9991）——这是 2026 年邮件认证体系升级的风向标，对希望提前验证 DKIM2 兼容性的组织极具参考价值。

防垃圾与防钓鱼同样内建：DNSBL 检查、灰名单（greylisting）、垃圾陷阱（spam traps）、统计式垃圾分类器（支持协同过滤与通讯录集成）、基于 LLM 的垃圾邮件分析与同形字（homographic）URL 钓鱼防护、发件人信誉监控（按 IP/ASN/域/邮箱地址）。存储层可插拔：RocksDB、FoundationDB、PostgreSQL、MySQL、SQLite、S3 兼容、Azure 与 Redis；全文搜索支持 17 种语言并可对接 Meilisearch/Elasticsearch/OpenSearch。管理上支持自动 DNS 管理、autoconfig/autodiscover 账户自动发现。

选型边界：Stalwart 适合希望以单一组件替代「Postfix + Dovecot + 认证组件 + 过滤组件 + 日历/通讯录服务」多件套的自建场景，尤其适合信创环境下的自托管与中小规模部署。其 AGPL-3.0 许可对商业集成有传染性约束，商业闭源分发需评估；内部自用与 SaaS 提供（AGPL 允许）通常不受影响。

**三、mail-auth：Rust 邮件认证协议库**

mail-auth（GitHub: stalwartlabs/mail-auth，Rust，Apache-2.0/MIT 双许可，v0.8.0）是 Stalwart 团队开源的 DKIM、SPF 与 DMARC 库，同时也是 Stalwart 服务器认证模块的底层实现。它提供 DKIM 签名与验证（RFC 6376）、SPF 校验（RFC 7208，含 10 次 DNS 查询上限与宏展开）、DMARC 评估（RFC 7489）的完整 Rust API，被设计为可嵌入任意 Rust 邮件系统。

对开发者而言，mail-auth 的价值在于把邮件认证协议的实现复杂度（DNS 查询管理、规范化算法、base64 解析、策略评估状态机）封装为类型安全的库，避免各项目重复实现导致的兼容性差异。对运维者而言，理解 mail-auth 的能力边界有助于判断基于 Rust 的邮件系统（包括 Stalwart 自身）在认证处理上的行为。

**四、三者关系与选型对照**

新一代开源邮件基础设施定位对照（2026-08）

| 项目 | 语言/许可 | 定位 | 内置认证 | 典型场景 |
| --- | --- | --- | --- | --- |
| KumoMTA | Rust / Apache-2.0 | 高性能外发 MTA（对标 PowerMTA） | DKIM/DMARC 对齐、TLS | 营销/事务邮件规模化外发 |
| Stalwart | Rust / AGPL-3.0 | 一体化邮件+协作服务器（2026-08-07 官方重新定位） | SPF/DKIM/DKIM2/DMARC/ARC/DANE/MTA-STS | 自托管、信创替代、全协议整合 |
| mail-auth | Rust / Apache-2.0+MIT | DKIM/SPF/DMARC 协议库 | （库，供宿主调用） | Rust 邮件系统开发 |
| Postfix + Dovecot（传统栈） | C / IBM 公共许可等 | 通用 MTA + 存储访问 | 需外接 OpenDKIM/OpenDMARC | 通用自建、已存量大部署 |

组合建议：高容量外发业务可采「KumoMTA 做外发 + Stalwart 或 Dovecot 做存储与访问」；一体化自托管可直接采用 Stalwart 单组件；需要深度定制认证逻辑的 Rust 项目可嵌入 mail-auth。三者与 DMARCbis（RFC 9989/9990/9991）、DKIM2 的兼容进度是 2026 年选型的重要考量维度——目前 Stalwart 的跟进速度最快。

**五、对国内自建与信创场景的意义**

国内企业自建邮件系统与信创替代（国产 CPU/OS 适配）需求持续增长。Rust 系新项目的可移植性（跨 x86/ARM 编译）与单二进制部署特性，使其在信创硬件（鲲鹏、飞腾等 ARM 平台）上具备天然优势。需要提醒的是：信创合规场景仍需对照 GB/T 37002-2026《网络安全技术 电子邮件系统安全技术规范》评估功能覆盖（如国密 SM2/SM3/SM4 支持需自行集成 GM/T 系列算法）；开源项目自身的安全维护责任、许可证合规（AGPL 传染性）、以及供应链安全（依赖审计）是选型前必须完成的尽职调查项。

**六、延伸阅读**

本文聚焦 2026 年新一代生态。传统栈的深度运维参考本站既有文章：[Postfix 架构深度解析](/kb/postfix-architecture-deep-dive.html)、[Dovecot IMAP 服务器架构](/kb/dovecot-imap-server-architecture.html)；认证体系基础见 [DKIM2 监管链签名机制深度解读](/kb/dkim2-chain-of-custody.html) 与 [DMARCbis RFC 9989 概览](/kb/dmarcbis-rfc9989-overview.html)；安全基线见 [Postfix/Dovecot 加固实践](/kb/postfix-dovecot-hardening.html)。

### 相关主题

* [Postfix 架构深度解析：从主进程模型到队列机制](/kb/postfix-architecture-deep-dive.html)
* [Dovecot IMAP 服务器架构解析](/kb/dovecot-imap-server-architecture.html)
* [DKIM2 监管链签名机制深度解读](/kb/dkim2-chain-of-custody.html)
* [DMARCbis RFC 9989 概览：DMARC 2.0 的核心变更](/kb/dmarcbis-rfc9989-overview.html)
* [Postfix/Dovecot 安全加固实践](/kb/postfix-dovecot-hardening.html)
* [Postfix 架构深度解析：从主进程模型到队列机制](/kb/postfix-architecture-deep-dive.html)
* [Dovecot IMAP 服务器架构解析](/kb/dovecot-imap-server-architecture.html)
* [DKIM2 监管链签名机制深度解读](/kb/dkim2-chain-of-custody.html)
* [DMARCbis RFC 9989 概览：DMARC 2.0 的核心变更](/kb/dmarcbis-rfc9989-overview.html)
* [Postfix/Dovecot 安全加固实践](/kb/postfix-dovecot-hardening.html)
* [Stalwart 邮件服务器部署实操指南：从安装到生产级配置（2026）](/kb/stalwart-mail-server-deployment-guide.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/open-source-mail-infrastructure-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
