---
title: "Cloudflare 2026 威胁形势报告揭示了哪些邮件安全发现？"
source: "https://ztpop.net/kb/cloudflare-email-security-2026.html"
license: CC-BY 4.0
---

# Cloudflare 2026 威胁形势报告揭示了哪些邮件安全发现？

1
Cloudflare 2026 威胁形势报告揭示了哪些邮件安全发现？
▼

**有效性度量（MOE）与高信任攻击**

Cloudforce One 提出“有效性度量”（MOE）框架：2026 年现代攻击者不再追求复杂与昂贵的一次性攻击，转而追求吞吐量与成果。窃取的会话令牌（身份）因 MOE 更高而受青睐；声誉护盾（LotX）提供免费、近乎不可追踪且高送达率的基础设施；AI 可自动发现连接最敏感数据的纽带。八趋势中与邮件直接相关者包括“令牌窃取致 MFA 失效”与“中继盲区导致内部品牌仿冒成为可能”。

**邮件认证缺口**

在对 4.5 亿封邮件的分析中，约 46% 未通过 DMARC 验证（一种邮件发件人认证协议），揭示出 PhaaS 机器人正迅速利用这一巨大攻击面。Cloudforce One 的 PhaaS 研究显示，攻击者借 Google Drive、Azure 等高信誉域名绕过安全过滤；并利用了邮件服务器未重新验证发件人身份的“中继盲区”，将高信任度品牌的仿冒邮件直接投递至用户收件箱。

**凭据与令牌**

遥测显示过去 3 个月内 63% 的登录凭据来自其他地方已泄露的账户凭据，94% 的登录尝试源自机器人。以 LummaC2 等信息窃取程序收集活动会话令牌，攻击者可绕过传统 MFA、直接进行认证后的操作。攻击者还积极将 Google Calendar、Dropbox、GitHub 等合法云工具武器化，以掩盖正常企业活动中的 C2 与恶意投递。

**防御建议**

对全域名实施 DMARC 执行（quarantine/reject）并核查转发场景下的对齐滑签；对 SaaS 与邮件集成的令牌生命周期及异常使用做监控；以 AI 驱动的邮件安全与收件箱回溯扫描类工具检测历史威胁；采用自主防御（autonomous defense）以机器速度响应。Cloudflare 认为，当威胁以机器速度移动时，以人为中心的防御不再是有效屏障。

参考：Cloudflare《2026 年威胁形势报告》（Cloudforce One）官方博客：https://blog.cloudflare.com/zh-cn/2026-threat-report/

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloudflare-email-security-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
