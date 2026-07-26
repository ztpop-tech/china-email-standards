---
title: "CISA《增强电子邮件与 Web 安全》指南：DMARC、STARTTLS 与 HTTPS 落地实践"
source: "https://ztpop.net/kb/cisa-enhance-email-web-security.html"
license: CC-BY 4.0
---

# CISA《增强电子邮件与 Web 安全》指南：DMARC、STARTTLS 与 HTTPS 落地实践

## 概述

美国网络与基础设施安全局（CISA）在 Insights 文件《Enhance Email & Web Security》中，将钓鱼邮件与未加密 HTTP 列为组织网络安全的两大持续性漏洞通道。该指南源自联邦指令 BOD 18-01，CISA 鼓励州/地方/部落/属地政府及私营企业同等落地。核心结论：用 SPF、DKIM、DMARC 三段式消除域名欺骗，用 STARTTLS 与 HTTPS+HSTS 消除传输明文。

## 威胁背景：域名欺骗与明文 HTTP

攻击者伪造可信组织的发件域，发出看似合法的钓鱼邮件；与此同时，用户通过未加密 HTTP 提交的数据可被窃听、追踪与篡改。若攻击者对某域成功实施欺骗发信，会严重损害该组织的声誉，并诱使内部员工或公众基于虚假邮件行动。

## 邮件侧缓解：SPF / DKIM / DMARC 三段式

CISA 将邮件认证拆为三层：

1. **SPF（RFC 7208）**：声明哪些 IP 被授权代表该域发送邮件，相当于给外发邮件打"来源水印"。
2. **DKIM（RFC 6376）**：用域名私钥对邮件签名，接收方用公开密钥验证内容未被篡改。
3. **DMARC（RFC 7489）**：域所有者告知接收方——未通过 SPF/DKIM 的邮件应当如何处理，并接收反馈报告。

## DMARC 策略：从 p=none 到 p=reject

指南明确建议：最低先落地 `p=none` 以开始收集可见性，再逐步推进到 `p=quarantine`，最终将 `p=reject` 作为最强防护——在邮件送达前于服务端直接拒绝未认证邮件。DMARC 报告（ aggregate + forensic）让组织首次获得"谁在伪造我域"的情报，可定义多个接收地址。

## 传输加密：STARTTLS 与 HTTPS / HSTS

当接收邮件服务器支持时，STARTTLS 向发送方信号"本跳可加密"，虽不强制，但使被动中间人窃听更难实施。Web 侧则要求对所有对外域名实施 HTTPS 并启用 HSTS，禁用弱加密套件，杜绝明文 HTTP 带来的隐私泄露与内容篡改。

## 合规建议清单

| 动作 | 要求 |
| --- | --- |
| 邮件认证 | 部署 SPF + DKIM，DMARC 至少 `p=none`，目标 `p=reject` |
| 传输加密 | 启用 STARTTLS；对外域名全量 HTTPS + HSTS |
| 弱点治理 | 禁用弱加密标准（Web 与邮件） |
| 持续可见性 | 持续监控 DMARC 发现与报告 |

## 落地顺序建议

对正在做信创邮件替换或 Exchange 迁移的政企客户，可把 DMARC 监控作为邮件网关上线前的"体检"步骤：先以 `p=none` 收集一个月报告，确认无合法流量被误拦后，再切 `p=reject`。这与 NIST SP 800-177 对可信电子邮件的部署建议一致。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cisa-enhance-email-web-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
