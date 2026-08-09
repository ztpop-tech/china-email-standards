---
title: "DMARC 标准演进 — RFC 9989/9990/9991（2026-05）正式发布：DNS Tree Walk 与标签体系重构"
source: "https://ztpop.net/kb/dmarc-standards-evolution.html"
license: CC-BY 4.0
---

# DMARC 标准演进 — RFC 9989/9990/9991（2026-05）正式发布：DNS Tree Walk 与标签体系重构

> 勘误说明（2026-08-09）：本文早期版本基于草案传闻误述「RFC 9989 于 2025-03 发布、Tree Walk 被弃用」。经与 RFC Editor 官方文本核对（rfc-editor.org/rfc/rfc9989），RFC 9989/9990/9991 均于 **2026 年 5 月**以 **Internet Standards Track** 状态发布，RFC 9989 的 **DNS Tree Walk 是新增的核心策略发现机制**（非被弃用）。本文已按官方文本全面修正。

## 一、概述：DMARC 正式成为互联网标准

2026 年 5 月，IETF 正式发布 **RFC 9989**（Domain-Based Message Authentication, Reporting, and Conformance (DMARC)，Standards Track），同时发布配套的 **RFC 9990**（DMARC Aggregate Reporting）与 **RFC 9991**（DMARC Failure Reporting）。

RFC 9989 废弃（Obsoletes）了服役 11 年的 **RFC 7489**（2015-03，Informational）与 **RFC 9091**（2021-07，Experimental，PSD DMARC 扩展）。RFC 9990 与 RFC 9991 分别独立规范聚合报告与失败报告，同时废弃 RFC 7489 的相应章节；RFC 9991 还更新了 RFC 6591（ARF 格式）。这是 DMARC 协议自诞生以来最重要的一次版本升级：从 Informational 类别正式进入 IETF 标准轨道（Standards Track）。

三份文档的官方信息：

- RFC 9989 — DMARC 基础规范（T. Herr 编辑，Valimail；J. Levine 编辑，Standcore；2026-05；ISSN 2070-1721）
- RFC 9990 — DMARC Aggregate Reporting（聚合报告；2026-05；Obsoletes 7489）
- RFC 9991 — DMARC Failure Reporting（失败报告；2026-05；Obsoletes 7489，Updates 6591）

## 二、三大架构性变更

### 2.1 DNS Tree Walk：正式确立的策略发现机制（新增，非弃用）

RFC 9989 引入 **DNS Tree Walk** 作为 DMARC 策略记录发现的核心机制（Section 4.10），替代 RFC 7489 依赖公共后缀列表（PSL）的组织域判定方式。这是本文档最重要的架构变化，与早期草案误传的「Tree Walk 被弃用」完全相反。

算法要点：

1. **查询域**：在 Author Domain 的 `_dmarc` 子域下查询 TXT 记录（如 `_dmarc.example.com`）。
2. **过滤**：丢弃不以 `v=DMARC1` 开头的记录；若返回多条记录则全部丢弃。
3. **终止条件**：若找到的记录包含 `psd=n` 或 `psd=y` 标签，停止遍历。
4. **标签剥离**：将域名拆分为标签序列，每次移除最左标签后向上查询父域。
5. **安全上限**：Author Domain 超过 8 个标签时先缩短至 7 个标签，保证最多 8 次 DNS 查询，防止深层域名构造的拒绝服务攻击。

观察数据显示实际使用的 Author Domain 最多 7 个标签，8 层限制覆盖全部合法场景。DNS Tree Walk 消除了对人工维护 PSL 的依赖，同时支持多级子域的差异化策略发现。

### 2.2 子域策略：sp 标签 + np 标签两级体系

RFC 9989 保留 `sp=` 标签为子域指定策略，并新增 `np=` 标签处理「不存在的子域」（DNS 查询返回 NXDOMAIN，定义同 RFC 8020）。np 取值与 p/sp 相同（none/quarantine/reject），未设置时回退到 sp，再回退到 p。

```
v=DMARC1; p=reject; sp=quarantine; np=none; rua=mailto:dmarc@example.com
```

