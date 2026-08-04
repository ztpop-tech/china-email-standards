---
title: "IETF 正式发布更新版 DMARC 规范：RFC 9989/9990/9991"
source: "https://ztpop.net/kb/ietf-publishes-updated-dmarc-specification.html"
license: CC-BY 4.0
---

# IETF 正式发布更新版 DMARC 规范：RFC 9989/9990/9991

## 概述

2026 年 5 月 20 日，IETF（互联网工程任务组）的 RFC 编辑正式发布了三份更新 DMARC（基于域的消息认证、报告与一致性）协议的文档，将此前称为「DMARCbis」的变更与增强写入正式标准，并将更新后的 DMARC 协议提升至 IETF 的 **Standards Track（标准轨道）**[[1]](#ref-1)。

这标志着 IETF 的 [DMARC 工作组](https://datatracker.ietf.org/wg/dmarc/)多年工作的里程碑：自 [ARC 协议（RFC 8617）](https://www.rfc-editor.org/info/rfc8617)于 2019 年定稿后不久，工作组便正式启动了更新工作。

## 三份新文档

此次发布包含三份 RFC 文档，分别覆盖 DMARC 协议的不同层面：

* **[RFC 9989](https://www.rfc-editor.org/rfc/rfc9989.html)** —— 描述核心协议
* **[RFC 9990](https://www.rfc-editor.org/rfc/rfc9990.html)** —— 涵盖聚合报告（Aggregate Reporting）
* **[RFC 9991](https://www.rfc-editor.org/rfc/rfc9991.html)** —— 详细说明失败报告（Failure Reporting）

## 主要变更亮点

新规范的主要变更包括以下内容：

* **Public Suffix List 被替换**：以 DNS Tree Walk（DNS 树遍历）和 Public Suffix Domains / PSD（公共后缀域）机制取而代之，不再依赖 [Public Suffix List](https://publicsuffix.org/)（公共后缀列表）。
* **多个标签被废弃**：`pct=`、`rf=`、`ri=` 标签不再使用。
* **新增 `np=` 标签**：用于指定对不存在的子域的策略。
* **引入 `psd=` 标签**：源自已废止的 [RFC 9091](https://www.rfc-editor.org/rfc/rfc9091.html)。
* **移除 `rua=` 中的报告大小限制符号**：`rua=` 标签不再包含报告大小限制的表示法。
* **DMARC SPF 仅使用 MAIL FROM 地址**：不再回退到 HELO 标识（HELO identity）。
* **PII/NPI 风险指导大幅增强**：在报告环节中新增了大量关于个人身份信息（PII）和非公开个人信息（NPI）风险的指引[[2]](#ref-2)。

## 背景与意义

DMARC 协议自 2012 年作为实验性标准发布以来，已成为全球邮件认证领域的基石。此次更新将 DMARC 从实验性标准（Experimental）提升为 **Standards Track（标准轨道）**，意味着协议经过了充分的审查与实践检验，具备了正式互联网标准的技术成熟度。这是国内业界首次关注到 DMARC 协议正式进入标准轨道这一重要转变。

新文档分组被称为「DMARCbis」，这一代号此前在 IETF 工作组的讨论与草案阶段使用，如今随着三份 RFC 的正式发布而尘埃落定。对于邮件管理员、安全运维人员以及邮件系统开发商而言，这些变更直接影响到 DNS 配置、报告接收机制和安全策略的实施方式。

本文由 ztpop.net 知识库编辑发布。了解更多邮件技术实践，请访问知识库或扫码联系我们。

本站技术文章采用 CC-BY 4.0 许可，可自由引用，仅需标注来源 [ztpop.net](https://www.ztpop.net)。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ietf-publishes-updated-dmarc-specification.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
