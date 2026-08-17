---
title: "DMARC 聚合报告详解：RFC 9990 中文解读"
source: "https://ztpop.net/kb/dmarcbis-rfc9990-aggregate-reporting.html"
license: CC-BY 4.0
---

# DMARC 聚合报告详解：RFC 9990 中文解读

# DMARC 聚合报告详解：RFC 9990 中文解读

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤

RFC 9990 / DMARCbis / DMARC 聚合报告

2026-07-29 · ztpop.net 邮件技术知识库

## 1. RFC 9990 的背景与定位

在 DMARCbis（RFC 9989）的体系重构中，IETF 将 DMARC 协议域与反馈报告层进行了清晰的分离。RFC 9989 定义了 DMARC 的核心协议——策略发现、身份对齐、域名所有者评估策略；而**RFC 9990**（Domain-Based Message Authentication, Reporting, and Conformance (DMARC) Aggregate Reporting）则独立规范了**聚合报告（Aggregate Report）**的格式定义、传输机制与处理逻辑。

这一分离的用意在于：聚合报告的格式和技术要求相对稳定且可独立演进。RFC 7489 将核心协议与报告格式写在同一个文档中，导致协议更新时报告部分的任何变更都需要重新发布整份 RFC。DMARCbis 工作组采用三文档架构（RFC 9989 核心协议、RFC 9990 聚合报告、RFC 9991 失败报告），使得各组件可以独立维护和迭代。

RFC 9990 由 Alex Brotman（Comcast, Inc.）编辑，于 2026 年 5 月作为 Standards Track 文档发布，同时废弃并替代了 RFC 7489 中关于聚合报告的全部内容。RFC 9990 的核心作用是为域名所有者（Domain Owner）提供一种标准化的、机器可读的反馈机制，使其能够了解邮件接收方（Mail Receiver）在 DMARC 策略层面上的处理结果。

**核心定位**：RFC 9990 提供了"可见性"。域名所有者通过聚合报告获得以下三类信息：  
(1) 认证结果 —— SPF 和 DKIM 验证结果以及对齐状态；  
(2) 需要域名所有者采取的纠正措施 —— 哪些邮件流未通过认证；  
(3) 域名所有者策略的影响 —— 接收方实际应用了何种处置。

## 2. 聚合报告格式（XML Schema）

RFC 9990 的核心产出物是用 XML 表示的聚合反馈报告。该报告的格式由附录 A 中的 XML Schema Definition（XSD）严格定义。一个符合规范的 XML 报告以 `<feedback>` 为根元素，命名空间为 DMARC 命名空间。

以下按 XML 层次结构逐层解析报告的结构。

### 2.1 根元素与第一层结构

根元素 `feedback` 包含以下五个子元素（必须按此顺序出现）：

| 元素名称 | 出现次数 | 内容说明 |
| --- | --- | --- |
| version | 可选（O） | 版本标识，必须为 "1.0" |
| report\_metadata | 必选（R） | 报告生成方元数据 |
| policy\_published | 必选（R） | 接收方观察到的 DMARC 策略配置 |
| extension | 可选（O） | 未来扩展点，元素必须带命名空间 |
| record | 至少一个（+） | 报告记录，每条记录对应一个 IP 地址 |

每份报告**必须**至少包含一个 `record` 元素，并且**必须**仅包含一个 DMARC Policy Domain 的数据。也就是说，报告是以"策略域"为单位生成的——如果在报告期内邮件接收方遇到了 example.com、foo.example.com、bar.example.com 三个域，且它们的策略配置不同，则需要生成多份独立的报告。

### 2.2 报告元数据（report\_metadata）

该元素包含报告生成方的身份信息和报告周期描述：

| 元素名称 | 出现次数 | 内容说明 |
| --- | --- | --- |
| org\_name | 必选（R） | 报告生成组织名称 |
| email | 必选（R） | 报告生成组织联系邮箱 |
| extra\_contact\_info | 可选（O） | 额外联系信息（支持 lang 属性） |
| report\_id | 必选（R） | 报告唯一标识符 |
| date\_range | 必选（R） | 报告覆盖的时间范围 |
| error | 可选（O） | 处理 DMARC 策略记录时遇到的错误信息 |
| generator | 可选（O） | 报告生成器的名称和版本号 |

`date_range` 元素包含 `begin` 和 `end` 两个子元素，值为自纪元（epoch）以来的秒数（UTC 时间），用以标识报告周期。典型的报告周期覆盖一个 UTC 自然日（0000 到 2359 UTC），报告周期的范围在连续的报告之间不应重叠。

### 2.3 已发布策略（policy\_published）

该元素反映接收方在评估期内发现的 DMARC 策略记录的实际内容：

