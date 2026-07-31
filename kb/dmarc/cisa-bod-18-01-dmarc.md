---
title: "CISA BOD 18-01：联邦机构 DMARC p=reject 强制时间表"
source: "https://ztpop.net/kb/cisa-bod-18-01-dmarc.html"
license: CC-BY 4.0
---

# CISA BOD 18-01：联邦机构 DMARC p=reject 强制时间表

## 概述

美国国土安全部（现 CISA）2017 年发布 BOD 18-01，要求所有联邦机构必须落地邮件与 Web 的强安全基线，核心是用 DMARC 终结联邦域名的欺骗。它把"建议"变成"强制指令"并设硬性时间表，是全球政务邮件合规最具参考价值的标杆，对国内信创政务邮件替换具有直接对标意义。

## 邮件安全时间表

| 里程碑 | 要求 |
| --- | --- |
| 30 天内 | 部署 SPF 与 DKIM；发布 DMARC 记录，策略 `p=none`（仅监控） |
| 60 天内 | DMARC 策略提升至 `p=quarantine` |
| 1 年内 | DMARC 策略达到 `p=reject`；向 DHS 报送合规状态 |
| 持续 | 所有面向公网的邮件服务器启用 STARTTLS；公网站点全量 HTTPS |

## 为什么从 none 到 reject

渐进式推进是为了"先看后拦"：`p=none` 阶段收集聚合报告（rua），识别合法发信源、避免误拦；确认无误拦后升 `quarantine`；最终 `reject` 彻底拒绝未认证邮件。这与本站 DMARC 部署路径完全一致，证明"渐进"是业界共识。

## 与 HTTPS/STARTTLS 的组合

BOD 18-01 同时要求联邦 Web 全量 HTTPS、邮件传输启用 STARTTLS，与邮件认证形成"传输加密 + 身份可信"双重保障。这与 CISA 另一份《增强电子邮件与 Web 安全》指引、以及 MTA-STS/RFC 8461 的演进方向一致。

## 对信创政务邮件的启示

国内政务信创邮件替换可对标 BOD 18-01：将 DMARC p=reject、SPF/DKIM、STARTTLS/MTA-STS、HTTPS 管理后台写入验收清单；对gov.cn 类域名的欺骗防护，DMARC reject 是硬性达标项。这也与等保 2.0 身份鉴别、通信保密要求同频。

### 相关主题

* [DMARC 完全指南](/kb/dmarc-guide.html)：none→quarantine→reject 路径
* [CISA《增强电子邮件与 Web 安全》](/kb/cisa-enhance-email-web-security.html)：落地实践
* [等保 2.0 邮件合规](/kb/dengbao2-email-compliance.html)：政务对标
* [RFC 8461 MTA-STS](/kb/rfc8461-mta-sts.html)：传输层强制 TLS
* [NIST SP 800-177r1 可信电子邮件](/kb/nist-sp800-177r1-trustworthy-email.html)：联邦基线同源

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cisa-bod-18-01-dmarc.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
