---
title: "Mailpit 与 MailHog：本地开发邮件测试工具对比与实战指南"
source: "https://ztpop.net/kb/mailpit-mailhog-dev-mail-testing.html"
license: CC-BY 4.0
---

# Mailpit 与 MailHog：本地开发邮件测试工具对比与实战指南

# Mailpit 与 MailHog：本地开发邮件测试工具对比与实战指南

更新时间：2026-08-01 · 分类：开发工具 · 阅读约 10 分钟

## 一、为什么需要本地邮件测试工具

在开发注册验证、密码找回、通知推送等邮件功能时，直接使用生产 SMTP 服务器存在三个问题：一是会真实向用户发送测试邮件，造成骚扰；二是无法检查邮件内容渲染是否正确（HTML 布局、图片、链接）；三是难以验证邮件头、DKIM 签名等投递细节。本地邮件测试工具通过启动一个捕获型 SMTP 服务器，**接收并保存所有邮件，但不真正投递**，开发者可以在 Web 界面中查看邮件内容、解析邮件头、测试附件，从而在不污染生产环境的前提下完成邮件功能开发与调试。

## 二、MailHog 概览

MailHog 是 Go 语言编写的开源 SMTP 测试工具，由 Ian Kent 开发（GitHub: mailhog/MailHog，MIT 协议）。它提供一个捕获型 SMTP 服务器（默认端口 1025）与一个 Web 界面（默认端口 8025），同时提供 JSON HTTP API 供程序化访问。

### MailHog 核心特性

* **SMTP 捕获**：监听 1025 端口接收邮件，支持 STARTTLS 与认证（可选）
* **Web 界面**：http://localhost:8025 查看邮件列表与内容
* **JSON API**：/api/v1/messages、/api/v1/messages/{id} 等端点，支持程序化断言
* **内存存储**：默认内存存储，可配置 MongoDB 持久化

MailHog 的 API 端点包括：`GET /api/v1/messages`（分页列出邮件）、`GET /api/v1/messages/{id}`（获取单封邮件详情）、`DELETE /api/v1/messages`（清空收件箱）、`GET /api/v1/search`（搜索邮件）。

## 三、Mailpit 概览

Mailpit 是 MailHog 的现代化继任者，由 axllent（Axllent 团队）开发（GitHub: axllent/mailpit，MIT 协议），用 Go 语言实现，专为开发与测试场景设计。Mailpit 在 MailHog 的基础上重构了 Web 界面与 API，并增加了多项增强功能。

### Mailpit 核心特性

* **SMTP 捕获**：默认监听 1025 端口，支持 STARTTLS、SMTP 认证与多地址监听
* **Web UI**：现代响应式界面，支持邮件全文搜索、标签过滤、附件预览与下载
* **REST API**：`/api/v1/messages`、`/api/v1/message/{id}`、`/api/v1/search` 等端点
* **消息详情**：API 返回完整 MIME 解析结果，含邮件头、正文（HTML/纯文本）、附件元数据
* **存储**：默认 SQLite 数据库持久化，消息不因重启丢失
* **标签与标记**：可为邮件打标签、标记为已读/未读、删除单封或全部

Mailpit 的 API 设计上，`GET /api/v1/message/{id}` 返回的消息对象包含 `ID`、`From`、`To`、`Subject`、`Date`、`Attachments`、`Headers`、`Text`、`HTML` 等字段，其中 `HTML` 为渲染后的内容。此外 Mailpit 还提供 `/api/v1/message/{id}/attachment/{attachmentID}` 用于下载附件。

## 四、核心对比

| 维度 | MailHog | Mailpit |
| --- | --- | --- |
| 语言 | Go | Go |
| 协议 | MIT | MIT |
| 默认端口（SMTP/Web） | 1025 / 8025 | 1025 / 8025 |
| 存储 | 内存（可选 MongoDB） | SQLite 持久化 |
| Web UI | 基础 | 现代响应式，支持搜索/标签/附件预览 |
| REST API | /api/v1/messages 等 | /api/v1/messages、/api/v1/message/{id} 等 |
| 附件下载 | 需解析 MIME | 内置 /attachment/ 端点 |
| 搜索 | 基础 | 全文搜索 + 高级过滤 |
| 维护状态 | 维护较少（新功能停滞） | 活跃开发（2026 年持续更新） |

