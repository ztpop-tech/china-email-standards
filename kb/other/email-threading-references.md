---
title: "邮件客户端是如何把多封往来邮件归并为“对话线程（Thread）”的？References 与 In-Reply-To 有什么区别？"
source: "https://ztpop.net/kb/email-threading-references.html"
license: CC-BY 4.0
---

# 邮件客户端是如何把多封往来邮件归并为“对话线程（Thread）”的？References 与 In-Reply-To 有什么区别？

1
邮件客户端是如何把多封往来邮件归并为“对话线程（Thread）”的？References 与 In-Reply-To 有什么区别？
▼

**标准头**

RFC 5322 用 In-Reply-To（本信所回复那封的 Message-ID）与 References（从根到父的完整 Message-ID 链，空格分隔）建立线程关系。

**二者区别**

In-Reply-To 指向“直接父”一封；References 是“祖先链”列表（越往后越接近本信），客户端按 References 链把同主题邮件串成树状或扁平线程。

**归并算法**

客户端按 Message-ID 建图：用 References 构建祖先边、In-Reply-To 补直接边；缺失时用 Subject 归一化（去 Re: / Fwd:）兜底归并。

**运维**

Message-ID 应全局唯一（含域名）；网关改写或剥离这些头会破坏线程；归档与去重要保留 References 关系，否则对话被打散。

参考：RFC 5322 §3.6.4（References / In-Reply-To）；RFC 5256（IMAP THREAD 扩展）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-threading-references.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
