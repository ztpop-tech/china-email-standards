---
title: "M3AAWG Unicode 滥用防御最佳实践"
source: "https://ztpop.net/kb/m3aawg-unicode-abuse-prevention.html"
license: CC-BY 4.0
---

# M3AAWG Unicode 滥用防御最佳实践

## 一、执行摘要

Unicode 标准极大增强了互联网的国际化能力，使得全球用户可以使用本地语言文字访问互联网服务。然而，这份包容性也被滥用于钓鱼攻击与社会工程——攻击者利用视觉上难以区分的 Unicode 字符（即"同形字"）来伪造合法的域名与邮箱地址。

例如，希腊字母 ο（omicron，U+03BF）与拉丁字母 o（U+006F）在绝大多数屏幕字体下几乎无法区分；西里尔字母 а（U+0430）与拉丁字母 a（U+0061）同样如此。攻击者可注册含这些视觉混淆字符的域名（如将 `paypal.com` 中的字母替换为同形字符），并使用该域名发送看似来自官方的钓鱼邮件。

本文档由 M3AAWG（Messaging, Malware and Mobile Anti-Abuse Working Group）于 2016 年 2 月发布，为邮件运营商、客户端开发者和域名注册商提供 Unicode 滥用防御的最佳实践建议。核心推荐策略包括：对入站及出站邮件中的邮箱地址与域名实施 Unicode 限制性检查（Restriction Level Detection），以及对邮件内嵌 URL/链接进行主动检测。

## 二、背景

### 2.1 国际化域名与国际化邮箱地址

国际化域名（Internationalized Domain Name, IDN）允许在域名中使用 Unicode 字符（非 ASCII），通过 Punycode 编码（RFC 3492）在 DNS 层面传输。国际化邮箱地址（Email Address Internationalization, EAI, RFC 5335 及后续标准）则允许邮箱本地部分也使用 Unicode 字符。

这两项技术的普及带来了新的安全挑战：同形字符（Homoglyph）可被用于构造视觉上几乎与合法地址完全一致的钓鱼地址。

### 2.2 Unicode TR39 — Unified Security Model for Identifiers

Unicode 技术标准 #39（UTS #39）定义了 Unicode 标识符统一安全模型，其中包括一组"限制级别"（Restriction Levels），用于评估一个 Unicode 字符串的混用风险：

* **ASC（ASCII）**：仅含 ASCII 字符，无安全风险。
* **Highly Restrictive（高度限制）**：仅使用单一脚本（Script）的字符，且符合该脚本的使用规则。
* **Moderately Restrictive（中度限制）**：允许混合使用多个脚本，但仅允许拉丁字母与另一脚本的混合等有限的组合。
* **Minimally Restrictive（最低限制）**：允许混合多个脚本，但排除某些高风险组合。
* **Unrestricted（无限制）**：无任何限制。

UTR #36（Unicode Security Considerations）和 UTS #39 共同构成了本文所依赖的安全理论基础。

### 2.3 三种检查实体

在邮件系统的上下文中，Unicode 滥用防御需要检查三类实体：

1. **邮箱本地部分**（Local Part）—— `@` 前面的部分
2. **邮箱域名**（Domain）—— `@` 后面的部分
3. **URL 中的域名**—— 邮件正文内嵌链接的域名

每一类实体均需独立的检查策略，因为其允许的字符集和上下文约束各不相同。

## 三、邮件最佳实践

### 3.1 收信检查

邮件接收方（MTA / MDA / 邮件安全网关）应在处理入站邮件时，对以下邮件头字段中的邮箱地址执行 Unicode 滥用检查：

* `MAIL FROM`（SMTP 信封发件人）
* `From`（邮件头发件人）
* `Sender`（邮件头发件人代理）
* `Reply-To`（回复地址）

当在上述字段中检测到可疑的 Unicode 字符使用模式时，接收方可选择：拒收邮件、标记为垃圾/钓鱼、或触发额外验证。

### 3.2 发信检查

邮件发送方同样应在出站邮件上执行 Unicode 检查，特别是对以下字段：

* `To`（收件人）
* `Cc`（抄送）
* `Bcc`（密送）

发信端应当检测发送者自身域名中是否存在疑似的 Unicode 滥用，以避免合法域名被仿冒。

### 3.3 检查项与建议决策对照表

M3AAWG 定义了下述 5 类检查项及其对应的建议处理决策：