**结论**：新项目推荐 Mailpit（活跃维护、SQLite 持久化、现代 UI）；老项目或已有 MailHog 依赖可继续使用，二者 API 结构相似，迁移成本低。

## 五、Docker 快速部署

### 部署 Mailpit

```
docker run -d --name mailpit -p 1025:1025 -p 8025:8025 axllent/mailpit
```

启动后：SMTP 服务器位于 `localhost:1025`，Web 界面位于 `http://localhost:8025`。

### 部署 MailHog

```
docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

## 六、接入应用

### 1. 环境变量配置（通用）

```
# SMTP 配置指向本地捕获服务器
MAIL_HOST=localhost
MAIL_PORT=1025
MAIL_USERNAME=          # Mailpit/MailHog 默认无认证
MAIL_PASSWORD=
MAIL_ENCRYPTION=null    # 不使用 TLS
```

### 2. Spring Boot 示例（application.yml）

```
spring:
  mail:
    host: localhost
    port: 1025
    username:
    password:
    properties:
      mail.smtp.auth: false
      mail.smtp.starttls.enable: false
```

### 3. Python (smtplib) 示例

```
import smtplib
from email.mime.text import MIMEText

msg = MIMEText('测试邮件正文')
msg['Subject'] = 'Hello from Mailpit'
msg['From'] = 'sender@example.com'
msg['To'] = 'recipient@example.com'

with smtplib.SMTP('localhost', 1025) as s:
    s.send_message(msg)
```

## 七、REST API 实战（自动化测试断言）

在 CI/CD 中，可以调用 Mailpit API 验证邮件是否发送成功、内容是否正确：

```
# 1. 列出最新邮件
curl http://localhost:8025/api/v1/messages?limit=1

# 2. 获取单封邮件详情（含 MIME 解析）
curl http://localhost:8025/api/v1/message/latest

# 3. 搜索包含关键词的邮件
curl "http://localhost:8025/api/v1/search?query=verification"

# 4. 清空收件箱
curl -X DELETE http://localhost:8025/api/v1/messages
```

注意：Mailpit API 的 `latest` 关键字可获取最新一封邮件，无需先查询 ID，适合测试断言。附件下载端点为 `/api/v1/message/{id}/attachment/{attachmentID}`。

## 八、邮件头解析与调试技巧

Mailpit 与 MailHog 的 Web 界面均可查看邮件的完整原始 MIME 头，这是调试邮件认证（SPF/DKIM/DMARC）的关键：

* **检查 Authentication-Results 头**：确认 SPF/DKIM/DMARC 认证结果是否符合预期
* **检查 DKIM-Signature 头**：验证签名选择器、规范算法与公钥匹配
* **检查 Received 头链**：理解邮件经过的服务器路径
* **检查 Message-ID**：排查重复发送问题

如需在线解析邮件头，可使用 ztpop.net 的[邮件头分析工具](/tools/mail-tools.html)。

## 九、常见问题

### Q1：Mailpit/MailHog 会真正投递邮件吗？

不会。二者仅捕获并存储邮件，不执行任何 MX 解析或 SMTP 投递，因此不会向真实收件人发送任何内容。这是「测试工具」的核心设计。

### Q2：如何持久化保存邮件？

Mailpit 默认使用 SQLite 持久化（数据目录可挂载卷）；MailHog 默认内存存储，重启丢失，需配置 MongoDB 或使用 `--storage mongodb://...`。

### Q3：可以在生产环境使用吗？

不建议。这是开发/测试工具，捕获邮件不投递，且 Web 界面默认无认证（可配置）。生产环境请使用真实 MTA 或邮件服务。

### Q4：与 mail-tester.com 的区别？

mail-tester.com 是面向投递质量检测的在线服务（发送邮件到随机地址后评分）；Mailpit/MailHog 是本地开发调试工具，二者用途不同。邮件投递质量检测可参考 ztpop.net 的[邮件 DNS 一键诊断](/tools/dns-check.html)。

参考：[datatracker.ietf.org](https://datatracker.ietf.org/doc/html/rfc5322)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailpit-mailhog-dev-mail-testing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
