---
title: "邮件反馈循环 FBL/ARF 完全指南 — RFC 5965/6650：Yahoo CFL、Microsoft JMRP 与开源 FBL 处理器 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/email-feedback-loop-arf.html"
license: CC-BY 4.0
---

# 邮件反馈循环 FBL/ARF 完全指南 — RFC 5965/6650：Yahoo CFL、Microsoft JMRP 与开源 FBL 处理器 · ztpop 邮件技术知识库

邮件反馈循环 FBL/ARF 完全指南 — RFC 5965/6650：Yahoo CFL、Microsoft JMRP 与开源 FBL 处理器

## 摘要

反馈循环（Feedback Loop, FBL）是大型邮箱服务商向发送方提供的一种"反向信号"机制：当收件人将来自某个发送方的邮件标记为"垃圾邮件"（Report Spam / This is Junk）时，邮箱服务商生成一份标准化的滥用报告（Abuse Report），发送回原始发件方。发件方据此可以识别出投诉用户并自动将其从邮件列表中移除，或调整发送策略以降低投诉率。FBL 的技术基座是 ARF（Abuse Report Format），由 RFC 5965 定义其可扩展框架、RFC 6650 定义其创建与使用规范。本文覆盖 ARF 的 MIME 结构（multipart/report、feedback-type 字段）、Yahoo CFL、Microsoft JMRP、Comcast、Mail.ru 四大主流 FBL 的注册流程与消息格式差异，以及开源 FBL 处理器（php-list-fbl、自定义 Postfix milter）的实际部署——包括如何将 FBL 投诉数据接入自动化退订流程，构建闭环的邮件列表管理。

## 1. ARF 标准：RFC 5965 与 RFC 6650

### 1.1 ARF 的三层 MIME 结构（RFC 5965 §3）

ARF 报告是一种特殊的 MIME 消息，使用
`multipart/report`
作为顶层 Content-Type，内部包含三个 MIME 部分：

1. **Part 1 — text/plain（人类可读摘要）**
   ：以自然语言描述此次反馈的概要信息。通常包含："This is a spam report for an email message received from  on ."
2. **Part 2 — message/feedback-report（机器可读报告）**
   ：包含 RFC 5965 §4 定义的标准 ARF header fields，以 key: value 格式逐行呈现。核心字段包括
   `Feedback-Type`
   、
   `User-Agent`
   、
   `Version`
   、
   `Original-Mail-From`
   、
   `Original-Rcpt-To`
   、
   `Source-IP`
   、
   `Reported-Domain`
   等。
3. **Part 3 — message/rfc822（原始邮件或部分邮件）**
   ：触发投诉的原始邮件内容。根据发送方与接收方的双边协议，可能包含完整邮件（full message）或仅头部（headers only）。

```
From: feedback-loop@receiver.example.net
To: abuse@send.example.com
Subject: Abuse Report for send.example.com
Content-Type: multipart/report; report-type="feedback-report"; boundary="===fbl-boundary==="

--===fbl-boundary===
Content-Type: text/plain; charset="utf-8"

This is a feedback report for a message received from 192.0.2.200
on 2026-07-10T14:32:15Z. The message was classified as spam by the
recipient.

--===fbl-boundary===
Content-Type: message/feedback-report

Feedback-Type: abuse
User-Agent: ReceiverFBL/2.0
Version: 1
Original-Mail-From: sender@send.example.com
Original-Rcpt-To: recipient@receiver.example.net
Arrival-Date: 2026-07-10T14:32:15Z
Source-IP: 192.0.2.200
Reported-Domain: send.example.com
Authentication-Results: receiver.example.net; spf=pass smtp.mailfrom=send.example.com;
    dkim=pass header.d=send.example.com;
    dmarc=pass header.from=send.example.com

--===fbl-boundary===
Content-Type: message/rfc822

[original message headers + optionally body]
--===fbl-boundary===--
```

### 1.2 feedback-type 字段的取值规范（RFC 5965 §4.1 / RFC 6650 §2.2）