含义：主域 reject，现有子域 quarantine，不存在的子域（如拼写错误产生的 NXDOMAIN）仅监控，避免误拒。

### 2.3 报告体系拆分：RFC 9990 + RFC 9991

RFC 7489 单一文档中的报告章节被拆分为两份独立规范：

- **RFC 9990（聚合报告）**：XML namespace 更新为 `urn:ietf:params:xml:ns:dmarc-2.0`；policy_published 回显 fo/adkim/aspf 等标签配置；多报告 URI 时报告应发送到每个列出的 URI（RFC 9989 Section 4.6）。
- **RFC 9991（失败报告）**：基于 ARF（RFC 6591）格式，更新 RFC 6591 并废弃 RFC 7489 相应章节；强化隐私保护——失败报告不得包含原始邮件正文，仅可包含部分头部字段，Subject 中的个人数据应脱敏。

## 三、标签体系变化

### 3.1 移除标签（C.5.2）

| 移除标签 | 原含义 | 移除原因 / 替代 |
| --- | --- | --- |
| **pct** | 按百分比应用策略 | 只在 0/100 时被准确执行，中间值实现不统一；测试功能由新 `t=` 标签承担（Appendix A.6） |
| **rf** | 失败报告格式（afrf/iodef） | 报告格式由 RFC 9991 统一管理 |
| **ri** | 聚合报告间隔（秒） | 接收方很少遵循指定间隔，改为自行决定；聚合报告中作为回显字段保留 |

### 3.2 新增标签（C.5.1）

| 新标签 | 名称 | 取值与语义 |
| --- | --- | --- |
| **np** | Non-Existent Subdomain Policy | none/quarantine/reject；定义不存在子域（NXDOMAIN）的评估策略；回退顺序 np → sp → p |
| **psd** | Public Suffix Domain 标志 | y=该域是公共后缀域（PSD）；n=希望被视为自身及子域的组织域；u=不确定（默认），使用标准 DNS Tree Walk |
| **t** | Testing 测试模式 | y=请求降低一级执行策略（p=reject→实际 quarantine；p=quarantine→实际 none）；n=正常应用（默认） |

psd 标签服务于 DNS Tree Walk：PSO（公共后缀运营商）在 PSD 上发布 DMARC 记录时必须包含 `psd=y`，接收方遇到该记录即停止向上遍历，向下一级查找真正的组织域策略。

## 四、术语与行为更新

- **Organizational Domain 重新定义**：从「在域名注册商处注册的域」改为「域名命名空间层次结构中处于顶部且具有相同管理权限的域」，判定不再依赖 PSL，由 DNS Tree Walk 完成。
- **Report Consumer**：原 Report Receiver 更名，强调「消费并分析报告」的角色。
- **Domain Owner Assessment Policy**（新增术语）：域名所有者在 DMARC Policy Record 中表达的关于验证失败消息的处理偏好（p/sp/np 三标签值）。
- **Enforcement / Monitoring Mode**（新增术语）：组织域 p 不为 none 时为强制执行状态；p=none 且接收聚合报告时为监控模式。
- **多报告 URI**：报告应发送到每个列出的 URI（SHOULD），替代 RFC 7489 的「至少两个」约束，支持同时向多个服务商发送报告。

## 五、关键互操作性建议（Section 7.4）

> **重要：** RFC 9989 Section 7.4 明确指出——拥有普通用户发送日常邮件的域 **不应部署 p=reject 策略**（SHOULD NOT），接收方也不得仅凭 p=reject 策略拒绝邮件，而应将其作为综合决策的输入。

- 发布 p=reject 且仅依赖 SPF 的域名所有者，必须同时应用有效的 DKIM 签名（SPF 在转发/邮件列表等间接邮件流中几乎必然失败）。
- 用户参与互联网邮件列表的域发布 p=reject 将导致严重互操作性问题。
- 接收方在无其他信息来源时，应将 p=reject 视为 p=quarantine 处理。
- 过渡期兼容：若接收方使用 RFC 7489 实现（依赖 PSL）而域名所有者预期 DNS Tree Walk，可能得出不同组织域；可通过 strict alignment 与在组织域发布明确记录完全避免（C.3）。

