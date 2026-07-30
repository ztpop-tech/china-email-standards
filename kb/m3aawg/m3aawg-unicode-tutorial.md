---
title: "M3AAWG Unicode 滥用教程：同形字符攻击与防御"
source: "https://ztpop.net/kb/m3aawg-unicode-tutorial.html"
license: CC-BY 4.0
---

# M3AAWG Unicode 滥用教程：同形字符攻击与防御

翻译自 M3AAWG Unicode Abuse Overview and Tutorial (Feb 2016)

Unicode 字符集包含超过 100,000 个字符，其中大量字符在视觉上完全相同（homoglyph，同形字）。M3AAWG 的 Unicode 滥用教程详细阐述了 Unicode 字符被用于网络钓鱼和身份冒充的工作原理，以及与现有反滥用措施（M3AAWG Unicode 滥用预防最佳实践）的协作方式。

## Unicode 滥用的根本原因

国际化域名（IDN）、国际化顶级域（IDN TLD）和国际化邮件地址（EAI）允许在域名和邮件地址中使用非 ASCII 字符。全球 70% 的互联网用户使用非 ASCII 字符语言，这意味着"http://שלןמ.com"或"jérome@example.fr"等地址的需求正快速增长。但随着这些字符被系统广泛支持，滥用风险也随之上升。

### 同形字攻击的本质

问题是滥用者利用庞大的 Unicode 字符集构造视觉上令人混淆的序列。例如：

* 用户看到 **https://Ьank.com/**，可能完全忽略 "bank" 的第一个字符并非拉丁字母 'b'，而是西里尔大写字母"软符号"（Ь, U+042C）
* 更隐蔽的是希腊小写字母 omicron（ο, U+03BF）和西里尔大写字母 ve（В, U+0412）在大多数计算机字体中与拉丁字母 'o' 和 'B' 像素级完全一致
* 零宽度空格（U+200B）在邮件正文中不可见，但可绕过基于关键字匹配的反钓鱼过滤

## 攻击面分析

### 邮件领域

* **发件人显示名欺骗**：使用同形字符构造与合法域完全相同的假冒域（如 microsоft.com 中的 'о' 为西里尔字母）
* **域级别欺骗**：在 DKIM 签名的域中使用 Unicode 同形字，使 DNS 查询指向完全不同的域
* **邮件正文中的 URL 隐藏**：使用零宽度字符将恶意链接分割，避免被反垃圾引擎检测

### Web 领域

* 同形域名注册（注册视觉上相同的域名用于钓鱼）
* 邮件中的链接伪装（显示的链接文本指向合法站点，实际 href 指向同形域名）

## M3AAWG 推荐的防御策略

1. **实施 Unicode 归一化（Normalization）**：使用 NFC 或 NFKC 归一化将用户输入的 Unicode 序列转换为标准形式，减少同形字的识别难度
2. **部署 IDN 同形检测**：邮件网关检查域名中的混合脚本（如 Latin + Cyrillic 混合），在发件人域和链接域中标记跨脚本内容
3. **BCD（Basic Confusable Detection）**：实施基本混淆字符检测，识别邮件头部中的同形字符组合
4. **SIDN（Slot-Based Internationalized Domain Names）**：限制域名中不同 Unicode 脚本的组合方式，防止 Latin 脚本和 Cyrillic 脚本混合使用在同一标签中
5. **Unicode 一致性检查**：在 DKIM 签名的域经过 DNS 查询前执行 Unicode 归一化一致性验证

## 与传统邮件认证的交互

DMARC 的域一致性验证需要特别注意 Unicode 处理。DMARC 比较的 header.From 域如果包含同形字符，与 SPF/DKIM 的域可能不同。M3AAWG 建议在 DMARC 验证前对域执行以下处理：

* 使用 IDNA（Internationalized Domain Names in Applications）将国际化域名转换为 ASCII Compatible Encoding (ACE) 后再执行 SPF/DKIM/DMARC 验证
* DNS 查询使用 ACE 格式，避免混淆的同形字符导致查询到错误的记录

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-unicode-tutorial.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
