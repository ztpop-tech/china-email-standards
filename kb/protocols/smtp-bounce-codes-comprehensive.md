---
title: "SMTP 退信码全面解读：DSN 状态码体系与各邮箱服务商自定义代码"
source: "https://ztpop.net/kb/smtp-bounce-codes-comprehensive.html"
license: CC-BY 4.0
---

# SMTP 退信码全面解读：DSN 状态码体系与各邮箱服务商自定义代码

参考 RFC 3461、RFC 3463、RFC 1894 及邮件服务商扩展码

SMTP 退信是邮件投递失败的正式通知。准确解读退信码可以快速定位问题根因。RFC 3463 定义了标准的 DSN（Delivery Status Notification）状态码体系，各邮箱服务商在此基础上增加增强型状态码。

## DSN 状态码体系

DSN 状态码由 RFC 3463 定义，格式为 `class.subject.detail`（例如 5.1.1）：

* **Class 2.X.X**：成功（Success）——邮件已成功投递
* **Class 4.X.X**：临时失败（Persistent Transient Failure）——邮件暂时未投递成功，可能会重试
* **Class 5.X.X**：永久失败（Permanent Failure）——邮件不可投递，不重试

## 常见 DSN 退信码详解

| 状态码 | 含义 | 原因 | 修复方案 |
| --- | --- | --- | --- |
| 4.4.1 | 无法连接远程 MX | DNS 解析失败或 MX 端口不可达 | 检查 MX DNS 记录和防火墙规则 |
| 4.4.2 | 连接超时 | 远程 MTA 无响应或网络问题 | 增加连接超时配置或排查网络 |
| 4.7.1 | 临时认证失败 | TLS 协商失败或证书问题 | 检查 TLS 配置和证书链 |
| 5.1.0 | 地址格式错误 | 收件人地址格式不合规 | 检查邮件地址是否包含非法字符 |
| 5.1.1 | 邮箱不存在 | 收件人地址在目标域中无效 | 立即从列表中移除该地址 |
| 5.1.2 | 收件人中继错误 | 目标域无法路由到邮件 | 检查 MX 记录和目标邮件系统 |
| 5.1.3 | 邮箱语法错误 | 地址的本地部分格式非法 | 使用 RFC 5321 校验地址有效格式 |
| 5.2.1 | 邮箱满 | 收件人邮箱已满无法接收 | 通知收件人清理邮箱，重试 |
| 5.2.2 | 超过限额 | 收件人接收速率超过限制 | 降低发送速率，间隔时间重试 |
| 5.2.3 | 邮件过大 | 邮件大小超过收件方限制 | 减小邮件大小或配置更大限额 |
| 5.4.1 | 无法路由 | 目标域的 MX DNS 记录缺失 | 通过 dig 验证 MX 记录 |
| 5.7.1 | 发送被拒 | 收件方拒绝接收来自该发送方的邮件 | 检查 IP 信誉和认证配置 |
| 5.7.26 | TLS 要求失败 | 收件方强制 TLS 但发件方未提供 | 配置 MTA-STS 和 DANE |

## Gmail 和 Outlook 自定义退信码

### Gmail 自定义代码

Gmail 的退信码通常在标准 DSN 码之后附加自定义信息：

* 5.7.1 (Google) - 发件信誉过低
* 5.7.1 (Gmail) - 邮件被认为是垃圾邮件
* 5.7.26 - Gmail 要求发件方配置 MTA-STS

### Outlook/Exchange Online 自定义代码

* 5.7.1 (OUTLOOK) - 发件方 IP 被单独阻止
* 5.7.25 - 发件方未通过 DMARC 认证
* 5.7.505 - 发件方域被列入"高置信度钓鱼"列表

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-bounce-codes-comprehensive.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
