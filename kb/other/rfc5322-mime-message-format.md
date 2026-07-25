---
title: "互联网邮件消息格式深度解析 — RFC 5322 与 MIME（RFC 2045-2049） · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/rfc5322-mime-message-format.html"
license: CC-BY 4.0
---

# 互联网邮件消息格式深度解析 — RFC 5322 与 MIME（RFC 2045-2049） · ztpop 邮件技术知识库

互联网邮件消息格式深度解析 — RFC 5322 与 MIME（RFC 2045-2049）

## 1. 消息整体结构

互联网邮件消息（Internet Message）由两部分组成：
**头部（Header）**
和
**正文（Body）**
，两者之间以一个空行（CRLF）分隔。RFC 5322 第 2.1 节定义了这条规则，RFC 2045 在此基础上通过 MIME 头部字段扩展了正文内容的表达能力。

```
从顶层视角看，一条完整的互联网邮件消息的结构如下：

    header-fields  (US-ASCII, 每行以 CRLF 结尾)
    CRLF           (空行, 标记头部结束)
    body           (US-ASCII 或 MIME 编码内容)
```

RFC 5322 限制头部和正文仅使用 US-ASCII 字符（第 2.1 节），这导致了两大扩展需求：

1. **非 ASCII 正文内容**
   — 由 RFC 2045（Content-Transfer-Encoding）和 RFC 2046（Content-Type）解决
2. **非 ASCII 头部字段值**
   （如中文主题行） — 由 RFC 2047 规定的 encoded-word 机制解决

邮件从发送方 MUA 到接收方 MUA 经过多跳 SMTP 中继，每跳 MTA 在消息顶部添加一条
`Received`
头部（RFC 5321 第 4.4 节），形成从下到上的路由追踪链。

## 2. RFC 5322 头部字段规范

### 2.1 起源字段（Originator Fields）

2.1 起源字段（Originator Fields）

| 字段 | RFC 章节 | 说明 |
| --- | --- | --- |
| `From` | RFC 5322 §3.4 | 消息作者，必填且唯一。格式： `display-name` |
| `Sender` | RFC 5322 §3.4 | 实际发送者。仅当发件人与作者不同时有值（如秘书代发） |
| `Reply-To` | RFC 5322 §3.6.2 | 回复地址覆盖。邮件客户端回复时优先使用此地址 |

**语法约束（RFC 5322 §3.4）：**
  
`addr-spec`
= local-part "@" domain。local-part 支持点分隔和
`+`
标签扩展（如
`user+tag@example.com`
），但不强制语义解释。domain 为 DNS 域名或地址字面量（如
`[192.168.1.1]`
）。

### 2.2 目标字段（Destination Fields）

2.2 目标字段（Destination Fields）

| 字段 | RFC 章节 | 说明 |
| --- | --- | --- |
| `To` | RFC 5322 §3.6.3 | 主要收件人 |
| `Cc` | RFC 5322 §3.6.3 | 抄送收件人（Carbon Copy） |
| `Bcc` | RFC 5322 §3.6.3 | 密送。SMTP 传 RCPT TO 但不写入消息头部 |

`Bcc`
在 RFC 5322 中有特殊的"三态"处理：Bcc 收件人收到消息时可看到 Bcc 头部（为自身），但 To/Cc 收件人看不到 Bcc 头部。主流 MTA 在投递时从消息头部剥离 Bcc 行。

### 2.3 标识字段（Identification Fields）

2.3 标识字段（Identification Fields）

| 字段 | RFC 章节 | 说明 |
| --- | --- | --- |
| `Message-ID` | RFC 5322 §3.6.4 | 全球唯一消息标识。格式： |
| `In-Reply-To` | RFC 5322 §3.6.4 | 回复链中的直接父消息 ID |
| `References` | RFC 5322 §3.6.4 | 完整引用链，用于线程重建。每回复一次追加一个 Message-ID |

`Message-ID`
的生成策略因 MUA 而异。典型模式为
。邮件客户端用
`References`
头部重建会话线索视图。

```
# 查看某封邮件的 Message-ID 和引用链
grep -E '^(Message-ID|In-Reply-To|References):' /var/mail/user
```

