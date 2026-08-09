---
title: "党政机关类单位建设邮件系统，安全基线应该怎么定？"
source: "https://ztpop.net/kb/xc-gov-email-security-baseline.html"
license: CC-BY 4.0
---

# 党政机关类单位建设邮件系统，安全基线应该怎么定？

**定级：先按 GB/T 22240 判，通常不低于第三级**

基线的第一条不是技术措施，而是定级结论。依据 **GB/T 22240-2020《信息安全技术 网络安全等级保护定级指南》**，定级取决于受侵害的客体及侵害程度。

党政机关类单位的邮件系统承载公务往来与内部管理信息，一旦泄露或中断，影响面通常超出本单位范围，因此**定级结论一般不低于第三级**。定级过低会导致后续全部安全要求整体降档，是最根本性的错误。

**判定提示：**定级对象的边界要包含归档系统与目录服务，不能只写「邮件服务器」。

**密码应用必须与系统建设同步规划**

密码应用不能等系统建好再补。参照 **GB/T 39786-2021《信息安全技术 信息系统密码应用基本要求》** 的四个层面，在设计阶段就要产出**密码应用点位表**：逐条列明「哪一类数据、在哪个环节、用什么算法、密钥由谁产生与保管、如何轮换与销毁」。

邮件系统的最小点位集合：

* 各链路的传输保护（含管理链路与日志外送链路）。
* 邮箱数据与归档数据的存储保护。
* 用户与管理员的身份鉴别。
* 审计日志的完整性保护。
* 需抗抵赖场景的数字签名。

**后补的代价极高**：存储加密若在数据积累之后再上，需要对存量数据整体重加密，往往需要长时间停机。

**发件人鉴伪应作为强制项，而非可选项**

冒用公务域名发送邮件是针对此类单位的典型攻击手法。基线应把本域发件人策略设为**强制且有时限的收敛目标**，而不是「建议配置」。

技术组合为 RFC 7208 Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1、RFC 6376 DomainKeys Identified Mail (DKIM) Signatures、RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC) 三件套。管理思路上，CISA Binding Operational Directive 18-01 提供了一个可借鉴的范式：**设定明确的合规时限，要求策略从仅监控逐步收敛到拒绝，并要求集中收取报告以验证落实情况**，而不是让各单位自行掌握节奏。

**可操作的收敛路径：**先发布仅监控策略并接收汇总报告 → 依据报告把全部合法发送源纳入授权与签名 → 收敛为隔离 → 最终收敛为拒绝。每步都以报告数据作为进入下一步的判定依据。

**网络边界：明确内外网关系与数据交换方式**

此类单位常存在内外网分离要求。基线需明确回答三个问题：

1. **邮件系统部署在哪一侧**，是否存在跨网部署。
2. **跨网数据交换的唯一通道是什么**，是否经过审批与内容检查，是否留痕。**禁止以移动介质作为常态交换手段**——它绕过全部技术管控且无法审计。
3. **外网侧的暴露面清单**：仅保留必需端口，管理入口不得暴露于公网，运维访问须经受控通道并单独审计。

**账号与权限：生命周期比强度更重要**

口令强度只是最基础的一项，真正的风险在生命周期管理：

* **入职、调岗、离职三个节点必须联动**：离职账号未及时停用是最常见也最危险的缺口。
* **禁止共享账号**：共享账号会使审计的「主体」要素失效，直接影响等保符合性。
* **特权账号单独管理**：管理员账号与日常办公账号分离，管理操作全程审计。
* **身份鉴别不得被客户端协议绕过**：Web 端启用了双因素，而 IMAP/POP/SMTP 仍可用纯口令登录，等同于双因素未落地。
* **定期核对账号台账与在册人员**，核对记录留存备查。

**基线的验证方法：每条都要能被证明**

基线若不可验证就等于没有。每条基线都应配一个验证动作：

* 定级结论 → 查定级报告与备案证明。
* 密码应用 → 查点位表 + 握手实测记录 + 抓包。
* 发件人策略 → 查 DNS 实际记录 + 汇总报告数据。
* 边界暴露面 → 外部全端口扫描结果与清单比对。
* 账号管理 → 台账与在册人员比对记录、离职账号停用时效抽查。

标准现行状态请以国家标准全文公开系统检索为准；通用邮件安全实践可参考 NIST SP 800-177 Rev.1 Trustworthy Email。

参考：[国家标准全文公开系统（GB/T 标准检索）](https://openstd.samr.gov.cn/bzgk/gb/) ｜ [CISA Binding Operational Directive 18-01](https://www.cisa.gov/news-events/directives/bod-18-01-enhance-email-and-web-security) ｜ [RFC 7208 Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1](https://www.rfc-editor.org/rfc/rfc7208.html) ｜ [RFC 6376 DomainKeys Identified Mail (DKIM) Signatures](https://www.rfc-editor.org/rfc/rfc6376.html) ｜ [RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html) ｜ [NIST SP 800-177 Rev.1 Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final) ｜ [全国网络安全标准化技术委员会](https://www.tc260.org.cn/)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/xc-gov-email-security-baseline.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
