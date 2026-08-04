---
title: "附件文件名的 MIME 参数写法为什么会造成网关与客户端判断不一致？"
source: "https://ztpop.net/kb/mime-filename-parser-differential-evasion.html"
license: CC-BY 4.0
---

# 附件文件名的 MIME 参数写法为什么会造成网关与客户端判断不一致？

1
附件文件名的 MIME 参数写法为什么会造成网关与客户端判断不一致？
▼

**文件名在 MIME 里的多种表达方式**

附件文件名主要由 RFC 2183 定义的 Content-Disposition 字段中的 `filename` 参数承载（Content-Type 中的 `name` 参数是另一种历史写法）。问题的根源在于：**MIME 参数值原本只能是受限的 ASCII，无法表达非英文文件名，也无法承载很长的值。**

RFC 2231（1997 年 11 月）为此引入了两项扩展，它更新了 RFC 2045、RFC 2047 与 RFC 2183：

* **参数续行（continuation）**：把一个长参数值拆成带序号的多段，形如 `filename*0=`、`filename*1=`、`filename*2=`，由接收方按序号拼接还原。
* **字符集与语言标记的扩展参数**：参数名后加星号，值以「字符集'语言'百分号编码内容」的形式给出，从而表达非 ASCII 字符。

两者还可组合，形成既分段又带编码的写法。于是同一个附件的文件名，在报文中可能以**三四种不同形式并存**——这正是解析分歧的土壤。

**解析分歧是怎么产生的**

当一个 MIME 分部中同时出现多种文件名表示时，规范并未覆盖所有畸形组合的处理方式，不同实现只能各自决定。常见的分歧点：

* **同时存在 `filename` 与 `filename*`**：按扩展参数的设计意图应优先取带星号的形式，但仍有实现取前者，或取先出现者。
* **同一参数重复出现**：取第一个还是最后一个，实现之间不一致。
* **续行序号缺失或乱序**：如只有 `*0` 与 `*2`，有的实现拼接可用段，有的整体放弃并回退到别处取值。
* **Content-Type 的 `name` 与 Content-Disposition 的 `filename` 冲突**：两处给出不同名字时优先级不一致。
* **编码与转义处理差异**：百分号编码、引号、反斜杠转义、折行（folding）与空白的处理细节不同。
* **字符集声明与实际内容不符**：解码结果因实现而异。

**攻击者利用的正是这种不一致：精心构造一封邮件，使邮件网关解析出 `report.txt`（无害、放行），而收件人客户端解析出 `report.exe`（可执行）。**网关与客户端都「按自己的规则正确工作」，但组合起来形成了绕过。这类问题不是某一方的漏洞，而是**解析分歧（parser differential）**——因此单独修补任何一方都不能根除。

**与之叠加的伪装手法**

解析分歧常与以下手法叠加使用，进一步降低用户的辨识能力：

* **双扩展名**：`invoice.pdf.exe`。在隐藏已知扩展名的默认设置下，用户只看到 `invoice.pdf`。
* **从右至左覆盖字符**：在文件名中插入 U+202E（RIGHT-TO-LEFT OVERRIDE），使其后的字符倒序渲染，从而把可执行扩展名在视觉上伪装成文档扩展名。
* **超长文件名**：用大量空格或无意义字符把真实扩展名推出显示区域之外。
* **不可见与同形字符**：插入零宽字符，或用视觉相近的 Unicode 字符替换扩展名中的字母。
* **声明类型与真实类型不符**：Content-Type 声明为 `text/plain`，实际内容是可执行文件或脚本。RFC 2045、RFC 2046 定义了媒体类型体系，但**声明值完全由发送方控制，不具备任何证明力。**
* **信头编码字（encoded-word）滥用**：RFC 2047 定义的编码字用于信头中的非 ASCII 文本，若被用在本不该出现的位置，同样会造成显示与解析不一致。

**检测侧应当怎么做**

