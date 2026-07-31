---
title: "ENISA 威胁态势报告：邮件仍是攻击首选入口，钓鱼与 BEC 持续高发"
source: "https://ztpop.net/kb/enisa-email-security-threat-landscape.html"
license: CC-BY 4.0
---

# ENISA 威胁态势报告：邮件仍是攻击首选入口，钓鱼与 BEC 持续高发

## 概述

欧盟网络安全局（ENISA）每年发布《威胁态势》（Threat Landscape, ETL）报告。2023 版覆盖 2022 年 7 月至 2023 年 6 月，分析了约 2,580 起事件（另有 220 起跨多成员国事件）。报告再次确认：邮件是攻击者最常用的初始访问向量，钓鱼（phishing）与商业邮件诈骗（BEC/VEC）持续高发。本文译介其核心数据与缓解建议。

## 八大威胁与占比

ENISA 将事件归入八大威胁类别，按观测事件数排序：

| 威胁 | 事件数 | 占比 |
| --- | --- | --- |
| 勒索软件 Ransomware | 1,480 | 31.32% |
| DDoS | 1,010 | 21.40% |
| 数据事件 Data | 950 | 20.09% |
| 恶意软件 Malware | 390 | 8.24% |
| 社工 Social Engineering | 370 | 7.88% |
| 信息操纵 Info Manipulation | 230 | 4.81% |
| Web 威胁 | 140 | 3.03% |
| 供应链 Supply Chain | 100 | 2.10% |
| 零日 Zero Day | 50 | 1.60% |

勒索软件与可用性威胁居首，但报告明确指出"钓鱼再次成为最常见的初始访问向量"，而 BEC/VEC"仍是攻击者获取经济利益的最爱手段"。

## 邮件相关威胁：钓鱼与 BEC

邮件在威胁链中扮演双重角色：一是社工与钓鱼的主战场——攻击者通过伪造发件域、恶意附件或链接诱导凭据泄露；二是 BEC/VEC 的载体——攻陷合法邮箱后发起虚假付款或数据窃取。值得注意的是，随着 Microsoft 禁用 Office 宏，攻击者转向 ISO、OneNote、LNK 文件作为载荷投递载体，这对依赖附件检测的邮件安全网关提出了新课题。

## 攻击技术演变趋势

* **宏退场、ISO/OneNote/LNK 登场**：响应 Microsoft 宏策略变化，载荷格式迁移。
* **AI 聊天机器人助长社工**：深度伪造与生成式内容提升钓鱼与信息操纵的逼真度。
* **双重勒索常态化**：数据窃取 + 加密勒索，提高谈判压力。
* **滥用合法工具**：RMM 软件、云配置错误被利用于隐蔽驻留与横向移动。

## ENISA 缓解建议（映射 ISO 27001 / NIST CSF）

1. **资产清点与风险评估**：识别关键目标，奠定缓解基础。
2. **漏洞扫描与补丁**：按策略定期更新，建立漏洞披露与事件通报流程。
3. **防钓鱼 MFA**：对远程访问等暴露面启用抗钓鱼多因素认证，配合强口令策略。
4. **最小权限与职责分离**：压缩攻击面。
5. **安全冗余备份**：维护离线、加密、定期演练的备份。
6. **安全意识培训**：针对 HR/销售/财务等部门定制，覆盖演变中的社工手法。
7. **零信任架构**：以"永不信任、始终验证"提升整体 posture。

## 对信创邮件与邮件安全网关的启示

ENISA 的建议与 NIST、M3AAWG 高度一致：邮件认证（SPF/DKIM/DMARC）是第一道防线，MFA 是账号基线，意识培训覆盖财务等高风险岗位。在信创邮件替换与 Exchange 迁移过程中，邮件安全网关应内置多引擎检测（含对 ISO/OneNote/LNK 等新载体的沙箱分析），并将 DMARC 强制与 TLS-RPT / MTA-STS 一并纳入上线验收。

### 相关主题

* [钓鱼邮件防御体系](/kb/phishing-defense.html)：网关 + 意识 + 认证的纵深组合
* [商业邮件诈骗防御实战](/kb/bec-defense.html)：从检测到止损的端到端闭环
* [邮件安全威胁全景](/kb/email-security-threats.html)：钓鱼、BEC、恶意软件的分类与应对
* [DMARC 完全指南](/kb/dmarc-guide.html)：从 p=none 到 p=reject 的部署路径
* [邮件纵深防御](/kb/email-defense-in-depth.html)：多层检测与响应的体系化思路

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/enisa-email-security-threat-landscape.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
