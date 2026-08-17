---
title: "Microsoft 365 DKIM 与 DMARC 官方配置文档中文摘录：记录语法与灰度路径"
source: "https://ztpop.net/kb/vnd-ms-dkim-dmarc-config.html"
license: CC-BY 4.0
---

# Microsoft 365 DKIM 与 DMARC 官方配置文档中文摘录：记录语法与灰度路径

**翻译／摘录披露：**本页为对 Microsoft Set up DKIM / Set up DMARC (Microsoft Learn, Defender for Office 365) 的中文翻译与摘录，原文著作权归该机构所有，内容以人类官方原文为准。
  
原文机构：Microsoft；原文名称：Set up DKIM / Set up DMARC (Microsoft Learn, Defender for Office 365)（《为云域邮件配置 DKIM 签名》与《配置 DMARC 校验 From 地址域》）；原文发布：持续更新；授权状态：© Microsoft。原文受版权保护，本页仅做配置事实（记录语法、参数、步骤）的结构化中译，不复刻原文全文。
  
本页由 AI 承担翻译、摘录与排版工作，**不含任何 AI 原创的技术结论**；每一节均标注其对应的人类原文章节，如与原文有出入，以原文为准。

# Microsoft 365 DKIM 与 DMARC 官方配置文档中文摘录：记录语法与灰度路径

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤来源机构：Microsoft　|　原文：Set up DKIM / Set up DMARC (Microsoft Learn, Defender for Office 365)　|　原文发布：持续更新　|　页面性质：中文翻译与摘录（非原创综述）

本页对 Microsoft Learn 两篇官方配置文档做中文摘录与结构化整理：DKIM 配置文档与 DMARC 配置文档。原文著作权归 Microsoft 所有；本页仅转述 DNS 记录语法、cmdlet 参数、默认值与操作步骤等事实性配置信息，并逐节标注原文章节位置。实际配置一律以官方原文为准。

## 一、DKIM 在 Microsoft 365 中的作用（原文 “Set up DKIM to sign mail from your cloud domain” 概述节）

人类原文来源章节：DKIM 文档 — 概述节

原文说明 DKIM 用于验证由 Microsoft 365 组织发出的邮件，防止在商业邮件诈骗（BEC）、勒索软件与钓鱼攻击中被伪造发件人，其主要目的是验证邮件在传输过程中未被篡改。原文给出的机制要点：

1. 为域生成一对或多对私钥，由源邮件系统对出站邮件的重要部分（如 From、To、Subject 等信头字段以及邮件正文）进行数字签名。
2. 数字签名存放于邮件信头的 `DKIM-Signature` 字段；只要中间系统不修改被签名部分，签名即保持有效。签名域由该字段中的 `d=` 值标识。
3. 对应公钥发布在签名域的 DNS 记录中：Microsoft 365 使用 CNAME 记录，其他系统可能使用 TXT 记录。
4. 目标邮件系统按 `d=` 值查找公钥并验证签名。

**原文强调的两条重要事实：**DKIM 签名域不要求与邮件的 MAIL FROM 或 From 地址域一致；同一封邮件可被不同域多次 DKIM 签名（例如服务方域加客户域）。

**按域类型的差异：**仅使用 `*.onmicrosoft.com` 域时，出站邮件自动 DKIM 签名、无需操作；使用自定义域（如 contoso.com）时默认**不做** DKIM 签名，需手动配置。原文并指出仅有 DKIM 并不足够，还需配置 SPF 与 DMARC。

## 二、DKIM CNAME 记录语法与选择器（原文 “Syntax for DKIM CNAME records”）

人类原文来源章节：DKIM 文档 — Syntax for DKIM CNAME records

原文说明：为自定义域启用 DKIM 时会生成**两**对公私钥；私钥不可访问，两条 CNAME 分别指向对应公钥，即所谓「选择器（selector）」。同一时间仅一个选择器处于活跃状态，另一个保留供后续密钥轮换。选择器信息位于 `DKIM-Signature` 信头的 `s=` 值（例如 `s=selector1-contoso-com`）。

原文给出的基础语法（原文注明仅作示例，实际值须从 Defender 门户或 PowerShell 获取）：

