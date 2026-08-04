---
title: "如何用可复现的算法判定邮件里的域名是否为同形异义仿冒？"
source: "https://ztpop.net/kb/unicode-uts39-confusable-domain-skeleton-detection.html"
license: CC-BY 4.0
---

# 如何用可复现的算法判定邮件里的域名是否为同形异义仿冒？

1
如何用可复现的算法判定邮件里的域名是否为同形异义仿冒？
▼

**为什么「肉眼比对」不是一种检测方法**

仿冒域名依赖的是**渲染结果相同或极为接近，而码点不同**。收件人看到的字形与真实域名一致，字符串本身却是另一个域。这类判定如果交给人工目视，既不可复现，也无法规模化——同一个域名在不同字体、不同字号、不同终端下的可辨识度差异极大。

要把它变成工程问题，需要一个**确定性的归一化函数**：给定任意字符串，输出一个「视觉骨架」，凡是看起来相同的字符串都映射到同一个骨架。Unicode 联盟在技术标准 UTS #39《Unicode Security Mechanisms》中给出了这样的函数。该文档当前版本为 17.0.0（2025-09-04）。

**UTS #39 的 skeleton 算法**

UTS #39 第 4 节 Confusable Detection 定义了混淆检测机制，其数据文件提供从源字符到**原型（prototype）**的映射：每个视觉符号类有一个示例字符（exemplar character），可混淆的字符被映射到同一个示例字符。

核心函数 `internalSkeleton(X)` 的步骤为：将 X 转换为 NFD 规范分解形式；移除具有 `Default_Ignorable_Code_Point` 属性的字符；按数据文件把每个字符替换为其原型并拼接，得到示例字符串；再次应用 NFD。

在此之上，`bidiSkeleton(d, X)` 先按 Unicode 双向算法以方向 d（RTL / LTR / FS）重排字符、把组合标记移到基字符之后、把镜像字符替换为其镜像字形，然后再取 `internalSkeleton`。为兼容早期定义，`skeleton(X) = bidiSkeleton(LTR, X)`。

**判定规则**：若 `skeleton(X) = skeleton(Y)`，则 X 与 Y 互为 confusable。该映射是幂等的（对骨架再取骨架结果不变），混淆关系具有传递性。这两条性质使得**可以为受保护域名预先计算骨架并建索引**，检测时只需对待判域名取一次骨架再做等值查表，复杂度是常数级的，适合放在邮件网关的同步处理路径上。

**三类混淆及其不同处置**

UTS #39 把混淆分为三类，对应不同的告警强度：

* **single-script confusables（同脚本混淆）**：两串可混淆且其解析脚本集有交集。例如同为拉丁字母内部的字形相近字符。这类在纯 ASCII 域名中也会发生，是最常被低估的一类。
* **mixed-script confusables（混合脚本混淆）**：两串可混淆但解析脚本集无交集。典型是用非拉丁脚本中的字符替换拉丁字母。
* **whole-script confusables（整串脚本混淆）**：属于混合脚本混淆，且两串各自都是单脚本字符串——即整个标签被完整替换为另一套脚本中形似的字符。UTS #39 第 4.1 节专门讨论这一类。

工程含义：**混合脚本与整串脚本混淆通常可以直接判为高风险**，因为正常业务域名极少在单个标签内混用互不相关的脚本；而同脚本混淆需要结合业务上下文与其他信号，否则误报率会失控。

**落到邮件：与 Punycode、IDNA2008 的衔接**

域名系统本身不直接承载 Unicode。RFC 3492 定义的 **Punycode** 是一种 Bootstring 编码，把 Unicode 标签编码为受限的 ASCII 字符集，编码后的标签带 `xn--` 前缀；RFC 5890 给出 IDNA 的定义与文档框架，RFC 5891 给出 IDNA 协议本身，规定了域名标签在 Unicode 与 ASCII 兼容编码之间转换的规则。

因此邮件侧的检测流水线应当是：

1. **提取**：从 RFC 5322 规定的 From、Reply-To、Return-Path 等地址字段，以及正文中的链接主机名，取出全部域名。
2. **解码**：把 `xn--` 形式的标签解码回 Unicode 形式。**只看 ASCII 形式会漏掉全部 IDN 仿冒，只看 Unicode 形式则无法与注册数据比对，两种形式都要保留。**
3. **取骨架**：对每个标签计算 skeleton。
4. **比对**：与受保护域名清单的骨架索引做等值匹配；命中即为同形异义候选。
5. **分级**：按同脚本 / 混合脚本 / 整串脚本区分风险，并叠加域名年龄、是否首次出现、是否与已知业务往来域一致等上下文。

**必须写进运维文档的几条限制**

* **骨架不稳定跨版本**：UTS #39 明确指出 bidiSkeleton 的结果不能用于显示，且不保证跨 Unicode 版本稳定。检测系统必须**记录所用的 UTS #39 与 confusables 数据版本**，升级数据时需重算全部索引，否则新旧骨架混存会造成静默漏检。
* **骨架相同不等于恶意**：合法组织也可能注册形近域名用于防御或多语言站点。判定结果是「需人工复核的候选」，不是「确认攻击」，不应直接用于自动删信。
* **不能取代同音/拼写变体检测**：骨架只覆盖*视觉*混淆。增删字符、词序调换、换用不同顶级域这类变体骨架并不相同，需另用编辑距离等方法覆盖。
* **显示层要给用户看真相**：检测之外，客户端与网关在展示可疑域名时应同时呈现其 Punycode 形式，把判断依据交给用户，而不是让用户去分辨字形。
* **把受保护清单当作一等资产维护**：骨架比对的召回完全取决于清单是否覆盖了本组织及主要往来方的域名。清单陈旧是这套方法最常见的失效原因。

参考：Unicode Technical Standard #39《Unicode Security Mechanisms》（UTS #39），Version 17.0.0，2025-09-04，第 4 节 Confusable Detection、4.1 Whole-Script Confusables、4.2 Mixed-Script Confusables，https://www.unicode.org/reports/tr39/ ；RFC 3492《Punycode: A Bootstring encoding of Unicode for Internationalized Domain Names in Applications (IDNA)》，A. Costello，2003 年 3 月，https://www.rfc-editor.org/rfc/rfc3492.html ；RFC 5890《Internationalized Domain Names for Applications (IDNA): Definitions and Document Framework》，J. Klensin，2010 年 8 月，https://www.rfc-editor.org/rfc/rfc5890.html ；RFC 5891《Internationalized Domain Names in Applications (IDNA): Protocol》，J. Klensin，2010 年 8 月，https://www.rfc-editor.org/rfc/rfc5891.html ；RFC 5322《Internet Message Format》，P. Resnick 编，2008 年 10 月，https://www.rfc-editor.org/rfc/rfc5322.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/unicode-uts39-confusable-domain-skeleton-detection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
