---
title: "DMARC 标准演进 — RFC 7489 → RFC 9989/9990/9991：Tree Walk 算法弃用与聚合报告格式重构 · ztpop 邮件技术知识库"
source: "https://ztpop.net/kb/dmarc-standards-evolution.html"
license: CC-BY 4.0
---

# DMARC 标准演进 — RFC 7489 → RFC 9989/9990/9991：Tree Walk 算法弃用与聚合报告格式重构 · ztpop 邮件技术知识库

DMARC 标准演进 — RFC 7489 → RFC 9989/9990/9991：Tree Walk 算法弃用与聚合报告格式重构

## 摘要

2025 年 3 月，IETF 发布了 RF 9989、RFC 9990 和 RFC 9991 三份新标准，正式取代 2015 年发布的 RFC 7489。这是 DMARC 协议自诞生以来最大规模的标准重构——原有的单一 RFC 7489 被拆分为基础规范（RFC 9989）、聚合报告（RFC 9990）和失败报告（RFC 9991）三个独立文档，RFC 7489 被标记为 Historic（已废止）。本次修订的核心变化包括：Tree Walk 子域策略继承算法被正式弃用（§9.4 of RFC 9989 明确禁止接收方继续使用 Tree Walk）、Identifier Alignment 规则得到精化、聚合报告 XML Schema 进行了面向简化的大幅重构、ruf 失败报告机制得到增强。本文编译三份新 RFC 的关键变更点，提供旧-新规范逐项对比表，并给出从 RFC 7489 DMARC 部署迁移到新标准的实践路线。

## 1. 背景：为什么 RFC 7489 需要被取代

RFC 7489 发布于 2015 年 3 月（DOI: 10.17487/RFC7489），在随后的十年间被全球数百万个域名采纳为邮件认证的最后一公里。根据 Google 的 Transparency Report 数据，截至 2024 年 12 月，全球 280 亿封入站邮件中超过 80% 的发件域已发布了 DMARC 记录。然而这一大规模部署过程也暴露了 RFC 7489 原始设计中的若干结构性缺陷：

1. **Tree Walk 算法的安全与性能隐患**
   ：RFC 7489 §6.6.3 定义的子域策略继承机制（即从
   `_dmarc.subdomain.example.com`
   →
   `_dmarc.example.com`
   →
   `_dmarc.com`
   逐级向上遍历 DNS 的 Tree Walk）被多个接收方 MTA 运营方报告为攻击面——攻击者可以在
   `_dmarc.com`
   注册一个 DMARC 记录，影响所有未显式发布 DMARC 策略的 .com 域的子域。此外 Tree Walk 在深层子域（如
   `a.b.c.d.example.com`
   ）场景下带来了不可预测的 DNS 查询延迟。
2. **聚合报告 XML 过于冗长**
   ：RFC 7489 Appendix C 定义的 XML Schema 包含了大量历史遗留字段，导致中等流量域每天接收的 rua 报告聚合压缩后仍有数 GB 总量。这对小型域造成了不成比例的存储和解析负担。
3. **ruf 隐私风险未充分收敛**
   ：RFC 7489 §7.3 对 ruf 失败报告中的 PII（个人身份信息）去敏化要求措辞较弱，导致在实际使用中部分接收方 MTA 在 ruf 报告中包含了原始邮件主题甚至正文部分。
4. **与 ARC（RFC 8617）和 BIMI（RFC 8617 之后）等后续协议缺乏互操作性规范**
   。

RFC 9989/9990/9991 即是 IETF DMARC Working Group 在上述运营经验教训基础上的全面修订。三份新 RFC 于 2025 年 3 月以 Proposed Standard 状态发布，RFC 7489 同日被标记为 Historic。

## 2. RFC 9989：DMARC 基础规范

RFC 9989
*Domain-based Message Authentication, Reporting, and Conformance (DMARC)*
是新的核心规范，对应旧 RFC 7489 中除聚合报告和失败报告外的全部内容。

### 2.1 Tree Walk 算法正式弃用（§9.4）

RFC 9989 §9.4 明确要求：
**接收方在查询
`_dmarc.`
未获得 DNS 响应时，不得向上遍历父域（即不得进行 Tree Walk）**
。子域策略继承的唯一合法机制改为：

* **主域
  `sp=`
  标签**
  ：主域在其 DMARC 记录中通过
  `sp=`
  标签为直接子域指定默认策略。这仍然是 RFC 9989 中定义的子域策略继承机制。
