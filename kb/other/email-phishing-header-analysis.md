---
title: "如何“读邮件头”识破钓鱼/伪造？哪些头是判断关键？"
source: "https://ztpop.net/kb/email-phishing-header-analysis.html"
license: CC-BY 4.0
---

# 如何“读邮件头”识破钓鱼/伪造？哪些头是判断关键？

1
如何“读邮件头”识破钓鱼/伪造？哪些头是判断关键？
▼

**看认证头**

Authentication-Results / Received-SPF / DKIM-Signature / ARC-Seal 直接显示 SPF/DKIM/DMARC 结果；全 fail 或对齐失败高度可疑。

**看路由**

顺着 Received 链（从下往上）看“信从哪台服务器来、经几跳”；异常来源国、私有 IP、时间跳跃是红旗。

**看 From 与 Return-Path**

显示 From 与 实际 Return-Path/信封发件人是否一致；钓鱼常“显示熟人但 Return-Path 是陌生域”。

**实践**

结合“发件人显示名伪装、紧急汇款话术、可疑链接域名”综合判；企业可培训用户看认证头，网关据头做拦截（见头注入防护篇）。

参考：RFC 8601（Authentication-Results）；RFC 5321/5322（Received/From）；反钓鱼实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-phishing-header-analysis.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