`feedback-type`
是 ARF 报告中最关键的分类字段：

1.2 feedback-type 字段的取值规范（RFC 5965 §4.1 / RFC 6650 §2.2）

| feedback-type | 含义 | RFC 引用 |
| --- | --- | --- |
| `abuse` | 未经请求的邮件或违反服务条款的滥用行为（最常见的投诉类型） | RFC 5965 §4.1 |
| `auth-failure` | 邮件认证失败（SPF/DKIM/DMARC 不通过），通常用于 DMARC ruf 报告 | RFC 6591 §3 |
| `fraud` | 欺诈性邮件（钓鱼、BEC、虚假账单等） | RFC 6650 §2.2 |
| `virus` | 携带恶意软件的邮件 | RFC 6650 §2.2 |
| `opt-out` | 收件人请求取消订阅但发送方未处理，邮箱服务商代为发送的退订请求 | RFC 6650 §2.2 |
| `not-spam` | 收件人将邮件从垃圾箱移至收件箱（正向反馈），部分 FBL 支持此类型 | RFC 6650 §2.2（注册为扩展） |

### 1.3 ARF 的 header fields 全量表（RFC 5965 §4）

1.3 ARF 的 header fields 全量表（RFC 5965 §4）

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `Feedback-Type` | 是 | 滥用类型分类（abuse / fraud / virus / opt-out / auth-failure / not-spam） |
| `User-Agent` | 是 | 生成该报告的软件名称及版本 |
| `Version` | 是 | ARF 版本号（当前为 1） |
| `Original-Mail-From` | 否 | 触发投诉的原始邮件信封发件人（RFC5321.MailFrom） |
| `Original-Rcpt-To` | 否 | 触发投诉的原始邮件收件人 |
| `Arrival-Date` | 否 | 原始邮件到达接收方 MTA 的时间（RFC 5322 date-time） |
| `Source-IP` | 否 | 发起 SMTP 连接的源 IP 地址 |
| `Reported-Domain` | 否 | 被投诉的域名 |
| `Authentication-Results` | 否 | 原始邮件的 SPF/DKIM/DMARC 认证结果（RFC 8601 格式） |
| `Original-Envelope-Id` | 否 | 原始邮件的 SMTP 信封 ID（RFC 3461 DSN ENVID 参数） |
| `DKIM-Domain` | 否 | DKIM 签名的 d= 域 |

M3AAWG（Messaging, Malware and Mobile Anti-Abuse Working Group）发布了独立的 FBL 最佳实践文档，建议接收方 MTA 运营商在生成 ARF 报告时至少包含
`feedback-type`
、
`source-ip`
和
`original-rcpt-to`
，以便发件方能够准确地定位告警对象。

## 2. 四大主流邮箱的 FBL 注册与差异

### 2.1 Yahoo CFL（Complaint Feedback Loop）

Yahoo 的 CFL 是最早大规模部署的 FBL 系统之一。注册流程：

* **前置条件**
  ：发件域必须具备有效的 SPF 和 DKIM DNS 记录（至少
  `p=none`
  的 DMARC 不是硬性要求但强烈建议）。
* **注册入口**
  ：通过 Yahoo Sender Hub（
  `senders.yahooinc.com`
  ）的 Postmaster 注册中心提交申请。
* **DKIM 验证**
  ：Yahoo 会向发件域发送一封带有特定 DKIM 签名的验证邮件，域管理员必须能够接收并确认该邮件。
* **报告格式**
  ：ARF 格式，
  `feedback-type: abuse`
  ，Part 3 包含原始邮件的完整头部（不含正文）。Yahoo CFL 特殊之处在于其 ARF 报告的
  `User-Agent`
  字段固定为
  `Yahoo!-Mail-Feedback/1.0`
  。报告发送频率为实时（收件人点击 "This is Spam" 后数分钟内发送）。
* **退订一体化要求**
  ：Yahoo 要求 CFL 注册者在收到 abuse 投诉后必须在 48 小时内停止向该收件人发送邮件（即实施自动退订）。违者可能被吊销 CFL 资格。

