---
title: "RFC 2231 如何解决 MIME 参数过长与非 ASCII 文件名问题？"
source: "https://ztpop.net/kb/rfc2231-mime-parameter-continuation.html"
license: CC-BY 4.0
---

# RFC 2231 如何解决 MIME 参数过长与非 ASCII 文件名问题？

1
RFC 2231 如何解决 MIME 参数过长与非 ASCII 文件名问题？
▼

**要解决的问题**

过长的 MIME 媒体类型参数值或 Content-Disposition 参数值，与信头折行惯例配合得很差。恰当的信头折行依赖于值中存在允许线性空白（LWSP）的位置，而参数值中未必有这样的位置；即使有，做折行的代理也未必掌握该参数值的具体语法，因而无法识别出这些位置。结果是过长的参数值常被错误的折行实现截断或损坏。

因此需要一种把参数值拆成便于折行的小单元的机制，且该机制必须与既有 MIME 处理器兼容，这意味着：(1) 不得改变 MIME 媒体类型行与 disposition 行的语法；(2) 不得依赖参数顺序，因为 MIME 规定参数对顺序不敏感——虽然 MIME 禁止在传输过程中修改信头，但在用户代理层处理时参数仍可能被重排。

**参数值续行机制**

显而易见的解法就是用多个参数承载单一参数值，并用某种可辨识的命名来表明正在这样做。规范采用的正是这一方案：在参数名后加**星号加十进制计数**，表示多个参数共同封装一个参数值。计数从 0 开始、每个后续分段加 1；必须使用十进制数值，且**不允许前导零，也不允许序号出现缺口**。原始参数值通过按序拼接各分段还原。例如：

```
Content-Type: message/external-body; access-type=URL;
 URL*0="ftp://";
 URL*1="cs.utk.edu/pub/moore/bulk-mailer/bulk-mailer.tar"
```

其语义等同于把 URL 写成单个完整值。需要注意：参数值两侧的引号属于值的语法，**不属于**值本身；并且明确允许把加引号与不加引号的续行字段混用。

**字符集与语言信息**

某些参数值需要附带字符集或语言信息，这既需要一个可辨识的参数命名方式来标明该信息存在，也需要值本身有确定的语法，还需要一种轻量编码机制来容纳参数值中的 8 位信息。

规范复用星号作为「存在语言与字符集信息且启用了编码」的指示符，用单引号 `'` 在参数值开头分隔字符集与语言信息，用百分号 `%` 作为编码标志（与 RFC 2047 保持一致）。具体而言：参数名**末尾**的星号表示该参数值开头可能带有字符集与语言信息；单引号用于在参数值字符串中分隔字符集、语言与实际值三部分；百分号用于标记以十六进制编码的字节。例如：

```
Content-Type: application/x-stuff;
 title*=us-ascii'en-us'This%20is%20%2A%2A%2Afun%2A%2A%2A
```

其中字符集与语言两个字段都**可以留空**。两种机制还可组合使用（形如 `name*0*`、`name*1*`），以同时解决超长与非 ASCII 两个问题。

**为何附件文件名要用 RFC 2231 而非 RFC 2047**

RFC 2047 已明确禁止在 Content-Type 或 Content-Disposition 的参数中使用 encoded-word，非 ASCII 附件文件名的合规写法正是 RFC 2231 的 `filename*=`。这一点在安全上尤为要紧：现实中大量客户端对 `filename`（RFC 2047 风格）与 `filename*`（RFC 2231 风格）并存时的取舍策略不一致，攻击者可借此构造「网关看到 .txt、客户端落盘 .exe」的解析器分歧。邮件网关在做附件类型判定时，应当完整实现续行拼接与百分号解码，并对同名参数的两种写法给出不一致告警，而非只取其一。

参考：IETF [RFC 2231《MIME Parameter Value and Encoded Word Extensions: Character Sets, Languages, and Continuations》](https://www.rfc-editor.org/rfc/rfc2231.txt)（Standards Track，1997-11）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc2231-mime-parameter-continuation.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
