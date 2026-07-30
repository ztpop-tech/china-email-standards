---
title: "DKIM规范化算法与签名验证"
source: "https://ztpop.net/kb/dkim-canon-algo-deepdive.html"
license: CC-BY 4.0
---

# DKIM规范化算法与签名验证

## 规范化（Canonicalization）概述

DKIM规范化的核心目的是在签名方和验证方之间统一消息格式，消除邮件传输过程中由MTA引入的无意内容变动。RFC 6376 §3.4定义了两种规范化算法——simple和relaxed，分别应用于头部（header）和正文（body），形成四种组合配置：simple/simple、simple/relaxed、relaxed/simple和relaxed/relaxed。

规范化签名标签c=的格式为c=header\_algo/body\_algo。例如c=relaxed/relaxed表示头部和正文都使用relaxed模式。若省略body\_algo，则默认与header\_algo相同。理解每种模式的操作规则，是正确实施DKIM签名的前提。

## 头部规范化详解

### simple模式（RFC 6376 §3.4.1）

simple模式的头部规范化不做任何转换，仅删除DKIM-Signature头部本身（签名方保留，验证方只验证已签名头部）。这是最严格的模式——任何头部格式变化（包括空白符和换行）都会导致签名验证失败。simple模式在实际部署中较少使用，因为它对MTA的头部处理极为敏感。

### relaxed模式（RFC 6376 §3.4.2）

relaxed模式执行以下转换：

* 压缩连续空白字符（WSP）为单个空格（ASCII 0x20）
* 删除头部值前后的空白
* 将头部字段名转换为小写
* 将非结构化字段内容中的连续空白折叠为单个空格
* 删除字段值末尾的空白字符
* 但\*\*不修改\*\*结构化字段（如From、To等RFC 5322定义的字段）的内部结构

```
# 原始头部
Subject: Hello    World   !

# relaxed规范化后
subject:Hello World !

# 转换要点：
# 1. 字段名转换为小写: Subject → subject
# 2. 冒号后删除空格: : → :
# 3. 连续空白压缩: "Hello    World   !" → "Hello World !"
```

## 正文规范化详解

### simple模式正文规范化

simple正文规范化几乎没有修改，仅执行：删除正文末尾的所有空行（CRLF），确保正文以单个CRLF结尾。这是最宽容的模式，因为正文的任何其他修改都会导致验证失败。

### relaxed模式正文规范化

relaxed正文规范化执行以下转换：

* 将所有空白字符（WSP：空格0x20和制表符0x09）压缩为单个空格
* 删除每一行末尾的空白
* 删除正文末尾的所有空行（与simple一致）

对于MIME多部分消息，relaxed规范化仅作用于原始MIME结构层级内的边界行和内容。MIME内容编码（如Base64）的规范化也需要特别注意——Base64编码内容中的空白行在relaxed模式下会被改变，导致Base64解码结果不同。RFC 6376 §8.2特别警告：对MIME编码的内容使用relaxed正文规范化可能导致解码后的内容不一致。

## 签名验证全流程

### 步骤一：头部提取与选择

验证方首先解析消息中的DKIM-Signature头部，提取bh（正文哈希）、h（签名头部列表）、a（算法）、c（规范化）、d（域名）、s（选择器）等标签。以bh和h标签中的头部列表作为签名范围界定依据。

```
# DKIM-Signature示例
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
  d=example.com; s=2025; t=1700000000; h=from:subject:date;
  bh=47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=;
  b=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789...==
```

### 步骤二：正文哈希计算

验证方对接收到的完整消息正文执行规范化（使用c=的body\_algo），然后计算SHA-256哈希。将结果与bh标签中的Base64编码哈希值比对。若不一致，验证直接失败。

### 步骤三：签名头部哈希与验证

验证方按h标签指定的头部顺序，对已签名头部执行规范化（使用header\_algo），每个头部之间以CRLF连接。规范化后的头部列表被传递给签名验证算法。验证方从DNS获取公钥（通过d+选择器查询），使用公钥验证b标签中的签名值。

```
# DNS查询
2025._domainkey.example.com TXT
  "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb4DQEBAQUAA4GNADCBiQKBgQC..."

# 验证命令（opendkim）
opendkim -vvV -t test.eml
# 输出应包含：signature verification successful
```

### 步骤四：验证结果处理

验证成功意味着整个消息（头部和正文）在签名后未被修改。但验证成功并不等价于认证通过——还需配合DMARC策略评估email from的Domain Alignment。

## 规范化与签名验证的兼容性陷阱

不同MTA和DKIM实现之间常见的兼容性问题：

* MIME边界行的空白处理：某些MTA在传输多部分消息时会修改边界行格式
* 头部折叠（header folding）：长头部可能在传输中被自动折叠，影响simple模式验证
* 字符集转换：邮件网关的字符集转换可能改变正文二进制表示
* 签名头部列表排序：签名方和验证方对h标签中头部顺序的理解必须完全一致
* 尾部空行处理：邮件列表追加的签名和脚注会破坏bh哈希一致性

实践建议：始终选择relaxed/relaxed作为规范化模式，它提供了最佳的兼容性平衡。仅在安全要求极高且MTA链路完全受控的情况下使用simple/simple。对于邮件列表和自动转发场景，考虑使用ARC（RFC 8617）来保护DKIM签名的一致性。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-canon-algo-deepdive.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