### 2.4 信息字段（Informational Fields）

2.4 信息字段（Informational Fields）

| 字段 | RFC 章节 | 说明 |
| --- | --- | --- |
| `Subject` | RFC 5322 §3.6.5 | 消息主题。非 ASCII 需用 RFC 2047 encoded-word |
| `Date` | RFC 5322 §3.6.1 | 消息创建时间。格式： `Day, DD Mon YYYY HH:MM:SS ±ZZZZ` |
| `Comments` | RFC 5322 §3.6.5 | 可选注释 |
| `Keywords` | RFC 5322 §3.6.5 | 逗号分隔的关键词短语 |

**Date 格式示例（RFC 5322 §3.3）：**
  
`Sat, 04 Jul 2026 15:30:00 +0800`
  
日期名和月份缩写固定为英文，时区偏移为 ±HHMM。遗留
`Date`
格式（RFC 2822 之前的 2 位数年份）已废弃。

### 2.5 追踪字段（Trace Fields）

```
Received: from mail.example.com (mail.example.com [203.0.113.1])
    by mx.receiver.net (MTA) with ESMTPS id 4QxY7n2K9jzF
    for ; Sat, 4 Jul 2026 15:30:05 +0800 (CST)
```

`Received`
头部（RFC 5321 §4.4）是最可靠的邮件路径审计源 — 它不由发件端构造，由每跳 MTA 独立添加。格式为 "FROM by VIA FOR recipient ; timestamp"。反向读取即得完整投递路径。

```
# 从下往上读取 Received 链，还原投递路径
awk '/^Received:/ {print NR": "$0}' raw_email.eml | tac
```

### 2.6 可选扩展（Resent Fields）

RFC 5322 §3.6.6 定义
`Resent-*`
系列字段（Resent-From、Resent-To、Resent-Date、Resent-Message-ID），用于消息转发时保留原始信息并追加新路由元数据。

## 3. MIME 体系（RFC 2045 – 2049）

MIME（Multipurpose Internet Mail Extensions）由五篇 RFC 构成，将互联网邮件从纯 ASCII 文本扩展为支持多媒体、多字符集、复合结构的消息格式。

3. MIME 体系（RFC 2045 – 2049）

| RFC | 标题 | 核心内容 |
| --- | --- | --- |
| RFC 2045 | Format of Internet Message Bodies | Content-Type / Content-Transfer-Encoding 语法、编码规则 |
| RFC 2046 | Media Types | 顶层媒体类型定义（text/image/audio/video/application/multipart/message） |
| RFC 2047 | Non-ASCII Header Values | encoded-word 机制： `=?charset?encoding?text?=` |
| RFC 2048 | Registration Procedures | 已升版为 RFC 6838（BCP 13） |
| RFC 2049 | Conformance Criteria | MIME 合规性级别、MIME-Version 头部 |

### 3.1 MIME-Version 头部

按 RFC 2049 第 4 节，MIME 消息必须包含：

```
MIME-Version: 1.0
```

该字段声明消息符合 MIME 规范。缺少此行时，符合 RFC 2049 的 UA 应将消息视为纯文本（text/plain; charset=US-ASCII）。
`MIME-Version: 1.0`
是当前唯一的合法值；后续数字（如 1.1）保留但从未标准化。

### 3.2 Content-Type — 媒体类型体系

RFC 2046 定义了 MIME 的媒体类型树（media type tree），RFC 2045 §5 定义了 Content-Type 头部语法：

```
Content-Type: type "/" subtype *(";" parameter)
```

#### 顶层类型一览

3.2 Content-Type — 媒体类型体系

| 顶层类型 | RFC 章节 | 用途 | 典型子类型 |
| --- | --- | --- | --- |
| `text` | RFC 2046 §4.1 | 可读文本 | plain, html, enriched, csv |
| `image` | RFC 2046 §4.2 | 图像 | jpeg, gif, png, svg+xml |
| `audio` | RFC 2046 §4.3 | 音频 | mpeg, ogg, wav |
| `video` | RFC 2046 §4.4 | 视频 | mp4, mpeg, webm |
| `application` | RFC 2046 §4.5 | 应用数据 | octet-stream, pdf, json, pkcs7-signature |
| `multipart` | RFC 2046 §5.1 | 复合消息体 | mixed, alternative, related, signed |
| `message` | RFC 2046 §5.2 | 封装的消息 | rfc822, partial, delivery-status |

