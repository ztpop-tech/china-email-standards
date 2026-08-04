---
title: "RFC 2045 定义的 Content-Type 与 Content-Transfer-Encoding 各自解决什么问题？"
source: "https://ztpop.net/kb/rfc2045-mime-content-transfer-encoding.html"
license: CC-BY 4.0
---

# RFC 2045 定义的 Content-Type 与 Content-Transfer-Encoding 各自解决什么问题？

1
RFC 2045 定义的 Content-Type 与 Content-Transfer-Encoding 各自解决什么问题？
▼

**Content-Type 的作用**

Content-Type 字段的目的，是把正文所含数据描述得足够充分，使接收方用户代理能挑选恰当的程序或机制把数据呈现给用户，或以其他恰当方式处理。该字段的值称为「媒体类型」（media type）。它通过给出媒体类型与子类型标识符，并为某些媒体类型提供必要的辅助信息，来指明实体正文中数据的性质；类型与子类型名之后的其余部分，只是一组以 `属性=值` 记法书写的参数，参数的先后次序不具意义。

一般而言，顶级媒体类型声明数据的大类，子类型指明该类数据的具体格式。例如仅凭 `image/xyz` 这一媒体类型，用户代理就足以判定这是一幅图像，哪怕它并不认识 `xyz` 这一具体图像格式——这类信息可用于决定是否把无法识别的子类型的原始数据直接展示给用户（对 text 的未知子类型这么做尚属合理，对 image 或 audio 则不然）。正因如此，text、image、audio、video 的已注册子类型不应内嵌实为其他类型的信息；这类复合格式应当用 multipart 或 application 类型来表达。

**参数的语义与容错**

参数是媒体子类型的修饰符，本身不从根本上改变内容的性质。有意义的参数集取决于具体的类型与子类型：多数参数只与某一个特定子类型相关联，但某个顶级媒体类型也可以定义适用于其所有子类型的参数。参数可能由定义它的内容类型或子类型规定为必需，也可能是可选的。一条重要的容错规则是：MIME 实现**必须忽略**它不认识的参数名。这条规则是 MIME 得以向前扩展而不破坏既有实现的基础。

**Content-Transfer-Encoding 的五种机制**

许多可通过邮件传输的媒体类型，其「天然」格式是 8 位字符或二进制数据，而这类数据无法在某些传输协议上传送——例如 RFC 821（SMTP）把邮件限制为 7 位 US-ASCII，且每行含结尾 CRLF 在内不超过 1000 字符。因此需要一种标准机制，把这类数据编码为 7 位短行格式；同时，对那些将直接在限制较少的传输通道上使用的、未编码的宽松格式材料，也需要恰当标注。RFC 2045 为此定义了 `Content-Transfer-Encoding` 头字段。

该字段的值是单个 token，形式定义为：

```
encoding  := "Content-Transfer-Encoding" ":" mechanism
mechanism := "7bit" / "8bit" / "binary" /
             "quoted-printable" / "base64" /
             ietf-token / x-token
```

这些取值**不区分大小写**——Base64、BASE64、bAsE64 完全等价。`7BIT` 编码类型要求正文本身已是 7 位、可直接投递邮件的表示形式；它同时是**默认值**，即当 Content-Transfer-Encoding 头字段缺失时，按 `Content-Transfer-Encoding: 7BIT` 处理。

**运维与安全含义**

理解这两个字段的分工，对邮件网关排障与内容检测都很关键：Content-Type 决定「这是什么」，Content-Transfer-Encoding 决定「它被怎样包装以便过管道」。安全设备若只按原始字节做特征匹配，而不先按声明的传输编码解码，就会被 base64 或 quoted-printable 包装的载荷绕过；反过来，若发件端声称 7bit 却夹带 8 位字节，下游遵循 7 位限制的 MTA 可能截断或损坏内容。因此规范化的处理顺序应当是：解析 Content-Type → 按 Content-Transfer-Encoding 解码 → 再做类型判定与内容检查，并对声明与实际不符的情况单独告警。

参考：IETF [RFC 2045《Multipurpose Internet Mail Extensions (MIME) Part One: Format of Internet Message Bodies》](https://www.rfc-editor.org/rfc/rfc2045.txt)（Standards Track，1996-11）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc2045-mime-content-transfer-encoding.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