| 元素名称 | 出现次数 | 内容说明 |
| --- | --- | --- |
| domain | 必选（R） | DMARC Policy Domain |
| discovery\_method | 可选（O） | 策略发现方法："psl" 或 "treewalk" |
| p | 必选（R） | 域名所有者评估策略（none / quarantine / reject） |
| sp | 可选（O） | 子域策略 |
| np | 可选（O） | 不存在的子域策略 |
| fo | 可选（O） | 失败报告选项（对应 RFC 9991） |
| adkim | 可选（O） | DKIM 对齐模式（r / s） |
| aspf | 可选（O） | SPF 对齐模式（r / s） |
| testing | 可选（O） | 测试模式标志（t 标签值 y / n） |

RFC 9990 新增了 `discovery_method` 和 `testing` 元素，这是与 RFC 9989（DNS Tree Walk、t 标签）紧密配合的体现。其中 `discovery_method` 的值 "psl" 对应 RFC 7489 的 PSL 方法，"treewalk" 对应 RFC 9989 的 DNS Tree Walk 方法。

### 2.4 记录数据（record）

每个 `record` 元素描述一个特定 IP 地址发来的邮件在接收端经历的认证处理结果。一个 `record` 包含三个必选子元素：

#### 2.4.1 row：连接端详情

| 元素名称 | 出现次数 | 内容说明 |
| --- | --- | --- |
| source\_ip | 必选（R） | 连接方 IP 地址（IPv4 或 IPv6） |
| count | 必选（R） | 接收到的邮件数量 |
| policy\_evaluated | 必选（R） | 实际应用的处置结果 |

`policy_evaluated` 包含以下子元素：

| 元素名称 | 出现次数 | 内容说明 |
| --- | --- | --- |
| disposition | 必选（R） | 实际处置结果（none / quarantine / reject） |
| dkim | 必选（R） | DKIM 对齐测试结果（pass / fail） |
| spf | 必选（R） | SPF 对齐测试结果（pass / fail） |
| reason | 0 或多个（\*） | 策略覆盖原因（如本地策略覆盖） |

注意：`dkim` 和 `spf` 在这里的值是**经过 DMARC 对齐测试后的结果**，而非原始的 SPF/DKIM 验证结果。原始验证结果在 `auth_results` 中另行报告。

#### 2.4.2 identifiers：标识符

| 元素名称 | 出现次数 | 内容说明 |
| --- | --- | --- |
| header\_from | 必选（R） | RFC5322.From 头部中的域名 |
| envelope\_from | 可选（O） | RFC5321.MailFrom 域（SPF 校验的源） |
| envelope\_to | 可选（O） | RFC5321.RcptTo 域 |

#### 2.4.3 auth\_results：认证结果

该元素包含 DKIM 和 SPF 的**原始验证结果**（未经 DMARC 对齐判断）：

**DKIM 认证结果：**

| 元素名称 | 出现次数 | 内容说明 |
| --- | --- | --- |
| domain | 必选（R） | 验证使用的域（签名中的 d= 标签） |
| selector | 必选（R） | 验证使用的选择器（签名中的 s= 标签） |
| result | 必选（R） | DKIM 验证结果（RFC 8601 定义的值） |
| human\_result | 可选（O） | 供人阅读的详细描述 |

**SPF 认证结果：**

| 元素名称 | 出现次数 | 内容说明 |
| --- | --- | --- |
| domain | 必选（R） | 验证使用的域 |
| scope | 可选（O） | 域来源（唯一有效值：mfrom） |
| result | 必选（R） | SPF 验证结果（RFC 8601 定义的值） |
| human\_result | 可选（O） | 供人阅读的详细描述 |

### 2.5 策略覆盖原因（reason 元素）

当接收方基于本地策略覆盖了域名所有者的 DMARC 策略时，`reason` 元素记录了覆盖的原因类型和说明文本。预定义的覆盖类型包括本地策略覆盖（forwarded、sampling\_outside、trusted\_forwarder 等），具体枚举值定义在 RFC 9990 Section 3.1.6。

### 2.6 样本报告

以下是一个简化的聚合报告 XML 示例（基于 RFC 9990 Appendix B）：