#### charset 参数（text 类型）

RFC 2046 §4.1.2 规定
`text/*`
类型的默认 charset 为 US-ASCII。实际邮件中
`charset="utf-8"`
和
`charset="gb2312"`
常见。RFC 6532 进一步扩展 SMTP 和邮件头部为 UTF-8 原生支持。

```
Content-Type: text/plain; charset="utf-8"
Content-Type: text/html; charset="utf-8"
```

#### name / filename 参数

RFC 2046 允许在
`Content-Type`
中指定建议文件名：

```
Content-Type: application/pdf; name="report-2026.pdf"
Content-Disposition: attachment; filename="report-2026.pdf"
```

RFC 2231 定义了
`filename*`
参数，用于在 Content-Disposition 中编码非 ASCII 文件名（如中文）：

```
Content-Disposition: attachment;
    filename*=UTF-8''%E5%B9%B4%E5%BA%A6%E6%8A%A5%E5%91%8A.pdf
```

### 3.3 Content-Transfer-Encoding

RFC 2045 §6 定义了从 8 位数据到 7 位传输编码的转换机制。经典 SMTP 只保障 7 位通道。

3.3 Content-Transfer-Encoding

| 编码 | RFC 章节 | 原理 | 膨胀率 |
| --- | --- | --- | --- |
| `7bit` | RFC 2045 §2.7 | 不编码。行 ≤998 字符，仅 US-ASCII | 1× |
| ```` 8bit RFC 2045 §2.8 | 不编码但允许 8 位字符。SMTP 须支持 8BITMIME 扩展 | 1× || binary | RFC 2045 §2.9 | 任意二进制，无行的概念 | 1× | | quoted-printable | RFC 2045 §6.7 | 可读性优先。非 ASCII 字节编码为 =XX （XX 为大写十六进制）。保留可读 ASCII 不变 | ~1.5–3× | | base64 | RFC 2045 §6.8 | 每 3 字节映射为 4 个可打印字符（A-Za-z0-9+/），≈76 字符一行 | ~1.33× |  ``` # quoted-printable 编码示例 原始:   "café" (c a f 0xE9) 编码:   "caf=E9"  # base64 编码示例 原始:   "Man" (3 字节) 编码:   "TWFu" (4 字符) ```  quoted-printable 编码规则（RFC 2045 §6.7）：   (1) 任何字节（除 33–60 和 62–126 外）编码为 =XX   (2) 行末空白（空格、制表符）必须编码，防止被 MTA 截断   (3) 行长度 ≤76 字符，软换行用 = 结尾表示行连续   (4) 字面量 = 编码为 =3D 3.4 RFC 2047 — 头部编码（encoded-word） RFC 2047 允许在邮件头部字段值中嵌入非 ASCII 字符，使用如下格式：   ``` =?charset?encoding?encoded-text?= ```  3.4 RFC 2047 — 头部编码（encoded-word）  | 组件 | 值示例 | 说明 | | --- | --- | --- | | charset | UTF-8, ISO-2022-JP, GB2312 | 原文字符集 | | encoding | B (Base64) 或 Q (Quoted-Printable) | 编码方式 | | encoded-text | 编码后的字符串 | 不含空格、控制字符 |  ``` # 中文主题行的典型编码 Subject: =?UTF-8?B?5L2g5aW9IOaXtui0ueaWsOmXu+WFrOWPuA==?= ```  ``` # 在 Python 中解码 encoded-word $ python3 -c " import email.header h = '=?UTF-8?B?5L2g5aW9IOaXtui0ueaWsOmXu+WFrOWPuA==?=' decoded = email.header.decode_header(h) result = ''.join(     t[0].decode(t[1] or 'ascii') if isinstance(t[0], bytes) else t[0]     for t in decoded ) print(result) " # 输出: 你好 时讯新闻公告 ```   RFC 2047 encoded-word 不能 出现在以下位置（§5）：unstructured 字段中的 < > @ , ; : \ " / [ ] ? = 等特例符号附近； From 、 To 等结构化字段的 addr-spec 部分。encoded-word 用于 display-name 部分但不用于地址部分。 4. multipart 与 boundary 分隔机制 RFC 2046 §5.1 完整定义了 multipart 媒体类型。消息的正文被 boundary 字符串分隔为多个 body part，每个 part 自成一个小型 MIME 实体（含自己的头部和正文）。 4.1 boundary 参数  ``` Content-Type: multipart/mixed;     boundary="----=_NextPart_000_0001_01DA3B5E.A0C1B0F0" ```   boundary 的值由发送方 MUA 生成，约束（RFC 2046 §5.1.1）：   * 长度 ≤70 字符 * 仅包含 US-ASCII 字母数字和   '()+_,-./:=? * 必须全局唯一 — 不能出现在任何 body part 的内容中   boundary 分隔符在消息体中使用时需加 -- 前缀。最后一个 boundary 后缀 -- 表示 multipart 结束。 4.2 multipart/mixed — 混合内容  ``` MIME-Version: 1.0 Content-Type: multipart/mixed;     boundary="----=_boundary_abc123"  ------=_boundary_abc123 Content-Type: text/plain; charset="utf-8"  这是邮件的纯文本正文。  ------=_boundary_abc123 Content-Type: image/jpeg; name="photo.jpg" Content-Transfer-Encoding: base64 Content-Disposition: attachment; filename="photo.jpg"  /9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAg...（base64 数据）  ------=_boundary_abc123-- ```   在 multipart/mixed 中，body part 按序排列。第一个 part 通常是纯文本正文，后续 part 是附件。主流 MUA 遵循此约定。 4.3 multipart/alternative — 多格式备选 RFC 2046 §5.1.4 规定， multipart/alternative 的各 part 是同一内容的不同表示形式。MUA 显示它能渲染的"最佳"格式（最后一个），通常按从低到高的优先级排列。   ``` Content-Type: multipart/alternative; boundary="alt_boundary"  --alt_boundary Content-Type: text/plain; charset="utf-8"  这是纯文本版。  --alt_boundary Content-Type: text/html; charset="utf-8"  t_boundary-- ```   MUA 对 multipart/alternative 的通常行为：显示最后一个可渲染的 part，忽略前面的低优先级版本。 4.4 嵌套 multipart 实际邮件常嵌套多层级 multipart。最常见的结构是 multipart/mixed 包裹一个 multipart/alternative （正文）和若干 attachment part。   ``` Content-Type: multipart/mixed; boundary="outer"  --outer Content-Type: multipart/alternative; boundary="inner"  --inner Content-Type: text/plain; charset="utf-8" 纯文本正文  --inner Content-Type: text/html; charset="utf-8" HTML 正文  --inner--  --outer Content-Type: application/pdf; name="doc.pdf" Content-Transfer-Encoding: base64  PDF 附件...  --outer-- ```   解析器须递归处理多层级 MIME 树。标准库的 MIME 解析器均支持此特性。 5. 完整原始消息拆解 下面是一条完整的互联网邮件原始消息，逐段拆解每项头部字段和 MIME 结构。   ``` Return-Path:  Delivered-To: recipient@example.net Received: from mx1.example.org (mx1.example.org [198.51.100.10])     by mx2.example.net (MTA) with ESMTPS id abc123     for ;     Sat, 4 Jul 2026 15:30:02 +0800 (CST) Received: from client.example.org (client.example.org [198.51.100.25])     by mx1.example.org (MTA) with ESMTPSA id xyz789     for ;     Sat, 4 Jul 2026 15:30:01 +0800 (CST) DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;     d=example.org; s=2026; h=from:to:subject:date:message-id;     bh=47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=;     b=Kj8f9s2...（DKIM 签名体） Date: Sat, 04 Jul 2026 15:30:00 +0800 From: =?UTF-8?B?5byg5rmW?=  To: =?UTF-8?B?5p2O5YWL?=  Subject: =?UTF-8?B?5YWs5Y+4IOmihOebtOWtpuS5oOaUtuWQkeeKtuaCqQ==?= Message-ID: <20260704153000.a1b2c3d4e5f6@example.org> MIME-Version: 1.0 Content-Type: multipart/mixed;     boundary="----=_Part_42_20260704"  ------=_Part_42_20260704 Content-Type: multipart/alternative;     boundary="----=_Part_42_20260704_alt"  ------=_Part_42_20260704_alt Content-Type: text/plain; charset="utf-8" Content-Transfer-Encoding: quoted-printable  =E6=82=A8=E5=A5=BD=EF=BC=8C  =E9=99=84=E4=BB=B6=E4=B8=BA=E6=9C=AC=E6=AC=A1=E4=BC=9A=E8=AE=AE=E7= =9A=84=E4=BC=9A=E8=AE=AE=E7=BA=AA=E8=A6=81=E3=80=82  ------=_Part_42_20260704_alt Content-Type: text/html; charset="utf-8" Content-Transfer-Encoding: quoted-printable  9=99=84=E4=BB=B6 =E4=B8=BA=E6=9C=AC=E6=AC=A1=E4=BC= =9A=E8=AE=AE=E7=9A=84=E4=BC=9A=E8=AE=AE=E7=BA=AA=E8=A6=81=E3=80=82   ------=_Part_42_20260704_alt--  ------=_Part_42_20260704 Content-Type: application/pdf; name="=?UTF-8?B?5Lya6K6u57qq6KaB?= =?UTF-8?B?LnBkZg==?=" Content-Transfer-Encoding: base64 Content-Disposition: attachment;     filename="=?UTF-8?B?5Lya6K6u57qq6KaB?= =?UTF-8?B?LnBkZg==?="  JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5k b2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPj4K ...（base64 编码的 PDF 数据，省略）  ------=_Part_42_20260704-- ```  结构拆解  1. Return-Path    — SMTP MAIL FROM 信封地址，由最终投递 MTA 写入（RFC 5321 §4.4） 2. Delivered-To    — 最终投递邮箱，由本地 MDA 写入 3. Received × 2    — 两跳路由：client → mx1 → mx2 4. DKIM-Signature    — 域名密钥签名，验证消息完整性和来源（RFC 6376） 5. Date / From / To / Subject    — RFC 5322 核心头部。Subject 和 display-name 使用了 RFC 2047 B 编码 6. Message-ID    — 全局唯一标识 7. MIME-Version: 1.0    — MIME 合规性声明 8. Content-Type: multipart/mixed    — 外层 MIME 容器 9. Body Part 1    — multipart/alternative：纯文本 + HTML 10. Body Part 2     — application/pdf：base64 编码的 PDF 附件  6. 命令示例：解析原始邮件6.1 使用 Python 标准库解析 .eml 文件  ``` # 解析 .eml 文件，打印 MIME 树结构和头部信息 python3 -c " import email import sys  with open('sample.eml', 'rb') as f:     msg = email.message_from_binary_file(f)  print('=== 头部字段 ===') for key in ('From','To','Subject','Date','Message-ID','MIME-Version'):     val = msg.get(key, '(none)')     # 自动解码 RFC 2047 encoded-word     from email.header import decode_header, make_header     try:         decoded = str(make_header(decode_header(val)))     except:         decoded = val     print(f'{key:>15s}: {decoded}')  print('\n=== MIME 结构遍历 ===') def walk_parts(msg, depth=0):     indent = '  ' * depth     ct = msg.get_content_type()     encoding = msg.get('Content-Transfer-Encoding', 'none')     print(f'{indent}[{ct}] encoding={encoding}')     if msg.is_multipart():         for part in msg.get_payload():             walk_parts(part, depth + 1)     else:         size = len(msg.get_payload(decode=True) or b'')         print(f'{indent}  -> {size} bytes decoded')  walk_parts(msg) " ```  6.2 提取邮件附件  ``` python3 -c " import email, os, sys  with open('sample.eml', 'rb') as f:     msg = email.message_from_binary_file(f)  os.makedirs('attachments', exist_ok=True) for part in msg.walk():     cd = part.get('Content-Disposition', '')     if 'attachment' not in cd:         continue     filename = part.get_filename()     if not filename:         continue     data = part.get_payload(decode=True)     path = os.path.join('attachments', filename)     with open(path, 'wb') as out:         out.write(data)     print(f'提取: {filename} ({len(data)} bytes)') " ```  6.3 使用 openssl 直连 SMTP 查看原始交互  ``` # 连接 SMTP 服务器，查看 EHLO 扩展能力（含 8BITMIME、STARTTLS 等） openssl s_client -connect smtp.example.com:465 -crlf -quiet 2>/dev/null | head -20  # 或通过 STARTTLS 升级： openssl s_client -connect smtp.example.com:25 -starttls smtp -crlf -quiet 2>/dev/null ```  6.4 解码 base64 / quoted-printable 快速检查  ``` # 解码 base64 字符串 echo -n '5L2g5aW9IOS4reWbveS6ug==' | base64 -d  # 解码 quoted-printable python3 -c " import quopri, sys data = sys.stdin.buffer.read() sys.stdout.buffer.write(quopri.decodestring(data)) " < qp_payload.txt ```  7. 国际化扩展 — RFC 6532 RFC 6532（Internationalized Email Headers）是 EAI（Email Address Internationalization）体系的一部分，扩展了 RFC 5322 头部字段格式以原生支持 UTF-8 字符：   * 头部字段值可直接使用 UTF-8（非 US-ASCII），无需 encoded-word * From   、   To   等地址的 display-name 可直接包含非 ASCII 字符 * 前提：SMTP 传输链必须支持 SMTPUTF8 扩展（RFC 6531）  ``` # 传统方式 (RFC 2047) Subject: =?UTF-8?B?5L2g5aW9IOS4reWbveS6ug==?=  # EAI 方式 (RFC 6532) Subject: 你好 中国用户 ```   当前 EAI 的部署渗透率有限 — 大量传统 MTA 不支持 SMTPUTF8，发送方 MUA 通常回退到 RFC 2047 编码。 8. 常见误区和调试提示8.1 头部行长度限制 RFC 5322 §2.1.1 限制每行不超过 998 字符（推荐 ≤78）。过长的头部行（特别是未经折叠的 Received 行和 DKIM-Signature）可导致解析器拒绝消息。 8.2 Content-Transfer-Encoding 的传输层陷阱 部分 MTA 在转发 8bit 邮件给不支持 8BITMIME 的下一跳时，不告警也不退回 — 只是静默将第 8 位置零，损坏多字节字符。选择 base64 永远是最安全的方式。 8.3 Message-ID 的线程重建 邮件客户端依赖 References 和 In-Reply-To 头部构建线程视图。如果 MUA 不生成标准 Message-ID 或不维护 References，收件人看到的将是散乱的平铺消息。 8.4 boundary 冲突 如果 boundary 字符串偶然出现在 body part 内容中（如用户邮件正文包含 boundary 字面量），解析器会误判消息结束，导致截断或内容错乱。RFC 2046 §5.1.1 的"全局唯一性"规则就是为了防止此问题。 9. 参考 RFC 清单  9. 参考 RFC 清单  | RFC | 标题 | 状态 | | --- | --- | --- | | RFC 5322 | Internet Message Format | 标准（Draft Standard） | | RFC 2045 | MIME Part One: Format of Internet Message Bodies | 标准 | | RFC 2046 | MIME Part Two: Media Types | 标准 | | RFC 2047 | MIME Part Three: Message Header Extensions for Non-ASCII Text | 标准 | | RFC 2049 | MIME Part Five: Conformance Criteria and Examples | 标准 | | RFC 2231 | MIME Parameter Value and Encoded Word Extensions | 标准 | | RFC 6532 | Internationalized Email Headers | 标准 | | RFC 5321 | Simple Mail Transfer Protocol | 标准 | | RFC 6376 | DomainKeys Identified Mail (DKIM) Signatures | 标准 | | RFC 6838 | Media Type Specifications and Registration Procedures | BCP 13 | ```` |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc5322-mime-message-format.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