| 检查条件 | 描述 | 建议决策 |
| --- | --- | --- |
| **1. 禁用码点扫描** （Disallowed Codepoint Scan） | 检查字符串中是否包含 UTS #39 定义的"禁用码点"（例如控制字符、私用区字符、非字符等）。 | 若检测到禁用码点，**直接拒收/拒绝**（reject）。这些字符不应出现在合法邮件地址或域名中。 |
| **2. Highly Restrictive 级别检测** （Highly Restrictive Check） | 将整个字符串的 Unicode 限制级别要求设定为 **Highly Restrictive**，即仅允许单一脚本内的字符。对于邮箱（含域名），这是推荐的严格级别。 | 若字符串未通过 Highly Restrictive 检测，根据业务策略**标记为可疑**（flag）或**拒收**（reject）。对来自可信域的邮件可适当放宽。 |
| **3. 混合数字检测** （Mixed Number Detection） | 检测字符串中是否混合使用了不同脚本的数字/数字形状。例如拉丁数字 `123` 与其他计数系统数字的混合。 | 若发现混合数字，**标记为可疑**（flag）。这种情况极为罕见，几乎总意味着人为构造的欺骗。 |
| **4. 多重非间距组合标记检测** （Multiple Non-Spacing Marks） | 检测字符串中是否存在多个连续的非间距组合标记（combining diacritical marks），这可能被用于构造视觉上与合法字符串相似的伪装。 | 若发现多重非间距组合标记，**标记为可疑**（flag）。合法的邮箱地址极少同时使用两个以上的组合标记。 |
| **5. 混合脚本检测** （Mixed Script Detection） | 检测是否在不同位置混合使用了不同脚本的字符（例如域名的拉丁字母标签中出现西里尔字符），使用 UTS #39 的脚本混合检测机制。 | 根据混合的脚本组合判定风险等级。常见的"高信任"脚本组合（如拉丁 + 中文）可接受；"低信任"组合（如拉丁 + 西里尔/希腊）应**标记或拒收**。 |

### 3.4 域名 Punycode 与显示策略

对于 IDN 域名，邮件客户端应当在 UI 层面采取以下策略：

* 默认显示 IDN 的 Punycode 表示（ASCII Compatible Encoding，以 `xn--` 开头），仅在确定域名安全后以 Unicode 形式显示。
* 对混合脚本的域名始终优先显示 Punycode 形式，除非用户已显式信任该域名。
* 提供可配置的 IDN 显示策略供用户选择：始终显示 Unicode / 始终显示 Punycode / 智能决定。

## 四、邮件外使用最佳实践

### 4.1 URL 与链接中的域名

邮件正文中的 URL（超链接）是 Unicode 钓鱼攻击的重要载体。攻击者可能：

* 使用 IDN 注册一个同形域名，并在邮件正文中构造看似来自合法服务的超链接。
* 在 URL 中使用 Unicode 字符构成路径或查询参数，利用视觉混淆使链接看起来指向合法网站。

建议实践：

* 邮件客户端应在渲染链接时，对其中包含的 IDN 域名执行与邮箱地址相同的 Unicode 安全检查。
* 展示链接时，优先显示 DNS 层面的真实域名（对 IDN 显示 Punycode）。
* 对于非 ASCII 域名，在浏览器/邮件客户端的状态栏或链接预览区域显示 Punycode 编码及 Unicode 解码两种形式供用户对比。
* 对包含混合脚本或疑似同形字符的 URL 添加视觉警告标识。

### 4.2 文档名与标签名

除邮件域外，Unicode 同形滥用还出现在：

* **附件文件名**：使用同形字符构造与已知安全文件相似的名称（如 `invoice.pdf` 中的部分字符被替换为同形字）。
* **发件人显示名**：`From`/`Sender` 头中的显示名称（Display Name）可以使用任意 Unicode 字符——攻击者可在此字段设置完全等同于合法品牌的名称。
* **MIME 标签与内容类型**：在非标准化的自定义头字段中使用可疑 Unicode。

建议对上述所有字段实施与邮箱地址一致的 Unicode 安全检查。

## 五、结论

同形字符欺诈（Homoglyph Spoofing）是 Unicode 普及化过程中不可忽视的安全威胁。M3AAWG 建议行业参与者——包括邮件服务提供商、域名注册商、浏览器厂商和邮件客户端开发者——协同采取以下措施：

