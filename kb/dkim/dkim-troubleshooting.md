---
title: "RFC 6376 · 4 类常见失败场景与修复方法"
source: "https://ztpop.net/kb/dkim-troubleshooting.html"
license: CC-BY 4.0
---

# RFC 6376 · 4 类常见失败场景与修复方法

DKIM签名验证失败诊断指南 · ztpop 邮件技术知识库

## 摘要

DKIM 签名验证失败分为 signature 失败（permfail）和 body hash 失败（permfail）两类。本文覆盖 DKIM 验证失败最常见的 4 种场景，分别阐述其根本原因、诊断方法和修复步骤。

## 1. body hash 不匹配

### 1.1 原理

DKIM 签名包含两部分哈希（RFC 6376 §3.7）：

* `bh=`
  — 邮件正文（body）的 SHA-256 哈希
* `b=`
  — 邮件头选定字段 + bh 的整体 RSA 签名

`body hash did not verify`
意味着签名中的
`bh=`
值（发信时计算的）与实际接收到的邮件正文的 SHA-256 值不一致。差异源于邮件在传输路径中被中间设备修改。

### 1.2 常见修改源

1. **MIME 转码**
   ：传输中的 MTA 将 8-bit 正文转换为 7-bit（
   `Content-Transfer-Encoding: 8bit → quoted-printable`
   ）。
2. **邮件安全网关 / 反垃圾引擎**
   ：在邮件末尾附加免责声明（Disclaimer）或安全警告文本。字节层面的正文被追加了内容。
3. **链接改写**
   ：URL 重写/跟踪（click-tracking）机制修改正文中的链接。
4. **电子邮件列表服务器**
   ：如 Mailman，在邮件末尾添加列表信息、退订链接。

### 1.3 诊断

1. 从收信方获取未修改的原始邮件（import 到 MTA 的 hold 队列）。
2. 确认发信后到返回 DKIM 失败之间的邮件传输路径上是否有转码/安全设备：

```
# 查看邮件头中的内容类型变化
grep -i "content-transfer-encoding" email.eml
```

1. 禁用列表服务器或安全网关的正文修改（添加页脚/改写链接），发送测试邮件确认。

## 2. DKIM 选择器不匹配

### 2.1 原理

DKIM 签名标签
`s=`
（RFC 6376 §3.5）指定了使用的选择器（selector）。接收方根据
`s=`
值构造 DNS 查询：
`selector._domainkey.example.com`
，获取对应选择器的 TXT 记录（公钥）。

如果 DNS 中的选择器记录与签名中的
`s=`
值不一致，验证直接失败。

### 2.2 常见原因

* 选择器名称拼写错误（含大小写，虽然 RFC 6376 不区分大小写，但部分实现区分）
* DNS 记录中的选择器域与签名中的签名域（
  `d=`
  标签）不在同一个父域（如签名是
  `d=sub.example.com`
  但 DNS 记录在
  `example.com`
  上）
* DNS 记录未对外网公开（split DNS / 内部 DNS 视图导致公网查询不到）

### 2.3 诊断与修复

```
# 查看邮件头中的签名
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
  d=example.com; s=202501;
  h=from:to:subject:date;
  bh=...; b=...

# DNS 查询公钥
dig TXT 202501._domainkey.example.com

# 如果无返回：
dig TXT 202501._domainkey.example.com @8.8.8.8  # 使用公共 DNS
```

## 3. 密钥轮换期 DNS 未同步

### 3.1 原理

DKIM 密钥有生命周期，M³AAWG 最佳实践建议每 6 个月轮换。轮换时新旧密钥需要共存一段时间（建议 24 小时以上），确保在途邮件不会用已删除的公钥去验证。

### 3.2 标准轮换流程

1. 生成新密钥对，发布新选择器（如
   `202501`
   →
   `202506`
   ）的 DNS TXT 记录。
2. 发信 MTA 切换到新选择器。
3. 保留旧选择器的 DNS 记录，持续监控旧选择器的查询日志。
4. 旧选择器查询量降至 0 后（通常 24-48 小时），删除旧 DNS TXT 记录。

## 4. MIME 多部分正文不一致

### 4.1 原理

如果邮件是 multipart/alternative MIME（同时包含
`text/plain`
和
`text/html`
两个正文版本），DKIM 签名覆盖的是整个邮件正文（both parts）。

虽然 DKIM 规范不要求两个 MIME 部分内容一致，但部分老旧实现或特定配置的发送软件可能导致两个部分内容差异过大，触发接收方反垃圾策略的信任度降级。

### 4.2 修复

1. 确保 HTML 版本和纯文本版本在语义上一致（不需要逐字相同，但应反映相同的核心内容）。
2. 配置发信 MTA 或第三方 ESP 同时生成两个版本而非仅生成 HTML。
3. 使用邮件测试工具（如 mail-tester.com）检查 multipart/alternative 评估。

## 5. 通用排查流程

```
# Step 1: 查看退信中的 Authentication-Results
grep -i "dkim=" bounce.eml

# Step 2: 查看原始邮件的 DKIM-Signature 头
grep -i "DKIM-Signature" original.eml

# Step 3: 提取选择器和签名域，在 DNS 中验证
# s=202501  d=example.com  → 查询
dig TXT 202501._domainkey.example.com

# Step 4: 检查 d= 域与 i= 域是否匹配
# i=user@example.com 必须与 d=example.com 同域或子域（RFC 6376 §3.5）

# Step 5: 在线诊断
# mxtoolbox.com/dkim.aspx
# dkimvalidator.com
# mail-tester.com
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-troubleshooting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