### 2.2 Microsoft JMRP（Junk Mail Reporting Program）

Microsoft 的 JMRP 覆盖 Outlook.com、Hotmail、Live 等 Microsoft 邮箱服务：

* **前置条件**
  ：发件域必须通过 SPF 认证，建议同时部署 DKIM 和 DMARC。Microsoft 对发送方的 IP 地址信誉有独立的评估——已在 Microsoft SNDS（Smart Network Data Services）中显示良好信誉的 IP 更容易获得 JMRP 批准。
* **注册入口**
  ：
  `postmaster.live.com`
  → JMRP Enrollment。需要 Microsoft 账户登录。
* **报告格式**
  ：JMRP 使用 Microsoft 自定义的 ARF 变体（非纯 ARF）。
  `feedback-type`
  为
  `abuse`
  。Microsoft JMRP 的 Part 3 仅包含原始邮件头部（headers only）——正文（body）被删除以保护收件人隐私。
* **聚合频率**
  ：与 Yahoo CFL 的实时发送不同，JMRP 以压缩包（zip 文件）的形式发送，通常每小时或每几小时间隔聚合一批投诉报告。
* **IP 粒度**
  ：JMRP 的上报粒度是按 IP 地址的，不是按域名的。这意味着如果一个 IP 地址被多个域名共享，JMRP 报告会将这些投诉一起发送到该 IP 对应的 JMRP 联系人。

### 2.3 Comcast FBL

Comcast（Xfinity）为美国最大的宽带 ISP 之一，其 FBL 覆盖 Comcast 自有邮箱用户：

* **前置条件**
  ：发件方必须在其邮件列表中实施 List-Unsubscribe header（RFC 8058）和明确的退订机制。
* **注册入口**
  ：通过 Comcast Postmaster（
  `postmaster.comcast.net`
  ）提交申请。Comcast 审核较严——申请表格需要详细描述邮件列表类型、用户获取方式、退订流程。
* **报告格式**
  ：标准 ARF 格式，
  `feedback-type: abuse`
  。Part 3 包含原始邮件头部。
* **特殊字段**
  ：Comcast FBL 的 ARF 报告中包含一个自定义字段
  `X-CFL-Origin`
  ，标记投诉来源（Webmail、IMAP 客户端等）。

### 2.4 Mail.ru FBL

Mail.ru 是俄罗斯最大的邮件服务商，其 FBL 是俄语互联网区域邮件列表管理的关键工具：

* **注册入口**
  ：
  `postmaster.mail.ru`
  ，需要 Mail.ru 账户并完成域名所有权验证。
* **报告格式**
  ：Mail.ru 使用自己的 JSON API 格式（非 ARF），不同于其他西方邮箱服务商的 MIME ARF 格式。FBL 数据通过 Mail.ru Postmaster API 的
  `/api/v2/spam-reports`
  端点以 JSON 格式拉取，每天更新一次。
* **API 认证**
  ：需要 OAuth 2.0 持有者令牌和域名所有权验证。
* **字段映射**
  ：Mail.ru JSON 报告中的
  `complaint_rate`
  （投诉率百分比）和
  `spam_reports_count`
  字段对应 ARF 的
  `feedback-type: abuse`
  统计聚合。

## 3. 开源 FBL 处理器：解析与自动退订

### 3.1 php-list-fbl：PHP 邮件列表软件的 FBL 集成

php-list-fbl 是 PHPList 邮件列表软件的 FBL 处理插件。它通过 IMAP 定期拉取专用 FBL 邮箱中的投诉报告邮件，解析 ARF 格式的
`Original-Rcpt-To`
字段，提取被投诉的收件人地址，自动标记为"已退订"或放入黑名单。