## 六、推荐部署路线

1. 发布 `v=DMARC1; p=none; rua=...`（监控模式）至少一个月，收集基线数据。
2. 分析聚合报告，修复未认证的合法邮件流（补充 DKIM 签名、修正 SPF）。
3. 升级 `p=quarantine` 至少一个月，观察误判。
4. 使用 `t=y` 标签在强制执行前进行最终测试（p=reject + t=y 实际执行 quarantine）。
5. 确认通用邮件域场景后再评估是否升级 `p=reject`（参考 Section 7.4 建议）。

示例（通用邮件域推荐配置）：

```
v=DMARC1; p=none; rua=mailto:dmarc-rua@example.com,mailto:rua@third-party-service.com
```

## 七、错误勘误汇总（RFC 7489 Errata）

RFC 9989 附录 C.9 逐项列出了 RFC 7489 自 2015 年以来的 15 个勘误（Erratum ID 5151/5221/5229/5365/5371/5440/5495/5774/6439/6485/6729/7099/7100/7835/7865），并说明每一勘误在 RFC 9989/9990/9991 中如何被处理。涉及策略发现算法（5495、7835）与 PSL 使用（6729）的勘误通过 DNS Tree Walk 重新设计彻底清除。

## 八、对中国邮件系统的影响

- **国内主流邮件系统仍基于 RFC 7489 实现**，尚未完全适配 DNS Tree Walk；过渡期内可能继续依赖 PSL 判定组织域。
- 使用新增标签（np/psd/t）的域名所有者可先行部署——接收方对不认识的标签按 RFC 7489 规则忽略，无兼容风险。
- 已移除标签（pct/rf/ri）失去效用，**新部署不应再使用**；存量记录中的 pct 由接收方按 Appendix A.6 语义处理。
- 等保/关基合规单位应修订安全基线：确认 p=reject 适用性（Section 7.4），验证 DNS 基础设施对深层子域 TXT 查询的支持，关注供应商 RFC 9989 适配时间表。

## 九、总结

RFC 9989/9990/9991 标志着 DMARC 从「社区实践描述」（Informational）正式升级为 IETF 互联网标准（Standards Track）。核心变化可概括为：**一套发现机制（DNS Tree Walk）、两个新语义标签（np/psd）、一个测试标签（t）、三标签移除（pct/rf/ri）、报告体系拆分（9990/9991）**。对已部署 DMARC 的域名，DNS 记录通常无需紧急修改；对新建部署，应直接按 RFC 9989 语义配置。

## 参考文献

1. RFC 9989 — Domain-Based Message Authentication, Reporting, and Conformance (DMARC)，IETF，2026-05，Standards Track，Obsoletes 7489, 9091。Section 4.10（DNS Tree Walk）、Section 4.7（标签格式）、Section 7.4（互操作性）、Appendix A.6（pct 移除）、Appendix C（变更对照）。https://www.rfc-editor.org/rfc/rfc9989
2. RFC 9990 — DMARC Aggregate Reporting，IETF，2026-05，Standards Track，Obsoletes 7489。https://www.rfc-editor.org/rfc/rfc9990
3. RFC 9991 — DMARC Failure Reporting，IETF，2026-05，Standards Track，Obsoletes 7489，Updates 6591。https://www.rfc-editor.org/rfc/rfc9991
4. RFC 7489 — Domain-Based Message Authentication, Reporting, and Conformance (DMARC)，IETF，2015-03，Informational（已废弃）。https://www.rfc-editor.org/rfc/rfc7489
5. RFC 9091 — DMARC Extension for Public Suffix Domains，IETF，2021-07，Experimental（已废弃）。https://www.rfc-editor.org/rfc/rfc9091
6. RFC 8020 — NXDOMAIN：There Really Is Nothing Underneath，IETF，2016-10（np 标签的 NXDOMAIN 定义依据）。https://www.rfc-editor.org/rfc/rfc8020

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-standards-evolution.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