```
Hostname: selector1._domainkey
Points to address or value: selector1-<CustomDomainWithDashes>._domainkey.<InitialDomainPrefix>.<DynamicPartitionCharacter>-v1.dkim.mail.microsoft

Hostname: selector2._domainkey
Points to address or value: selector2-<CustomDomainWithDashes>._domainkey.<InitialDomainPrefix>.<DynamicPartitionCharacter>-v1.dkim.mail.microsoft
```

* `<CustomDomainWithDashes>`：自定义域中的点改为短横线（contoso.com → contoso-com）。
* `<InitialDomainPrefix>`：注册时使用的 `.onmicrosoft.com` 前缀（如 contoso）。
* `<DynamicPartitionCharacter>`：由 Microsoft 自动分配的动态字符（例如 r 或 n）。原文说明自 2025 年 5 月起新增自定义域采用该新格式；此前的域沿用旧格式，形如 `selector1-contoso-com._domainkey.contoso.onmicrosoft.com`。

原文提示：同一租户下不同自定义域可能被分配到不同的动态分区字符，需按门户／PowerShell 实际输出逐域抄录，不可推测。

## 三、启用 DKIM 的两条路径与密钥参数（原文配置与轮换节）

人类原文来源章节：DKIM 文档 — Configure DKIM signing… / Rotate DKIM keys

### 3.1 Defender 门户路径

1. 确认自定义域已加入 Microsoft 365，且在 DKIM 选项卡中状态为 `NoDKIMKeys`、开关为 Disabled。
2. 进入 Defender 门户 → Email & collaboration → Policies & rules → Threat policies → Email authentication settings，选择 **DKIM** 选项卡。
3. 尝试将该域开关滑至 Enabled，弹出的对话框会显示所需 CNAME 值，确认后状态变为 `CnameMissing`。
4. 在域详情浮出面板的 **Publish CNAMEs** 中复制两条 CNAME 值，到域名注册商处创建这两条 CNAME 记录。
5. 返回面板开启「Sign messages for this domain with DKIM signatures」；记录被检测到后状态变为已签名。

### 3.2 Exchange Online PowerShell 路径

1. `Get-DkimSigningConfig` 查看域状态。
2. 若域未列出：`New-DkimSigningConfig -DomainName <Domain> -Enabled $false`（可附 `-KeySize` 等参数）。
3. 复制输出中的 `Selector1CNAME` 与 `Selector2CNAME`，到注册商创建 CNAME。
4. 检测通过后执行 `Set-DkimSigningConfig -Identity <Domain> -Enabled $true`。
5. 再次 `Get-DkimSigningConfig` 确认 `Enabled: True` 且 `Status: Valid`。

### 3.3 密钥长度与规范化参数

* `New-DkimSigningConfig` 的 `-KeySize`：可取 **1024（默认）** 或 **2048**。
* `-BodyCanonicalization` / `-HeaderCanonicalization`：可取 `Relaxed`（默认）或 `Simple`。

### 3.4 密钥轮换（原文 Rotate DKIM keys）

* 原文明确：**轮换并非立即生效，新私钥需 4 天（96 小时）后才开始签名**，在此之前仍使用旧密钥。
* 相关属性（`Get-DkimSigningConfig -Identity <CustomDomain> | Format-List`）：`KeyCreationTime`、`RotateOnDate`、`SelectorBeforeRotateOnDate`、`SelectorAfterRotateOnDate`。
* 命令：`Rotate-DkimSigningConfig -Identity <CustomDomain> [-KeySize <1024 | 2048>]`。原文说明由 1024 改为 2048 时，仅在首次轮换后的活跃选择器上生效，再次轮换时另一选择器才更新。
* 原文提示：轮换进行期间不可再次发起轮换；`*.onmicrosoft.com` 域目前无自动轮换。

## 四、DMARC TXT 记录语法（原文 “Syntax for DMARC TXT records”）

人类原文来源章节：DMARC 文档 — Syntax for DMARC TXT records

原文说明：Microsoft 365 **没有**用于管理自定义域 DMARC TXT 记录的管理门户或 PowerShell cmdlet，需在域名注册商或 DNS 托管服务处创建该记录。原文给出的语法：

```
Hostname: _dmarc
TXT value: v=DMARC1; <DMARC policy>; <Percentage of DMARC failed mail subject to DMARC policy>; <DMARC reports>
```

```
Hostname: _dmarc
TXT value: v=DMARC1; p=<reject | quarantine | none>; pct=<0-100>; rua=mailto:<DMARCAggregateReportURI>; ruf=mailto:<DMARCForensicReportURI>
```

