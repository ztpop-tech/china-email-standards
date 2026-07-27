---
title: "Microsoft 365 邮件身份验证机制解析：SPF/DKIM/DMARC 与复合验证（compauth）"
source: "https://ztpop.net/kb/microsoft-email-authentication.html"
license: CC-BY 4.0
---

# Microsoft 365 邮件身份验证机制解析：SPF/DKIM/DMARC 与复合验证（compauth）

## 概述

Microsoft 365（含 Exchange Online Protection / EOP 与 Microsoft Defender for Office 365）每天处理数十亿封邮件，其反钓鱼体系以 SPF、DKIM、DMARC 为基石，并叠加自有"隐式邮件验证（implicit email authentication）"。理解这套机制，对配置发往 Microsoft 365 的域、以及自建或信创邮件系统与 EOP 互通都至关重要。

## 三大基石：SPF / DKIM / DMARC

三者相互依赖、协同工作，单独部署任一部分都会导致防护不达标：

* **SPF（RFC 7208）**：在 DNS 声明授权发件 IP，仅验证信封发件人（MAIL FROM / Return-Path），不验证信头 From 域对齐。
* **DKIM（RFC 6376）**：用域私钥对邮件（含 From）签名，转发场景不受影响，弥补 SPF 在转发下的失效。
* **DMARC（RFC 7489）**：要求 SPF 或 DKIM 标识符与 RFC 5322 的 From 域对齐，并指定失败动作与报告。

## SPF 的验证盲区

SPF 仅校验 MAIL FROM（又称 5321.MailFrom、P1、信封发件人），并不检查信头 From（5322.From / P2）是否与之对齐。攻击者可以注册 proseware.com 并正确配置 SPF，却把信头 From 写成 woodgrovebank.com，从而"假阴性"通过 SPF。此外，服务器级转发会改写源 IP，使原 MAIL FROM 域未授权该转发器，造成"假阳性"误拦。每个子域需独立 SPF 记录，不继承父域。

## DKIM 与 DMARC 如何补位

DKIM 签名绑定信头 From（当选择器域与 From 对齐时），在托管或转发共用 MAIL FROM 时仍有效。DMARC 则显式要求对齐，解决了 SPF/DKIM 各自缺乏 From 域对齐检查的问题。需要注意的是，合法的中转服务若修改了邮件，可能破坏 SPF/DKIM 从而导致 DMARC 失败——此时应通过租户允许/阻止列表精确放行。

## ARC：为被修改的中转保留信任链

ARC（Authenticated Received Chain，RFC 8617）由已知会修改邮件的中转服务保留原始验证结果，接收方识别其为"可信 ARC 封印者（trusted ARC sealer）"后即可继承验证状态，补救 DMARC 因中转而失败的合法邮件。Microsoft 建议入站修改服务配置可信 ARC 封印者。

## 隐式验证与复合认证（compauth）

由于 SMTP（RFC 5321 / RFC 5322）本身不验证发件人真实身份，且互联网上发件人验证采用不全，Microsoft 365 在常规 SPF/DKIM/DMARC 检查之外引入隐式邮件验证，综合发件人信誉、发件/收件历史、行为分析等信号，输出单一"复合认证（composite authentication，compauth）"值，写入 Authentication-Results 头：

```
Authentication-Results: compauth=pass reason=109
Authentication-Results: compauth=fail reason=001
```

关键行为：复合验证失败并不直接阻断邮件，Microsoft 采用整体评估策略，结合邮件可疑度与 compauth 结果，避免误拦未严格遵循协议的正常域。例如域无 SPF/DKIM/DMARC 记录时 `compauth=fail reason=001`；SPF 或 DKIM 域与 From 匹配时 `compauth=pass reason=109`。

## 发件方部署建议（渐进式）

1. 发布 SPF：先列已知源，用 `~all`（soft fail），纳入本地、SaaS、云托管后再改 `-all`（hard fail）。
2. 配置 DKIM：对出站邮件数字签名。
3. 配置 DMARC：设定对齐要求、失败动作（建议从 p=none 起步收集报告）与 rua/ruf 报告地址。
4. 批量发件人：确保 From 域与通过 SPF/DMARC 的域一致。
5. 误拦救济：使用欺骗情报洞察、租户允许/阻止列表、安全发件人列表放行。

## 与邮件安全网关、信创邮件的对接

当政企进行信创邮件替换或 Exchange 迁移时，新邮件系统发往 Microsoft 365 的邮件必须满足上述认证要求，否则将被标记为欺骗或进垃圾箱。在 RFC 7208 / RFC 6376 / RFC 7489 / RFC 8617 之上部署邮件安全网关，可统一签发 DKIM、发布 DMARC 策略，并向 EOP 呈现一致的可信身份。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/microsoft-email-authentication.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
