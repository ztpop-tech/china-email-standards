---
title: "RFC 2047 的 encoded-word 语法与使用限制有哪些？"
source: "https://ztpop.net/kb/rfc2047-encoded-word-header-rules.html"
license: CC-BY 4.0
---

# RFC 2047 的 encoded-word 语法与使用限制有哪些？

1
RFC 2047 的 encoded-word 语法与使用限制有哪些？
▼

**encoded-word 语法**

encoded-word 由如下 ABNF 文法定义（沿用 RFC 822 记法，但各组成部分之间**不得**出现空白字符）：

```
encoded-word = "=?" charset "?" encoding "?" encoded-text "?="
charset      = token
encoding     = token
token        = 1*<除 SPACE、CTL 与 especials 外的任意 CHAR>
especials    = "(" / ")" / "<" / ">" / "@" / "," / ";" / ":"
               / <"> / "/" / "[" / "]" / "?" / "." / "="
encoded-text = 1*<除 "?" 与 SPACE 外的任意可打印 ASCII 字符>
```

`encoding` 与 `charset` 名均**不区分大小写**：`ISO-8859-1` 等价于 `iso-8859-1`，编码名 `Q` 写作 `q` 亦可。

**长度限制与折行**

单个 encoded-word 的总长（含 charset、encoding、encoded-text 与各分隔符）**不得超过 75 个字符**。若需编码的文本超出这一长度，可使用多个 encoded-word，彼此以 `CRLF SPACE` 分隔。虽然多行头字段的总长度不受限制，但含有 encoded-word 的头字段每一行限制在 76 个字符以内。

设置这些长度限制有双重目的：便于经由跨网邮件网关时的互操作；以及限制头字段解析器在判定某个 token 究竟是 encoded-word 还是普通内容之前（即寻找结尾 `?=` 分隔符时）所需的前瞻量。

**空白禁令（最常见的实现错误）**

规范以 IMPORTANT 强调：encoded-word 被设计为可被 RFC 822 解析器识别为一个 atom，因此其内部**禁止**出现未编码的空白字符（如 SPACE 与 HTAB）。例如字符序列 `=?iso-8859-1?q?this is some text?=` 会被 RFC 822 解析器解析为四个 atom，而不是一个 atom 或一个 encoded-word。正确写法是把空格本身也编码：

```
=?iso-8859-1?q?this=20is=20some=20text?=
```

**允许与禁止出现的位置**

encoded-word 只能出现在三类位置：(1) 替代 Subject、Comments、任意扩展信头字段，或任意字段体定义为 `*text` 的 MIME 正文部分字段中的 text token，也可出现在任何用户自定义（X- 开头）的信头字段中；普通 ASCII 文本与 encoded-word 可同处一个字段，但字段体定义为 `*text` 时，相邻的 encoded-word 之间、以及与相邻 text 之间必须以线性空白分隔。(2) 出现在由 `(` 与 `)` 界定的 comment 内部，即任何允许 ctext 的位置；出现在 comment 中的 Q 编码 encoded-word 不得含有 `(`、`)` 等字符，且必须与相邻内容以线性空白分隔。(3) 作为 phrase 内某个 word 的替代，例如 From、To、Cc 中地址前的显示名；此时 Q 编码可用的字符集被进一步收窄为大小写 ASCII 字母、十进制数字，以及 `!`、`*`、`+`、`-`、`/`、`=`、`_`。

以上是**仅有**的合法位置。规范明确列出禁止项：encoded-word **不得**出现在 addr-spec 的任何部分；**不得**出现在 quoted-string 内部；**不得**用于 Received 头字段；**不得**用于 MIME 的 Content-Type 或 Content-Disposition 字段的参数中（这一场景应改用 RFC 2231 的机制）。这些禁令在安全上意义重大——把 encoded-word 塞进地址或引号字符串，正是显示名欺骗与解析器分歧（parser differential）类攻击的常见土壤。

参考：IETF [RFC 2047《MIME Part Three: Message Header Extensions for Non-ASCII Text》](https://www.rfc-editor.org/rfc/rfc2047.txt)（Standards Track，1996-11）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc2047-encoded-word-header-rules.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
