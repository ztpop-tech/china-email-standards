---
title: "BIMI VMC 认证要求详解：证书类型、颁发条件与申请流程"
source: "https://ztpop.net/kb/bimi-vmc-requirements-overview.html"
license: CC-BY 4.0
---

# BIMI VMC 认证要求详解：证书类型、颁发条件与申请流程

翻译自 BIMI Group VMC Requirements v1.8 规范文档

VMC（Verified Mark Certificate，验证标志证书）是 BIMI（品牌标识消息识别）体系中的核心组件。VMC 由受信任的 CA（证书颁发机构）签发，向接收邮箱系统证明邮件发件方对其品牌标志拥有合法权益。本章节介绍 VMC 的基本要求和申请流程。

## VMC 证书类型

### OV（Organization Validation）组织验证型 VMC

OV-VMC 是基本级别的证书，验证组织的法人身份和商标所有权。CA 需要确认：

* 企业在注册机构（如中国的国家知识产权局商标局、美国的 USPTO）已注册该商标
* 申请组织是商标的合法持有人
* 域名所有权已通过 DNS 验证或 WHOIS 验证

### EV（Extended Validation）扩展验证型 VMC

EV-VMC 提供最高级别的品牌验证，要求更为严格的审查：

* 商标需在商标局有效注册（R 标），TM 商标可能不被接受
* 商标必须属于申请组织，而非第三方授权
* 组织的法人身份需通过政府企业数据库验证
* 高级管理人员签字确认

## VMC 颁发条件

1. **合法注册商标**：商标必须在目标发送域所在国家的商标局有效注册。商标类别需覆盖第 35 类（广告/商业管理）或第 38 类（通信服务）等与邮件发送相关的类别。
2. **域所有权验证**：申请者必须证明对发送域的控制权。验证方式包括：DNS TXT 记录挑战、WHOIS 邮箱验证、或通过 CA 提供的域验证流程。
3. **DMARC p=quarantine 或 p=reject**：发送域的 DMARC 策略必须设置为 p=quarantine 或 p=reject，且 SPF 和 DKIM 认证通过率需达到一定阈值。DMARC p=none 不被接受。
4. **BIMI 选择器 DNS 记录**：域名需发布 BIMI DNS TXT 记录，包含 SVG 标志的位置 URL（或 LPS 标识符）和 VMC 证书颁发机构 URL。

## 申请流程

1. **选择 CA**：目前支持颁发 VMC 的 CA 包括 DigiCert、Entrust、GlobalSign 和 Sectigo。
2. **提交商标证明**：提供商标注册证书扫描件（+ 英文翻译，若非英文）
3. **域名验证**：通过 DNS 挑战验证域控制权
4. **组织验证**：CA 通过企业数据库验证组织的合法注册状态
5. **颁发**：CA 颁发 VMC 证书（通常以 .p7b 或 .pem 格式提供）
6. **部署**：将 VMC 证书内容嵌入 BIMI DNS TXT 记录的 v=TLSRPTv1;p=... 字段

整个流程通常需要 5-15 个工作日。年费约为 $1,200-$3,500 美元（视 CA 和证书类型而定）。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-vmc-requirements-overview.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