* **标准化检测框架**：统一采用 UTS #39 定义的 Restriction Level 评估体系作为行业基准。
* **多层次防御**：在收信、发信、链接展示三个层面分别实施检查。
* **用户可感知的安全提示**：对可疑 Unicode 内容给予清晰的视觉警告，而非静默接受。
* **持续更新**：Unicode 标准持续演进，防御措施也应随之更新。

通过全行业的协同努力，我们可以在享受国际化互联网便利的同时，有效遏制基于 Unicode 同形字符的社会工程攻击。

## 六、参考文献

1. Unicode Technical Standard #39: Unicode Security Mechanisms (UTS #39). <https://www.unicode.org/reports/tr39/>
2. Unicode Technical Report #36: Unicode Security Considerations (UTR #36). <https://www.unicode.org/reports/tr36/>
3. RFC 5322: Internet Message Format. <https://tools.ietf.org/html/rfc5322>
4. RFC 5321: Simple Mail Transfer Protocol. <https://tools.ietf.org/html/rfc5321>
5. RFC 3492: Punycode: A Bootstring encoding of Unicode for Internationalized Domain Names in Applications (IDNA). <https://tools.ietf.org/html/rfc3492>
6. RFC 5891: Internationalized Domain Names in Applications (IDNA): Protocol. <https://tools.ietf.org/html/rfc5891>
7. RFC 5335: Internationalized Email Headers. <https://tools.ietf.org/html/rfc5335>
8. M3AAWG Best Practices for Unicode Abuse Prevention, February 2016. Messaging, Malware and Mobile Anti-Abuse Working Group (M3AAWG).

## 七、国内场景补充

### 7.1 中文环境中的 Unicode 风险

中文互联网用户面临以下几类特有的 Unicode 混淆风险：

* **拉丁 / 西里尔 / 希腊字母同形**：与全球相同的传统风险。例如西里尔小写字母 `а`（U+0430）与中文环境中随处可见的拉丁字母 `a` 几乎无法区分。
* **"rna" 与 "ma" 等拼音混淆**：当拼音文字中出现拉丁字母 `rn` 组合时，在某些字体下 `rn` 可能被误认为 `m`（即所谓的 "r n" → "m" 混淆）。攻击者可利用此特性构造域名或邮箱地址中的视觉等价替换。
* **拼音 / 汉字的混合域名**：中文 IDN 支持中文字符在域名中的直接使用，但也引入了汉字混用的可能性——例如使用字形接近的异体字替代标准汉字。
* **全角 / 半角字符混淆**：Unicode 中全角拉丁字母（如全角 A，U+FF21）与普通的半角 A（U+0041）外观一致但码点不同，在部分解析器中可能导致不同的解析结果。

### 7.2 国内邮件厂商的实践

腾讯企业邮、阿里企业邮等国内主流邮件服务商在 IDN/Unicode 安全方面已实施一系列措施：

* **腾讯企业邮**：对发信人域名进行 Punycode 解码后的同形检测，对混合脚本域名在客户端展示时附加安全提示。收信策略中默认对 IDN 域名执行 UTS #39 的 Restriction Level 检查，对高度可疑的邮件直接拒收或进入垃圾箱。
* **阿里企业邮**：结合钓鱼威胁情报库，对疑似同形域名的发件地址实施额外的 DKIM/SPF/DMARC 验证。在其邮箱客户端中，发件人地址若包含非 ASCII 字符则在读取窗中显示 Punycode 原始编码。
* **网易企业邮**：部署了多重字符集的兼容性检测机制，对邮件头中的非标准 Unicode 编码进行归类检查并标记。

### 7.3 对国内邮件系统运营者的建议

结合 M3AAWG 框架与国内实际环境，建议国内邮件系统运营者：

* **部署 IDN 同形检测模块**：在 MTA（Postfix、Exim、定制系统等）层面集成 UTS #39 检测逻辑，对入站邮件的发件地址和域名实施检查。
* **增强中文语境词表**：建立针对中文品牌名、金融机构名、政府网站等的高频钓鱼目标词表，对这些词的同形变形实施特别严格的检查。
* **邮件客户端改进**：在网页邮件和移动邮件客户端中，对 IDN 域名默认显示 Punycode 编码，并在用户点击链接前展示实际指向的域名。
* **结合多因素认证**：对标记为"高度可疑"的邮件中的链接，给用户弹窗提示确认后再放行。
* **日志与审计**：记录所有触发 Unicode 安全检查的邮件信息，便于事后追溯与威胁建模。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-unicode-abuse-prevention.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
