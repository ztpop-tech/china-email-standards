---
title: "amavisd-new 在邮件内容过滤里扮演什么角色？它如何串联杀毒与反垃圾？"
source: "https://ztpop.net/kb/email-amavis-content-filter.html"
license: CC-BY 4.0
---

# amavisd-new 在邮件内容过滤里扮演什么角色？它如何串联杀毒与反垃圾？

1
amavisd-new 在邮件内容过滤里扮演什么角色？它如何串联杀毒与反垃圾？
▼

**定位**

amavisd-new 是“内容过滤中枢”：以 SMTP 代理模式（前置或旁路）接收邮件，调用 SpamAssassin（反垃圾）与 ClamAV（杀毒）等，再决定通过/标记/隔离/拒。

**代理模式**

常见“双向 SMTP”部署：MTA 把信交给 amavis 端口，amavis 处理后回交 MTA 投递；支持 policy banks 按“入站/出站/内部”应用不同策略。

**动作**

据扫描结果打头（X-Spam-Status、病毒名）、按策略 quarantine（隔离区）、加白/黑名单、改信体；与 MTA 的 milter/过滤钩子对接。

**实践**

企业邮件网关常用 amavis 统一编排杀毒+反垃圾+合规扫描；注意资源（扫描耗 CPU/内存）与队列排队时延，需按量扩容。

参考：amavisd-new 文档（policy banks / quarantine）；与 SpamAssassin/ClamAV 集成

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-amavis-content-filter.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