```
<?xml version="1.0" encoding="UTF-8"?>
<feedback xmlns="urn:ietf:params:xml:ns:dmarc">
  <report_metadata>
    <org_name>Example Receiver</org_name>
    <email>dmarc-report@receiver.example</email>
    <report_id>2024-01-01T00:00:00Z_example.com</report_id>
    <date_range>
      <begin>1704067200</begin>
      <end>1704153599</end>
    </date_range>
  </report_metadata>
  <policy_published>
    <domain>example.com</domain>
    <discovery_method>treewalk</discovery_method>
    <p>reject</p>
    <sp>reject</sp>
    <adkim>r</adkim>
    <aspf>r</aspf>
  </policy_published>
  <record>
    <row>
      <source_ip>192.0.2.1</source_ip>
      <count>10</count>
      <policy_evaluated>
        <disposition>none</disposition>
        <dkim>pass</dkim>
        <spf>pass</spf>
      </policy_evaluated>
    </row>
    <identifiers>
      <header_from>example.com</header_from>
      <envelope_from>mail.example.com</envelope_from>
    </identifiers>
    <auth_results>
      <dkim>
        <domain>example.com</domain>
        <selector>2024dkim</selector>
        <result>pass</result>
      </dkim>
      <spf>
        <domain>mail.example.com</domain>
        <scope>mfrom</scope>
        <result>pass</result>
      </spf>
    </auth_results>
  </record>
</feedback>
```

## 3. 报告传输机制

### 3.1 基于电子邮件的传输

RFC 9990 Section 3.5.2 规定，聚合报告主要通过电子邮件传输。域名所有者通过在 DMARC DNS 记录中使用 `rua`（Report URI for Aggregate reports）标签指定报告目标邮箱地址，语法为 `mailto:user@domain`。支持指定多个接收地址（以逗号分隔），RFC 9990 明确要求报告应发送到列表中的**每一个** URI。

报告电子邮件本身使用 MIME 封装：

* Content-Type 应为 `application/xml` 或 `text/xml`，也可以使用 `application/gzip`（压缩后的 XML）
* 建议使用 `.xml` 或 `.xml.gz` 扩展名
* 文件名应包含易于识别的信息，如报告域和生成时间

### 3.2 DKIM 签名要求

为了保证报告的真实性和完整性，RFC 9990 Section 3.1.3 明确规定：**发送聚合报告电子邮件的 MTA 应对报告邮件进行 DKIM 签名**。签名域建议使用接收方自身的外发域。这一要求与 RFC 9989 Section 6.1 中关于"接收方应验证报告来源"的安全建议保持一致。

RFC 9990 同时指出，对于一封邮件中存在多个 DKIM 签名的情况，报告中应包含每个签名域的结果，从而确保域名所有者能够完整了解其域名的认证状况。

### 3.3 Report-ID 定义

每份报告在 `report_metadata` 的 `report_id` 元素中携带一个全局唯一标识符。RFC 9990 Section 3.5.1 规定 Report-ID 必须确保唯一性，以便接收方检测和处理重复报告。典型的实现方式是组合时间戳与发送方域名（如 `2024-01-01T00:00:00Z_example.com`）。

### 3.4 重复报告处理

RFC 9990 Section 3.5.4 指出，报告接收方可能接收到重复的报告（例如因传输故障导致的重新发送）。接收方应通过 Report-ID 检测重复，并对重复报告进行去重处理——只处理第一个有效副本，丢弃后续的重复副本。

## 4. 关键字段详解

### 4.1 域名所有者评估策略（disposition）

RFC 9990 报告中的 `disposition` 字段反映了邮件接收方实际应用的处置动作，而非域名所有者发布的策略。三个有效值：

* **none**：放行邮件至收件箱（通常是 DMARC 验证失败但域名所有者策略为 p=none，或接收方本地策略覆盖）
* **quarantine**：将邮件隔离（如放入垃圾邮件文件夹）
* **reject**：拒绝邮件（拒绝在 SMTP 阶段，邮件未被接收）

### 4.2 标识符（identifiers）

`header_from` 是记录中最重要的标识符，因为它直接对应 DMARC 的 Authorization Domain（RFC5322.From 域）。`envelope_from` 用于 SPF 验证，`envelope_to` 则提供了收件人信息（RFC 9990 将其标记为可选，因为某些接收方可能因隐私原因选择不报告此字段）。

### 4.3 认证结果（auth\_results）分解

RFC 9990 在 `auth_results` 部分明确区分了**原始认证结果**和 **DMARC 对齐结果**：

* `auth_results` 中的 dkim/spf 子元素包含的是原始验证结果（如 DKIM 签名验证的 pass/fail，SPF 的 pass/fail/neutral 等，遵从 RFC 8601 定义）
* `policy_evaluated` 中的 dkim/spf 元素则是经过对齐判断后的结果（pass/fail）——即 SPF 或 DKIM 验证成功且域对齐**同时成立**才为 pass

这种区分使得域名所有者可以迅速判断：认证失败是由于**原始验证失败**（如忘记为某个子域配置 DKIM 签名，或 SPF 记录缺少某个发送 IP），还是由于**对齐失败**（如使用第三方邮件发送服务但域对齐模式不匹配）。