1. **以内容而非声明为准判定类型**：这是最重要的一条。用文件魔数（magic bytes）判定真实格式，与 Content-Type 声明、各处文件名的扩展名做**三方比对**，任何不一致都应显著提升风险分值。
2. **穷举所有可能的文件名解释**：不要只取一个「正确」的文件名，而应把 `filename`、`filename*`、续行拼接结果、Content-Type 的 `name` 等**全部候选值都提取出来**，只要其中*任意一个*命中高危扩展名策略，就按高危处理。**这是应对解析分歧最有效的工程手段——用「取并集」代替「猜对方怎么解析」。**
3. **把畸形结构本身当作信号**：重复参数、续行序号缺失或乱序、同一附件多个互相冲突的文件名——这些在正常邮件中极为罕见，其出现本身就值得告警，而不只是需要「兼容处理」的边缘情况。
4. **规范化后再匹配**：解码百分号编码、统一 Unicode 规范化形式、移除双向控制字符与零宽字符、去除首尾空白，然后再与策略规则比对。**在未规范化的原始串上做正则匹配，是规避得以成功的常见原因。**
5. **检查双向控制字符**：文件名中出现 U+202E 等双向覆盖字符，在正常业务中几乎没有合理用途，应直接判为可疑。
6. **递归解包容器**：压缩包、磁盘镜像、嵌套 message/rfc822 内部的附件，需要用同一套规则再走一遍，不能只检查最外层。
7. **解析失败要「按危险处理」**：当解析器无法确定文件名或类型时，默认动作应是隔离或阻断，而不是放行。**「解析不出来所以放过去」是设计缺陷，不是容错。**

**投递与显示侧的配套措施**

* **在客户端强制显示扩展名**：通过终端策略统一开启已知扩展名显示，消除双扩展名伪装的基础。
* **对可疑附件重写文件名**：网关可将附件重命名为规范化后的安全形式（如去除控制字符、统一为单一扩展名），并在正文中说明。这样客户端与网关看到的就是同一个名字，**从根上消除分歧**。
* **按类型而非按名字设策略**：阻断规则应基于检测到的真实类型，而不是基于文件名字符串匹配。名字可被无限变形，类型不能。
* **限制高危类型的直接投递**：对可执行文件、脚本、快捷方式、磁盘镜像等，采用隔离后按需释放的流程，而非依赖用户判断。
* **保留原始报文**：出于取证与复核需要，隔离时应保存未经改写的原始 RFC 5322 报文，改写只作用于投递副本。

参考：RFC 2231《MIME Parameter Value and Encoded Word Extensions: Character Sets, Languages, and Continuations》，N. Freed、K. Moore，1997 年 11 月（取代 RFC 2184，更新 RFC 2045、RFC 2047、RFC 2183），DOI 10.17487/RFC2231，https://www.rfc-editor.org/rfc/rfc2231.html ；RFC 2183《Communicating Presentation Information in Internet Messages: The Content-Disposition Header Field》，R. Troost、S. Dorner、K. Moore 编，1997 年 8 月，https://www.rfc-editor.org/rfc/rfc2183.html ；RFC 2045《Multipurpose Internet Mail Extensions (MIME) Part One: Format of Internet Message Bodies》，N. Freed、N. Borenstein，1996 年 11 月，https://www.rfc-editor.org/rfc/rfc2045.html ；RFC 2046《Multipurpose Internet Mail Extensions (MIME) Part Two: Media Types》，1996 年 11 月，https://www.rfc-editor.org/rfc/rfc2046.html ；RFC 2047《MIME (Multipurpose Internet Mail Extensions) Part Three: Message Header Extensions for Non-ASCII Text》，K. Moore，1996 年 11 月，https://www.rfc-editor.org/rfc/rfc2047.html ；RFC 5322《Internet Message Format》，2008 年 10 月，https://www.rfc-editor.org/rfc/rfc5322.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mime-filename-parser-differential-evasion.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