* **子域显式覆写**
  ：子域可以通过发布自己的
  `_dmarc..example.com`
  记录来覆写主域的
  `sp=`
  。

```
# RFC 7489 (旧): DNS Tree Walk
# 查询 _dmarc.a.b.example.com → 未找到
#   → 尝试 _dmarc.b.example.com → 未找到
#     → 尝试 _dmarc.example.com → 找到！使用其记录
# ❌ RFC 9989 不再允许此行为

# RFC 9989 (新): 仅两层
# 查询 _dmarc.a.b.example.com → 未找到
#   → 仅使用 example.com 的 sp= 标签（如果子域与主域共享组织域）
#   → 若无 sp= 标签且 DNS 查询未返回结果，DMARC 不介入
```

### 2.2 Identifier Alignment 精化（§6.2–§6.4）

RFC 9989 对 Identifier Alignment 规则进行了精化：

* **组织域定义更严格**
  ：引入 Public Suffix List（PSL）作为组织域判断的参考依据，消除不同实现对 "example.co.uk" 类域名的组织域判断差异。
* **aspf=r 的匹配语义澄清**
  ：明确 Relaxed SPF Alignment 在 SPF 验证结果为
  `pass`
  且
  `Authserv-ID`
  为 MAIL FROM 域时，对齐判据是
  `RFC5321.MailFrom`
  的组织域与
  `RFC5322.From`
  的组织域匹配。
* **空 MAIL FROM 的处理**
  ：当 SPF 验证的 MAIL FROM 为
  `<>`
  （空信封，通常用于退信 DSN）时，SPF 对齐应基于 HELO 域进行判断（§6.2.2）。

### 2.3 DMARC TXT 记录语法变更

RFC 9989 §7.3 保留了 tag-value 语法框架但做了若干微调：

2.3 DMARC TXT 记录语法变更

| Tag | RFC 7489 | RFC 9989 | 变更说明 |
| --- | --- | --- | --- |
| `v` | DMARC1 | DMARC1（不变） | — |
| `p` | none / quarantine / reject | 同左 | — |
| `sp` | none / quarantine / reject | 同左 + 新增 `none` 默认行为澄清 | 明确无 sp= 时子域默认继承 p= 策略 |
| `pct` | 1–100 | 同左 | §7.4 新增"pct 应用粒度为 per-session"的规范性语言 |
| `rua` | mailto: URI 列表 | 同左 | §7.5 新增 rua URI 的最大推荐长度（512 字节） |
| `ruf` | mailto: URI 列表 | **不再建议使用** | RFC 9991 接管失败报告定义，RFC 9989 §7.6 请读者参见 RFC 9991 |
| `fo` | 0/1/d/s（冒号分隔） | 移入 RFC 9991 | RFC 9989 不再定义 fo 标签 |
| `adkim` | r / s | r / s（不变） | — |
| `aspf` | r / s | r / s（不变） | — |
| `rf` | afrf / iodef | 移入 RFC 9991 | — |
| `ri` | 秒（默认 86400） | 同左 | — |
| `np` | 不存在 | **新增** | Notification Policy——发件域对 ruf 报告中包含非公开信息的许可策略 |

## 3. RFC 9990：DMARC 聚合报告

RFC 9990
*DMARC Aggregate Reporting*
将原 RFC 7489 §7.1、§7.2 及 Appendix C 的内容提取为独立文档，并进行了大幅重构。

### 3.1 聚合报告 XML Schema 重构

新 Schema 的主要变化：

* **删除
  `extra_contact_info`
  字段**
  （原
  `/feedback/report_metadata/extra_contact_info`
  ）。该字段在 RFC 7489 时代几乎无人使用且常包含过期 URL。
* **`policy_published`
  中删除
  `fo`
  、
  `rf`
  、
  `ri`**
  ——这些标签移至 RFC 9991 管理，不再出现在聚合报告的策略回显中。
* **新增
  `np`
  字段**
  到
  `policy_published`
  中，回显发件域的 Notification Policy 设置。
* **`policy_evaluated`
  中新增
  `reason`
  数组**
  ——当 disposition 为 fail 时，报告生成方可以附加 DMARC 失败的根因说明（如
  `dkim-alignment-failed`
  、
  `spf-alignment-failed`
  、
  `both-failed`
  ），帮助域管理员快速定位。
