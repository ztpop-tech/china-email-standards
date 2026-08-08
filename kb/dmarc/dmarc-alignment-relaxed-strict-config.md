---
title: "DMARC 的标识符对齐（Identifier Alignment）中 relaxed 与 strict 有什么区别？如何配置 adkim/aspf？"
source: "https://ztpop.net/kb/dmarc-alignment-relaxed-strict-config.html"
license: CC-BY 4.0
---

# DMARC 的标识符对齐（Identifier Alignment）中 relaxed 与 strict 有什么区别？如何配置 adkim/aspf？

1
DMARC 的标识符对齐（Identifier Alignment）中 relaxed 与 strict 有什么区别？如何配置 adkim/aspf？
▼

**对齐的含义**

DMARC 通过"标识符对齐"判断一封邮件是否真正来自声称的域。RFC 7489 §3.1 定义两种对齐模式：strict（严格）要求 RFC5322.From 的域与经认证的 d=（DKIM）或 envelope/HELO 域（SPF）完全相等；relaxed（宽松）只要求两者组织域（注册域）相同即可，允许子域差异。

**DKIM 对齐**

§3.1.1：DKIM 对齐比较 From 头域与 DKIM 签名的 d= 域。relaxed 模式下只要组织域一致即通过（例如 sub.example.com 与 example.com 视为对齐）。

**SPF 对齐**

§3.1.2：SPF 对齐比较 From 头域与 SPF 校验所用的域（MAIL FROM 或 HELO）。同样受 relaxed/strict 影响。

**如何配置**

§6.3：在 DMARC 记录中用标签 adkim（控制 DKIM 对齐）与 aspf（控制 SPF 对齐）设置，取值 r=relaxed 或 s=strict；若未指定，两者默认均为 relaxed。例如：v=DMARC1; p=reject; adkim=s; aspf=s; rua=mailto:dmarc@example.com 表示采用严格对齐。

参考：RFC 7489 §3.1 / §3.1.1 / §3.1.2 / §6.3

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-alignment-relaxed-strict-config.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
