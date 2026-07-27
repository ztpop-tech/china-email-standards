---
title: "澳大利亚 ACSC 邮件系统加固指南：Essential Eight 视角下的邮件防护基线"
source: "https://ztpop.net/kb/acsc-email-hosting-hardening.html"
license: CC-BY 4.0
---

# 澳大利亚 ACSC 邮件系统加固指南：Essential Eight 视角下的邮件防护基线

## 概述

澳大利亚网络安全中心（ACSC）是澳政府网络安全技术权威，其 **Essential Eight** 是一套被广泛采用的优先缓解策略。邮件系统作为最易被利用的入口，几乎贯穿 Essential Eight 的多条策略。以下以邮件视角精译 ACSC 的加固基线，可直接作为国产/信创邮件系统的配置清单。

## 建议一：禁用遗留认证 + 强制 MFA

Essential Eight 的第一要务就是"打补丁、限接口、强认证"。对邮件：关闭所有遗留/基础认证协议，统一现代认证，并对邮箱访问强制多因素认证。对特权邮箱与高管，采用抗钓鱼 MFA。这一步直接切断凭据窃取后的邮箱被盗链条。

## 建议二：强制域名认证 SPF/DKIM/DMARC

发布并逐步强制 SPF、DKIM 与 DMARC 到 `p=reject`，对齐 From 域。ACSC 强调把 DMARC 报告接入持续监控，及时发现伪造尝试与配置漂移。这与 CISA BOD 18-01、NCSC 立场一致，是国际共识。

## 建议三：阻断外部自动转发

默认禁止邮箱向外部域自动转发，防止敏感邮件被悄悄抄送出境。确有需要则走审批与审计。对 BEC 攻击者常用的"植入转发规则"行为，应纳入常态化检测。

## 建议四：链接与附件防护

启用安全链接改写与实时检测（如 Safe Links 类机制），对可疑 URL 做时间点击查杀；限制宏附件、归档附件的执行，减少初始入侵向量。对高价值收件人启用更严格的隔离策略。

## 建议五：日志与邮箱规则狩猎

保留并集中邮件网关与邮箱审计日志，定期"狩猎"异常：可疑的收件箱规则（转发/标记已读/删除）、异常的海外登录、突发的外发高峰。主动狩猎比被动拦截更能发现潜伏的 BEC 跳板。

## 对国产化邮件的映射

Essential Eight 的邮件基线可逐条映射为昆仑邮件系统的出厂配置：遗留认证端口封闭、MFA 强制开关、DMARC p=reject 模板、外部转发默认关、安全链接与附件沙箱、统一日志与规则审计。政务与国企在信创替代时，可直接以 Essential Eight 作为验收对照表。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/acsc-email-hosting-hardening.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