* **`auth_results`
  重构**
  ：将原 RFC 7489 中扁平化的
  `dkim`
  /
  `spf`
  子元素扩展为支持多签名和多认证结果的数组型结构。

```
  reject
  fail
  fail
  
    dkim-alignment-failed
    DKIM d=esp.example does not align with header_from=example.com
  
  
    spf-alignment-failed
    SPF auth domain mail.esp.example != example.com
```

### 3.2 报告压缩与传输优化

RFC 9990 §5.2 新增了针对大流量域的传输优化建议：(1) 报告分片：单个报告文件超过 10 MB 时应拆分为多个部分，通过
`Content-Type: multipart/mixed`
合并发送；(2) 差分报告：报告生成方可以选择只包含与前一日报告相比发生变化的 record 行（通过
`/feedback/record/row/diff`
标记），减少重复数据的传输。

## 4. RFC 9991：DMARC 失败报告

RFC 9991
*DMARC Failure Reporting*
是 ruf 失败报告（Forensic Report / Failure Report）的独立规范。

### 4.1 fo= 标签语法保留但语义精化

RFC 9991 §4.3 保留了
`fo=`
标签的四个值（0/1/d/s），但新增了以下语义约束：

* `fo=0`
  （默认）不再是"仅在所有机制均未产生 pass 时报告"，改为"在 DMARC 策略判定为 fail 时报告"，即消除了原 RFC 7489 中 fo=0 的歧义——原来的措辞可能被解读为"SPF 和 DKIM 都必须产生 fail"。
* `fo=1`
  的触发次数被限制在每域每日 10,000 封（建议值），以防止大型接收方对小型发件域造成 ruf 洪水。

### 4.2 隐私保护增强（§6）

RFC 9991 §6 纳入了 GDPR 时代的隐私考量：

1. **强制去敏化**
   ：ruf 报告中不得包含原始邮件正文（message body），仅可包含原始邮件的部分头部字段（From、To、Date、Subject、Message-ID）。Subject 行中的个人数据（如姓名）应使用
   替换。
2. **`np=`
   标签**
   ：发件域在 DMARC 记录中新增
   `np=`
   （Notification Policy）标签，声明是否允许接收方在 ruf 报告中包含非公开信息（如邮件主题中的特定业务数据）。
   `np=standard`
   表示遵守 RFC 9991 的默认去敏化规则；
   `np=restrictive`
   表示请求接收方最大程度去敏化（连 Subject 字段也应去除）。
3. **接收方 ruf 报告生成频率限制**
   ：每个
   `sending-mta-ip + domain`
   组合每天最多发送 100 封 ruf 报告。

## 5. 新旧规范对比总表

5. 新旧规范对比总表

| 特性 | RFC 7489 (2015, Historic) | RFC 9989–9991 (2025, Proposed Standard) |
| --- | --- | --- |
| 文档结构 | 单一 RFC（78 页） | 三份独立 RFC（基础规范 9989、聚合报告 9990、失败报告 9991） |
| 子域策略继承 | DNS Tree Walk（向上遍历） | 仅两层：主域 sp= 标签 + 子域显式覆写。Tree Walk 已弃用 |
| 组织域判断 | 依赖实现自行判断 | 引用 Public Suffix List 标准化 |
| 空 MAIL FROM 对齐 | 措辞模糊 | 明确基于 HELO 域进行对齐判断（RFC 9989 §6.2.2） |
| 聚合报告 XML | 单一扁平 Schema | 重构 Schema — 删除 extra\_contact\_info，新增 reason 数组，auth\_results 支持多签名 |
| ruf 报告 | RFC 7489 §7.3 在正文内 | 独立 RFC 9991，强制性去敏化，np= 标签，频率限制 |
| fo= 标签 | 在 RFC 7489 §6.3 | 在 RFC 9991 §4.3，fo=0 语义修正 |
| 新增 DNS 标签 | — | np= Notification Policy（RFC 9991 §4.4） |
| 报告压缩 | gzip 建议 | gzip 建议 + 分片传输（>10MB 拆片）、差分报告选项（RFC 9990 §5.2） |
| ARC 互操作 | 未提及 | 新增 ARC 互操作章节（RFC 9989 §10.3），明确 ARC 验证结果如何与 DMARC 评估衔接 |