原文示例：

```
Hostname: _dmarc
TXT value: v=DMARC1; p=reject; pct=100; rua=mailto:rua@contoso.com; ruf=mailto:ruf@contoso.com
```

严格对齐模式示例（原文 Syntax 节）：

```
Hostname: _dmarc
TXT value: v=DMARC1; p=reject; aspf=s; adkim=r; pct=100; rua=mailto:dmarc@contoso.com
```

`*.onmicrosoft.com` 域（原文管理中心章节给出的取值）：

```
v=DMARC1; p=reject
v=DMARC1; p=reject; rua=mailto:rua@contoso.onmicrosoft.com; ruf=mailto:ruf@contoso.onmicrosoft.com
```

停放域（Parked domains，原文对应章节）：

```
Hostname: _dmarc
TXT value: v=DMARC1; p=reject;
```

原文说明停放域记录不含 `pct=`（默认即 100），且该场景下 `rua`／`ruf` 非必需。跨域报告授权记录示例为 `Hostname: contoso.com._report._dmarc`、`Value: v=DMARC1;`。

## 五、DMARC 官方灰度顺序（原文 “Set up DMARC for active custom domains in Microsoft 365”）

人类原文来源章节：DMARC 文档 — Set up DMARC for active custom domains

原文表述其目标为：让所有自定义域与子域最终达到 `p=reject` 策略，但沿途需要测试与验证。原文给出的推进步骤：

1. **起步 `p=none`**，监控聚合报告（`pct=100` 或省略，默认即 100）。
2. **提升至 `p=quarantine`** 并持续监控，可配合 `pct=` 逐级放量：`pct=10` → `pct=25` → `pct=50` → `pct=75` → `pct=100`。
3. **提升至 `p=reject`** 并持续监控，同样可用 `pct=` 逐级验证。
4. 按邮件量与复杂度，先对子域重复上述三步，**最后处理父域**。
5. 子域继承父域的 DMARC 记录并可单独覆盖；若最终设置一致，可仅保留父域记录。

原文给出的子域三阶段示例（marketing.contoso.com）：

```
v=DMARC1; p=none;       pct=100; rua=mailto:rua@marketing.contoso.com; ruf=mailto:ruf@marketing.contoso.com
v=DMARC1; p=quarantine; pct=100; rua=mailto:rua@marketing.contoso.com; ruf=mailto:ruf@marketing.contoso.com
v=DMARC1; p=reject;     pct=100; rua=mailto:rua@marketing.contoso.com; ruf=mailto:ruf@marketing.contoso.com
```

原文 DMARC 文档另设 DMARC troubleshooting 章节，涵盖对齐失败诊断（对齐模式、常见失败场景、从信头诊断、PowerShell 检查）、DMARC 策略对 Microsoft 365 行为的影响、聚合报告与取证报告解读、跨域报告与诊断流程，详见官方原文。

## 常见问题（答案均取自上述人类原文章节）

### Microsoft 365 自定义域启用 DKIM 需要几条 CNAME？

按官方 DKIM 文档，需要两条：selector1.\_domainkey 与 selector2.\_domainkey，分别指向 Microsoft 生成的两个公钥选择器。同一时间只有一个选择器活跃，另一个保留给后续密钥轮换。

### DKIM 密钥轮换后多久生效？

官方文档明确：轮换不是立即生效，新私钥需要 4 天（96 小时）后才开始签名，在此之前仍使用旧密钥；轮换进行期间不可再次发起轮换。

### Microsoft 官方推荐的 DMARC 上线顺序是什么？

官方 DMARC 文档给出的顺序为：先 p=none 监控，再提升到 p=quarantine 并可用 pct=10/25/50/75/100 逐级放量，最后提升到 p=reject；按邮件量先做子域、最后处理父域。

## 人类官方原文来源（source）

* Microsoft — Microsoft Learn — Set up DKIM：<https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dkim-configure>
* Microsoft — Microsoft Learn — Set up DMARC：<https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dmarc-configure>

本页为对 Microsoft Set up DKIM / Set up DMARC (Microsoft Learn, Defender for Office 365) 的中文翻译与摘录，原文著作权归该机构所有，内容以人类官方原文为准。本页仅作中文可达性辅助，任何技术决策请以上述官方原文为准。

ztpop.net 邮件技术知识库 · 官方文献中译摘录系列

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/vnd-ms-dkim-dmarc-config.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
