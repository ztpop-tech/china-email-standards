---
title: "DMARC 的「标识符对齐」到底在比什么？adkim 与 aspf 的严格与宽松差在哪？"
source: "https://ztpop.net/kb/auth-dmarc-identifier-alignment.html"
license: CC-BY 4.0
---

# DMARC 的「标识符对齐」到底在比什么？adkim 与 aspf 的严格与宽松差在哪？

1
DMARC 的「标识符对齐」到底在比什么？adkim 与 aspf 的严格与宽松差在哪？
▼

**先纠正一个常见误解：SPF 过了不等于 DMARC 过了**

DMARC 的判定不是「SPF 通过或 DKIM 通过」，而是「**存在一个通过的认证机制，且其标识符与 RFC5322.From 头域中的域名对齐**」。RFC 7489 第 3.1 节（Identifier Alignment）正是为此而设：认证机制各自验证的域名未必是收件人看到的发件域，只有把两者绑定，认证才对「防冒充」有意义。

因此排障第一步永远是回答：**这封信通过的是哪个机制？它认证的域是什么？From 域又是什么？**三个答案凑齐，结论自明。

**DKIM 对齐：比的是签名的 d= 与 From 域**

RFC 7489 第 3.1.1 节（DKIM-Authenticated Identifiers）规定，DKIM 侧参与对齐的标识符是 `DKIM-Signature` 中 `d=` 标签所示的域。判定逻辑：

* **宽松（adkim=r，默认）**：`d=` 与 From 域的**组织域相同**即对齐。例如 From 为 `news.example.com`、`d=example.com`，对齐成立。
* **严格（adkim=s）**：要求**完全相同**，上例即不对齐。

**运维要点：**一封信可以带多个 DKIM 签名，只要**其中任意一个**既验签通过又对齐，DKIM 侧即算通过。所以给邮件同时打「平台签名」与「自有域签名」是提高通过率的常规做法。

**SPF 对齐：比的是 MAIL FROM 域与 From 域**

RFC 7489 第 3.1.2 节（SPF-Authenticated Identifiers）规定，SPF 侧参与对齐的是 **RFC5321.MailFrom**（信封发件人）的域；当 MAIL FROM 为空（如退信）时，改用 EHLO 中的主机名。判定逻辑同样分 `aspf=r`（组织域相同）与 `aspf=s`（完全相同）。

**这里是最高频的踩坑点：**许多外发通道会把信封发件人改写成自己的退信域，此时 SPF 明明 pass，却因为与 From 域不同而**不对齐**，DMARC 侧 SPF 判定为失败。这类场景必须靠 DKIM 对齐兜底。

**adkim / aspf 怎么填：默认宽松，收紧要有前提**

两个标签在 RFC 7489 第 6.3 节（General Record Format）定义，**未显式声明时默认值均为 r（宽松）**。选择建议：

1. **默认保持 r。**宽松模式允许子域与组织域互认，能覆盖绝大多数正常业务（如用子域发送通知信），显著降低误伤。
2. **只有在完全掌握全部发送源、且各源都能以精确同名域签名时，才考虑 s。**严格模式确实能压缩「攻击者注册子域或利用宽松匹配」的空间，但代价是任何子域差异都会导致失败。
3. **切换前先看数据。**用聚合报告确认现网是否存在依赖组织域匹配的合法流量，再决定是否收紧。

**国际化域名场景的对齐处理**

当 From 域含国际化域名（IDN）时，比较前必须先做形式归一。RFC 8616 第 6 节明确更新了 RFC 7489 第 6.6.1 与 7.1 节的处理方式：**域名中的 U-label 一律先转换为 A-label，再进行后续处理**。

**实现提示：**自研对齐比较逻辑时，若一侧是 U-label、另一侧是 A-label，字符串直比必然不等，会造成「看起来该对齐却判失败」。归一化必须放在比较之前。

**排障清单：三步定位对齐失败**

1. **取三个域。**从 `Authentication-Results` 与原始头中分别取出 From 域、DKIM 的 `d=`、SPF 校验所用的 MAIL FROM 域。
2. **逐机制判定。**先看该机制本身是否 pass；再按 r/s 规则判断是否与 From 域对齐。两者都成立才算这一侧过关。
3. **定位缺口。**典型结论有三类：通道改写了信封发件人（补 DKIM 对齐签名）、签名域用了平台域（改用自有域签名）、误开了严格模式（回退为宽松）。

参考：[RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.txt)、[RFC 8616 Email Authentication for Internationalized Mail](https://www.rfc-editor.org/rfc/rfc8616.txt)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/auth-dmarc-identifier-alignment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
