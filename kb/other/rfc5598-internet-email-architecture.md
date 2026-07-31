---
title: "RFC 5598 互联网邮件架构：从发件方到收件方的端到端组件视图"
source: "https://ztpop.net/kb/rfc5598-internet-email-architecture.html"
license: CC-BY 4.0
---

# RFC 5598 互联网邮件架构：从发件方到收件方的端到端组件视图

## 概述

RFC 5598 把分散在 SMTP、MIME、IMAP、POP 等文档中的概念整合为一幅"互联网邮件架构"全景图。它定义了一套通用术语与功能组件，使不同实现（Postfix、Exchange、信创邮件系统）能在同一坐标系下被比较。对正在做 Exchange 迁移或信创邮件替换的团队，这是架构设计的权威基线。

## 核心组件

* **MUA（邮件用户代理）**：用户直接交互的客户端（Outlook、网页邮箱、移动 App）。
* **MSA（邮件提交代理）**：位于发件方一侧，接收 MUA 提交、执行认证与策略后交给 MTA，对应 RFC 6409 的 587 端口提交。
* **MTA（邮件传输代理）**：基于 SMTP（RFC 5321）在服务器间路由转发，是互联网的"邮政网络"。
* **MDA（邮件投递代理）**：把邮件存入收件方信箱，可能触发过滤、归档、病毒扫描。
* **Message Store（信箱存储）**：收件方读取邮件的仓库，通过 IMAP/POP 暴露。

## 信息流与边界

一封邮件的旅程：`MUA → MSA →（一系列）MTA → MDA → Message Store →（IMAP/POP）→ 收件方 MUA`。RFC 5598 特别强调了"管理域（ADMD）"边界——每个组织是一个 ADMD，跨 ADMD 的信任靠认证（SPF/DKIM/DMARC）与传输加密（STARTTLS/MTA-STS）建立。

## 与协议栈的映射

| 功能 | 对应协议/RFC |
| --- | --- |
| 提交 | RFC 6409（Submission，587） |
| 传输 | RFC 5321（SMTP）、RFC 8461（MTA-STS） |
| 信头/正文格式 | RFC 5322、RFC 2045/2046（MIME） |
| 读取 | RFC 3501（IMAP）、RFC 1939（POP3） |
| 认证 | RFC 7208 / 6376 / 7489 |

## 对信创邮件替换的启示

迁移时按 RFC 5598 的组件逐层对账：MSA 的 587 提交与认证、MTA 的 MX 路由与队列、MDA 的投递与过滤、Message Store 的 IMAP 兼容。任何一层不兼容都会表现为"能发不能收"或"客户端连不上"。以架构视图驱动迁移，比逐个排错高效得多。

### 相关主题

* [企业邮件迁移完全指南](/kb/email-migration-guide.html)：从评估到割接的步骤
* [SMTP 协议深度解析](/kb/smtp-protocol-deep-dive.html)：MTA 路由与队列机制
* [邮件提交协议（MSA）](/kb/smtp-submission-protocol.html)：587 端口与认证
* [信创邮件系统架构设计](/kb/xinchuang-email-architecture-design.html)：国产替代的组件映射
* [Exchange 到昆仑邮件迁移](/kb/exchange-to-turboex-migration.html)：组件级对照

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc5598-internet-email-architecture.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
