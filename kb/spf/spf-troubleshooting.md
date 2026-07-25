---
title: "RFC 7208 · 5 类常见失败原因与修复方法"
source: "https://ztpop.net/kb/spf-troubleshooting.html"
license: CC-BY 4.0
---

# RFC 7208 · 5 类常见失败原因与修复方法

## 摘要

SPF 是最基础的邮件认证协议，但配置错误率居高不下。RFC 7208 §4.6 定义了 SPF 验证的完整流程，涵盖 DNS 查询机制、结果判定和错误处理。本文按发生频率排列 5 类最常见的 SPF 验证失败场景，提供诊断步骤和修复方法。

## 1. DNS 查询超过 10 次（permerror）

### 1.1 原因

SPF 协议硬性限制每次验证的总 DNS 查询次数不得超过 10 次（RFC 7208 §4.6.4）。每次
`include`
、
`a`
、
`mx`
、
`ptr`
机制都会触发至少一次 DNS 查询。链式
`include`
中嵌套的查询也计入同一个 10 次限额。

### 1.2 症状

```
Authentication-Results: example.com; spf=permerror smtp.mailfrom=example.com
# (too many DNS lookups)
```

### 1.3 修复

1. **展平（Flatten）SPF 记录**
   ：将嵌套的
   `include`
   展开为
   `ip4`
   /
   `ip6`
   授权。例如将
   `include:spf.protection.outlook.com`
   替换为其最终解析的 IP 范围列表。
2. **合并冗余 include**
   ：如果一个服务商的多个
   `include`
   实际指向同一组 IP，则只保留一个。
3. **避免使用 ptr 机制**
   ：RFC 7208 §5.5 已废弃
   `ptr`
   机制，它不仅消耗大量 DNS 查询且安全性低。

```
# 展平前（查询次数 = 7）
v=spf1 include:spf1.example.com include:spf2.example.com
  include:spf3.example.com include:spf4.example.com
  include:_spf.google.com ~all

# 展平后（查询次数 = 1）
v=spf1 ip4:203.0.113.0/24 ip4:198.51.100.0/24
  include:_spf.google.com ~all
```

## 2. 多条 SPF 记录（permerror）

### 2.1 原因

RFC 7208 §4.5 明确规定：一个域名的 SPF 检查应返回确切的一条 TXT 记录。当 DNS 中存在多条
`v=spf1`
开头的 TXT 记录时，接收方无法判断使用哪一条，返回 permerror。

### 2.2 症状

```
Authentication-Results: example.com; spf=permerror smtp.mailfrom=example.com
# (multiple SPF records found)
```

### 2.3 修复

1. 检查 DNS：
   `dig TXT example.com | grep "v=spf1"`
2. 将所有
   `include:`
   和
   `ip4:`
   /
   `ip6:`
   授权合并为一条记录。
3. 删除多余的 SPF TXT 记录。
4. 保留非 SPF 的 TXT 记录（如
   `google-site-verification`
   ）不受影响。

```
# 错误：两条 SPF 记录
v=spf1 include:spf1.example.com ~all
v=spf1 include:spf2.example.com ~all

# 正确：合并为一条
v=spf1 include:spf1.example.com include:spf2.example.com ~all
```

## 3. MAIL FROM 域与 From 域不一致

### 3.1 原因

SPF 检查的是 SMTP 信封域的
`MAIL FROM`
命令中声明的域名（RFC 5321），
**而非**
邮件头
`From:`
字段。如果两个域不同（即使用了外包邮件发送服务而 MAIL FROM 是外包服务商的域），即使 SPF 验证本身通过，DMARC 的
`aspf=s`
（对齐失败）也会导致整体认证失败。

### 3.2 症状

```
Authentication-Results: example.com;
  spf=pass smtp.mailfrom=bounce.sendgrid.net;
  dmarc=fail (p=reject sp=reject) header.from=example.com
```

### 3.3 修复

1. 方案 A（推荐）：让外包邮件服务商支持自定义 MAIL FROM 域（又称 Return-Path 自定义）。需要为你的域配置独立的 MAIL FROM 域（如
   `bounce.example.com`
   ）并添加对应的 SPF 记录。
2. 方案 B：将外包服务商的 MAIL FROM 域加入你的域的 SPF
   `include`
   。

## 4. 第三方发送方未 include

### 4.1 原因

每新增一个代表你的域发信的第三方服务（如 SendGrid、MailChimp、Postmark），都需要在 SPF 记录中
`include`
该服务商的 SPF 授权域。遗漏将导致该服务商发出的邮件 SPF 返回
`softfail`
或
`fail`
。

### 4.2 修复

从每个使用的第三方服务获取其 SPF include 域，追加到 SPF 记录中。注意每次新增 include 会增加 DNS 查询次数。

```
v=spf1 include:spf.example.com include:_spf.google.com
  include:sendgrid.net include:spf.mandrillapp.com
  include:mail.zendesk.com -all
```

## 5. 语法错误

### 5.1 常见语法问题

* **缺少 v=spf1 前缀**
  ：SPF 记录必须以
  `v=spf1`
  开头，否则被忽略
* **使用已弃用的 ptr 机制**
  ：RFC 7208 §5.5 明确列
  `ptr`
  为"不应使用"
* **使用大写字符**
  ：虽然大多数实现不区分大小写，但不鼓励使用大写机制名
* **`-all`
  前有空格**
  ：部分 SPF 解析器对此敏感
* **DN S末尾有额外空格或换行符**

### 5.2 验证工具

```
# DNS 查询
dig TXT example.com

# 在线验证
# mxtoolbox.com/spf.aspx
# dmarcian.com/spf-survey/
# kitterman.com/spf/validate.html（Scott Kitterman，RFC 7208 作者的工具）
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-troubleshooting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