### 4.4 策略发现方法（discovery\_method）

RFC 9990 新增的 `discovery_method` 元素是 RFC 9989 DNS Tree Walk 的重要配套字段。它记录了报告生成方当时使用的策略发现方法，取值为 "psl" 或 "treewalk"。这一字段的引入有助于域名所有者识别接收方使用的是旧方法还是新方法，从而在过渡期内正确诊断问题。

## 5. 报告接收与处理最佳实践

### 5.1 接收方视角

邮件接收方（Mail Receiver）在生产聚合报告时应遵循以下原则：

* **报告频率**：建议每日生成一次，覆盖 UTC 自然日。频率可以更高，但报告周期不应重叠
* **单域单报告**：每份报告必须包含且仅包含一个 DMARC Policy Domain 的数据。如果多个子域应用了不同的策略，需要分别生成报告
* **策略变更处理**：如果在报告周期内域名所有者更改了 DMARC 策略，RFC 9990 Section 3.3 允许接收方选择：(a) 发送多份报告（每份对应一种策略配置），或 (b) 仅在报告中记录周期末的最终配置
* **DKIM 签名字段**：对含有多个 DKIM 签名的邮件，应包含所有签名域的结果，让域名所有者全面了解认证状况
* **数据完整性**：如果报告 XML 不符合规范格式，报告消费者应丢弃该报告（Section 3.1.1）。消费者也可以尝试部分使用其中的数据，但格式有问题的数据可能同样不可靠

### 5.2 域名所有者视角

域名所有者在接收和处理 DMARC 聚合报告时，应关注以下要点：

* **报告验证**：验证报告的 DKIM 签名，确保报告来自可信的邮件接收方。这是 RFC 9989 Section 6.1 的安全要求
* **外部目的地验证**：RFC 9990 Section 4 规定，如果 rua 中的 URI 指向非 DMARC Policy Domain 的外部域，域名所有者必须通过 `<domain>._report._dmarc.<external-domain>` TXT 记录声明授权（"rua=mailto:..."），以防止报告数据泄露给未经授权的第三方
* **数据分析**：对比 `policy_published` 与 `policy_evaluated` 的差异，可以判断哪些邮件流受到了本地策略覆盖
* **IP 地址审计**：通过 `source_ip` 字段识别未知的发送 IP，发现潜在的仿冒或未授权发送行为
* **count 字段**：结合邮件量的**绝对值**和**趋势**进行分析，判断 DMARC 策略变更的效果
* **存储规划**：RFC 9990 Section 9.3 指出，聚合报告可能很大（互联网上每天数 GB），应规划好报告的存储和归档策略

### 5.3 工具与生态系统

目前，多个开源和商业工具支持 DMARC 聚合报告的接收和分析：

* **OpenDMARC**：开源项目，支持 DMARC 验证和聚合报告生成
* **parsedmarc**：Python 工具库，解析 DMARC 聚合报告并支持多种后端输出（Elasticsearch、S3 等）
* **dmarc-report-converter**：将 XML 报告转换为可读格式
* **商业服务**：Dmarcian、Valimail、Agari（如今的 HelpSystems）等提供全托管报告分析平台

## 6. 安全与隐私考量

### 6.1 报告内容被用作攻击向量

RFC 9990 Section 8.1 指出，邮件接收方生成的报告内容可能被恶意利用。报告接收方应对报告文件进行验证，确保 XML 不包含恶意负载。报告分析系统应安全处理 XML（防止 XXE、Billion Laughs 等攻击）。

### 6.2 虚假信息

恶意的邮件接收方可能向域名所有者发送虚假的聚合报告，伪造认证数据或邮件量。RFC 9990 Section 8.2 建议域名所有者验证报告的来源（通过 DKIM 签名），并对异常数据进行交叉验证。

### 6.3 报告泄露

聚合报告本身包含了邮件流量的详细信息（发送 IP、邮件量、认证结果等），如果被未经授权的第三方获取，可能泄露敏感的商业情报。RFC 9990 Section 7.3（Feedback Leakage）和 Section 8.3 对此做了专门讨论。外部目的地验证（Section 4）就是防止报告泄露的关键机制之一——确保报告只能发送到域名所有者明确授权的外部服务商。

### 6.4 隐私考量

聚合报告默认仅包含发送方的 IP 地址和认证结果，不包含收件人个人信息（如邮件内容、收件人邮箱地址等）。可选字段 `envelope_to` 虽然可以包含收件人信息，但 RFC 9990 将其标记为可选，允许接收方因隐私原因不报告此字段。报告接收方在处理聚合报告时，应遵守适用的数据保护法规（如中国的《个人信息保护法》、GDPR 等）。

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarcbis-rfc9990-aggregate-reporting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