## 6. 对现有 DMARC 部署的迁移影响

### 6.1 不需要修改 DNS 记录的内容

大多数已部署 DMARC 的域名无需针对 RFC 9989 迁移修改 DNS TXT 记录。以下配置在两个版本下均可正常工作：

```
"v=DMARC1; p=reject; sp=reject; pct=100; adkim=s; aspf=r; rua=mailto:dmarc@example.com"
```

`fo=`
和
`rf=`
标签在 RFC 9989 记录中仍然被允许出现（接收方应将它们视为定向到 RFC 9991 的参考），但在 DNS 记录中继续包含它们不会导致错误。

### 6.2 可选的新增配置

如果希望利用 RFC 9991 的隐私保护增强，可新增
`np=`
标签：

```
# 标准隐私保护（推荐）
"v=DMARC1; p=reject; rua=mailto:dmarc@example.com; np=standard"

# 最大程度去敏化（高隐私需求场景）
"v=DMARC1; p=reject; rua=mailto:dmarc@example.com; np=restrictive"
```

### 6.3 MTA 软件更新需求

接收方 MTA 软件（Postfix 的 OpenDMARC milter、Microsoft Exchange Online Protection、Google Workspace 等）需要实现 RFC 9989–9991 的新行为：

* 停止 Tree Walk 子域策略继承（§9.4）；
* 采用 PSL 进行组织域判断；
* 在聚合报告中输出
  `reason`
  数组；
* 实施 ruf 报告的强制性去敏化和频率限制。

对于自建邮件系统的管理员，这意味着需要将 OpenDMARC 从 1.4.x 升级至未来的 2.x 版本（当前截至 2026 年 7 月，OpenDMARC 2.0 仍在开发中，预计支持 RFC 9989–9991 的版本为 2.0+）。在过渡期间，RFC 9989 §13 定义了向后兼容性条款：旧版接收方（只理解 RFC 7489）的 DMARC 评估结果在新标准下仍然被接受为合法，但新标准的增强特性（如 reason 数组、np= 标签）可能不被识别。

### 6.4 聚合报告解析器的更新

使用 parsedmarc 或自研报告解析器的管理员需要适配：

* 新 Schema 中
  `policy_evaluated`
  新增的
  `reason`
  数组字段；
* `policy_published`
  中不再存在的
  `fo`
  、
  `rf`
  、
  `ri`
  字段（向后兼容处理——若缺失则置默认值）；
* `auth_results`
  中结构变化（单值 vs 数组）。

```
#!/usr/bin/env python3
"""
dmarc-rfc9990-parser.py — 兼容 RFC 7489 与 RFC 9990 双 Schema 的报告解析器
"""
import json
from xml.etree import ElementTree as ET

NS = {"f": "urn:ietf:params:xml:ns:dmarc:1.0"}

def safe_find_text(element, xpath, default=""):
    """安全提取 XML 文本——兼容双 Schema"""
    result = element.find(xpath, NS)
    return result.text if result is not None and result.text else default

def parse_auth_results(record, ns):
    """解析 auth_results，兼容 RFC 7489（单值）和 RFC 9990（数组）"""
    auth = record.find("f:auth_results", ns)
    if auth is None:
        return []
    results = []
    # RFC 9990 式：多 spf/dkim 子元素
    for spf_elem in auth.findall("f:spf", ns):
        results.append({
            "mechanism": "spf",
            "domain": safe_find_text(spf_elem, "f:domain"),
            "result": safe_find_text(spf_elem, "f:result"),
            "scope": safe_find_text(spf_elem, "f:scope", "mfrom")
        })
    for dkim_elem in auth.findall("f:dkim", ns):
        results.append({
            "mechanism": "dkim",
            "domain": safe_find_text(dkim_elem, "f:domain"),
            "result": safe_find_text(dkim_elem, "f:result"),
            "selector": safe_find_text(dkim_elem, "f:selector"),
            "human_result": safe_find_text(dkim_elem, "f:human_result", "")
        })
    return results

def parse_reasons(pe, ns):
    """解析 policy_evaluated 中的 reason 数组（RFC 9990 新增）"""
    reasons = []
    for reason_elem in pe.findall("f:reason", ns):
        reasons.append({
            "type": safe_find_text(reason_elem, "f:type"),
            "comment": safe_find_text(reason_elem, "f:comment")
        })
    return reasons

# 使用示例
tree = ET.parse("report.xml")
root = tree.getroot()
metadata_domain = safe_find_text(root, ".//f:policy_published/f:domain")
# 兼容：fo, rf, ri 可能不存在于 RFC 9990 报告中
fo = safe_find_text(root, ".//f:policy_published/f:fo", "0")
rf = safe_find_text(root, ".//f:policy_published/f:rf", "afrf")
ri = safe_find_text(root, ".//f:policy_published/f:ri", "86400")
# RFC 9990 新增 np 字段
np_val = safe_find_text(root, ".//f:policy_published/f:np", "")
print(f"Domain: {metadata_domain}, fo={fo}, np={np_val}")
```