```
# php-list-fbl 的核心处理逻辑（伪代码）
# 1. 连接 FBL 邮箱，拉取未读邮件
$imap = imap_open("{imap.example.com:993/ssl}INBOX", "fbllist@example.com", "password");
$emails = imap_search($imap, 'UNSEEN');

foreach ($emails as $email_num) {
    # 2. 解析 MIME multipart/report 结构
    $structure = imap_fetchstructure($imap, $email_num);
    # 查找 message/feedback-report part
    foreach ($structure->parts as $part) {
        if ($part->subtype == 'FEEDBACK-REPORT') {
            $arf_body = imap_fetchbody($imap, $email_num, $part_num);
            # 3. 解析 ARF header fields
            foreach (explode("\n", $arf_body) as $line) {
                if (strpos($line, 'Original-Rcpt-To:') === 0) {
                    $complaint_recipient = trim(substr($line, 19));
                    # 4. 自动退订
                    php_list_unsubscribe_user($complaint_recipient);
                    log_fbl_action($complaint_recipient, 'auto-unsubscribe');
                }
            }
        }
    }
    imap_delete($imap, $email_num);
}
```

### 3.2 自定义 Postfix FBL Milter

Postfix Milter（Mail Filter）接口允许在 SMTP 层面或通过邮件交付路径拦截和处理邮件。构建一个 FBL 专用 milter 的方案：

```
#!/usr/bin/env python3
"""
fbl-milter.py — 自定义 Postfix FBL 处理器（基于 pymilter）
功能：(1) 拦截发往 fbl@example.com 的 ARF 报告
      (2) 解析 ARF header fields，提取 Original-Rcpt-To
      (3) 自动将投诉收件人加入 Postfix 的黑名单 access 表
      (4) 生成 FBL 统计日志
"""
import Milter
import email
import re
from io import BytesIO

class FBLMilter(Milter.Base):
    def __init__(self):
        self.body = b""

    def body(self, chunk):
        self.body += chunk
        return Milter.CONTINUE

    def eom(self):
        """End of message — 解析完整 ARF 报告"""
        msg = email.message_from_bytes(self.body)

        # 检查是否为 ARF 报告
        ct = msg.get_content_type()
        if ct != 'multipart/report':
            return Milter.CONTINUE

        for part in msg.walk():
            if part.get_content_type() == 'message/feedback-report':
                arf_payload = part.get_payload()
                if isinstance(arf_payload, list):
                    arf_payload = arf_payload[0].get_payload()
                # 解析 ARF header fields
                for line in arf_payload.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('original-rcpt-to:'):
                        rcpt = line.split(':', 1)[1].strip()
                        print(f"FBL Complaint: {rcpt}")
                        # 写入 Postfix access 表
                        with open('/etc/postfix/fbl_blacklist', 'a') as f:
                            f.write(f"{rcpt} REJECT FBL complaint\n")
                        # 刷新 Postfix access 数据库
                        import subprocess
                        subprocess.run(['postmap', '/etc/postfix/fbl_blacklist'])
                        break

        self.body = b""
        return Milter.ACCEPT

def main():
    Milter.factory = FBLMilter
    Milter.runmilter('fbl_milter', '/var/run/fbl-milter/fbl.sock', 240)

if __name__ == '__main__':
    main()
```

```
# /etc/postfix/main.cf 中启用 FBL milter
smtpd_milters = unix:/var/run/fbl-milter/fbl.sock

# /etc/postfix/fbl_blacklist 格式
# recipient@example.com REJECT FBL complaint

# 在 smtpd_recipient_restrictions 中添加 access 表检查
smtpd_recipient_restrictions =
    ...
    check_recipient_access hash:/etc/postfix/fbl_blacklist
    ...
```

## 4. FBL 处理的最佳实践

### 4.1 投诉率阈值与响应机制

Industry standard thresholds (per M3AAWG best practices):

* **警告阈值**
  ：投诉率 > 0.1%（即每 1,000 封投递成功邮件中超过 1 封被投诉）。此时应审查最近的邮件列表变更或发送内容。
* **紧急阈值**
  ：投诉率 > 0.3%。此时应立即暂停该邮件列表或发送 IP 的发送活动，调查原因。
