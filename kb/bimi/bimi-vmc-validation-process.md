---
title: "BIMI VMC 验证流程详解：三阶段验证指南"
source: "https://ztpop.net/kb/bimi-vmc-validation-process.html"
license: CC-BY 4.0
---

# BIMI VMC 验证流程详解：三阶段验证指南

翻译自 BIMI Group VMC Guidelines v1.1

VMC 的验证流程是 BIMI 安全体系中最重要的环节。BIMI Group 联合 CA/B Forum 制定了严格的三阶段验证流程，确保每个 VMC 的签发都经过完整的审查。本章详解三个阶段的具体技术细节。

## 阶段一：商标验证

### 商标注册证明

申请者需要提供在其目标市场的商标注册证明。具体要求包括：

* 商标必须在目标国的官方商标局有效注册（在美国为 USPTO，中国为 CNIPA，欧盟为 EUIPO）
* 商标注册状态必须是"Registered"（注册有效），而非"Pending"（审查中）
* TM（商标申请中标志）仅适用于极少数特殊情况，大部分 CA 不接受 TM 作为 VMC 申请
* 商标的注册日期必须早于 VMC 申请日期

### 商标所有者证明

CA 需要确认 VMC 申请者是商标的合法所有者。如果商标属于母公司，申请者作为子公司授权使用，需要额外提交商标授权书（Letter of Authorization）。BIMI Group 建议授权书中明确商标的使用范围、地域、期限。

## 阶段二：域验证

### DKIM/DMARC 配置检查

CA 会自动化检查申请域的以下配置：

* **DMARC 记录**：必须存在且策略为 p=quarantine 或 p=reject。p=none 不接受。DMARC 报告中的认证通过率需达到 95% 以上。
* **DKIM 签名**：出站邮件必须使用申请域签名域（d=domain）进行 DKIM 签名。CA 会抽样验证 DKIM 签名的有效性。
* **SPF 记录**：必须存在正确配置的 SPF 记录（虽然 BIMI 本身不直接需要 SPF）。

### 域所有权确认

CA 采用以下方式之一验证域所有权：

* **DNS TXT 挑战**：CA 提供一个随机字符串，申请者在域 DNS 的特定 \_validation 子域中添加 TXT 记录
* **WHOIS 邮箱验证**：向 WHOIS 中注册的域联系人邮箱发送验证链接
* **HTTP 文件上传**：在域根目录的指定路径上传 CA 提供的验证文件

## 阶段三：组织验证

### 企业注册文件

CA 要求提交以下企业证明文件之一：

* 营业执照（中国企业）
* Articles of Incorporation（美国企业）
* Certificate of Incorporation（英联邦国家）
* 其他 CA 接受的同等企业注册文件

### 法人授权

需要由企业法定代表人（CEO 或同等负责人）签署 VMC 申请授权书。授权书需包含：

* 申请企业全称和注册号
* 申请域名列表
* 商标名称和注册号
* 签署人姓名和职位
* 公证签章（部分 CA 要求）

## 验证周期

标准验证周期为 5-15 个工作日。EV-VMC 通常需要更长时间（10-20 个工作日），因为组织验证的深度更大。CA 可能需要补交材料、回复澄清问题，这会延长验证时间。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-vmc-validation-process.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