## 7. 迁移路线：从 RFC 7489 到 RFC 9989–9991

7. 迁移路线：从 RFC 7489 到 RFC 9989–9991

| 阶段 | 操作 | 风险 | 时长 |
| --- | --- | --- | --- |
| 1. 认知升级 | 阅读 RFC 9989、9990、9991 全文。理解 Tree Walk 弃用的影响——确认你的域不受第三方 `_dmarc.` 记录的影响 | 无 | 1 天 |
| 2. DNS 记录审查 | 检查 `_dmarc` 记录，确认 `sp=` 标签已正确覆盖所有发送子域。因为 Tree Walk 不再可用，未配置 sp= 的子域将退化为无 DMARC 保护 | 中——未覆盖的子域将失去 DMARC 保护 | 1–2 天 |
| 3. 报告解析器更新 | 更新 DMARC 聚合报告解析器以兼容 RFC 9990 新 Schema（reason 数组、auth\_results 结构变化） | 低 | 2–5 天 |
| 4. MTA 软件升级 | 确认 Postfix/Dovecot/OpenDMARC 版本支持 RFC 9989（或至少与其兼容） | 中——升级前在测试环境验证 | 视情况而定 |
| 5. np= 标签添加（可选） | 根据隐私需求在 DMARC 记录中添加 `np=standard` 或 `np=restrictive` | 低 | 几分钟 |

昆仑邮件系统在主动推送 DMARC 最佳实践的客户运维中已将上述迁移路线纳入了季度安全审查流程——通过审查客户 DNS 记录中的
`sp=`
覆盖率和
`_dmarc.`
显式配置来确保在 Tree Walk 弃用后所有发送子域持续获得 DMARC 保护。

### 参考文献

1. RFC 9989 — Domain-based Message Authentication, Reporting, and Conformance (DMARC) (IETF, March 2025). Proposed Standard. 第 6 节 Identifier Alignment（组织域定义、空 MAIL FROM 处理），第 7 节 DMARC TXT Record Tags，第 9.4 节 Tree Walk Deprecation，第 10.3 节 ARC Interoperability，第 13 节 Backward Compatibility.
2. RFC 9990 — DMARC Aggregate Reporting (IETF, March 2025). Proposed Standard. 第 4 节 Aggregate Report XML Schema（reason 数组、auth\_results 重构），第 5.2 节 Report Transmission Optimization（分片与差分报告）.
3. RFC 9991 — DMARC Failure Reporting (IETF, March 2025). Proposed Standard. 第 4.3 节 fo= Tag Semantics，第 4.4 节 np= Notification Policy Tag，第 6 节 Privacy Considerations（强制去敏化、频率限制）.
4. RFC 7489 — Domain-based Message Authentication, Reporting, and Conformance (DMARC) (IETF, March 2015).
   **Historic**
   . 原 DMARC 基础规范，已被 RFC 9989/9990/9991 废止.
5. RFC 8617 — Authenticated Received Chain (ARC) Protocol (IETF, July 2019). 第 5 节 ARC Set 生成与验证流程，弥补 DMARC 在邮件列表转发场景下的覆盖缺口.
6. GB/T 30283-2020 — 信息安全技术 电子邮件系统安全技术要求（修订版）. 第 5.2 节 邮件认证机制，引用 DMARC 为邮件反欺诈的核心技术标准.
7. NIST SP 800-177 Rev.1 — Trustworthy Email (NIST, February 2019). 第 4 节 Email Authentication，将 DMARC 列为可信邮件生态系统的强制性认证层.
8. Google Transparency Report — HTTPS & Email Encryption,
   <https://transparencyreport.google.com/>
   . DMARC 采纳率的全球趋势数据.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-standards-evolution.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