* **黑名单阈值**
  ：投诉率 > 1.0%。此时邮箱服务商通常会主动暂停或降级该发送 IP 的邮件投递。

### 4.2 自动退订的 48 小时原则

FBL 投诉处理的第一优先级是立即停止向投诉用户发送邮件。Yahoo 和 Microsoft 均要求 48 小时内完成退订操作。实现方式：

1. 从 ARF 报告的
   `Original-Rcpt-To`
   字段提取被投诉的收件人地址；
2. 在邮件列表数据库中查询该地址，标记为
   `status=unsubscribed`
   （而非删除——保留记录用于 FBL 审计）；
3. 记录投诉时间、来源 FBL、
   `Feedback-Type`
   等信息到审计日志；
4. 未来 30 天内不再向该地址发送任何邮件。

### 4.3 昆仑邮件系统的 FBL 集成实践

昆仑邮件系统在中大型企业邮件运营中需要面向数亿用户的发送规模。FBL 集成流程为：(1) 为每个客户域注册 Yahoo CFL 和 Microsoft JMRP（按 IP 地址粒度），(2) 使用专用的 FBL 处理 IMAP 邮箱接收 ARF 报告，(3) Python 解析器提取投诉者地址并写入黑名单数据库，(4) 通过 Grafana 面板按域维度监控投诉率，（5）每日生成 FBL 汇总报告发送给客户管理员。该流程使邮件列表的投诉率从注册 FBL 前的平均 0.8% 降至 0.1% 以下——通过自动退订机制，每条投诉只发生一次，而不是每周从同一用户收到 3 条投诉。

### 参考文献

1. RFC 5965 — An Extensible Format for Email Feedback Reports (IETF, August 2010). 第 3 节 ARF 的三层 MIME multipart/report 结构定义，第 4 节 ARF header fields 全量表（feedback-type、user-agent、original-mail-from 等），第 4.1 节 feedback-type 字段的 abuse/fraud/virus/other 四类初始取值.
2. RFC 6650 — Creation and Use of Email Feedback Reports: An Applicability Statement for the Abuse Reporting Format (ARF) (IETF, June 2012). 第 2 节对 feedback-type 进行了扩展（新增 opt-out、not-spam 等类型），第 4 节定义了 ARF 在 FBL 场景下的生产部署最佳实践.
3. RFC 6591 — Authentication Failure Reporting Using the Abuse Report Format (AFRF) (IETF, April 2012). 第 3 节定义了 auth-failure feedback-type 用于 DMARC 失败取证报告，与 FBL abuse 类型的互操作考量.
4. RFC 8058 — Signaling One-Click Unsubscribe for Email (IETF, January 2017). List-Unsubscribe header 及 List-Unsubscribe-Post 的单步退订机制，Comcast FBL 注册的前置条件.
5. RFC 8601 — Message Header Field for Indicating Message Authentication Status (IETF, May 2019). 第 2 节 Authentication-Results header 的标准格式，ARF 报告中
   `Authentication-Results`
   字段的引用规范.
6. M3AAWG Best Practices for Feedback Loop Operations (M3AAWG, 2018). 投诉率阈值（0.1%/0.3%/1.0%）、FBL 处理 SLA（48 小时退订）、ARF Part 3 内容的隐私考量.
7. GB/T 30283-2020 — 信息安全技术 电子邮件系统安全技术要求. 第 5.3 节 垃圾邮件处理，要求邮件系统应具备反馈处理与投诉闭环能力.
8. NIST SP 800-177 Rev.1 — Trustworthy Email (NIST, February 2019). 第 5.3 节 Feedback Loops，将 FBL 列为发送方声誉管理的必要组件.
9. Yahoo Sender Hub —
   <https://senders.yahooinc.com/complaint-feedback-loop/>
   . Yahoo CFL 注册入口与技术文档.
10. Microsoft JMRP —
    <https://sendersupport.olc.protection.outlook.com/pm/services.aspx>
    . JMRP 注册入口与 Microsoft SNDS 数据服务.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-feedback-loop-arf.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
