---
title: "发件方信誉体系详解"
source: "https://ztpop.net/kb/sender-reputation-framework.html"
license: CC-BY 4.0
---

# 发件方信誉体系详解

你的邮件能否进入收件箱，很大程度上取决于邮箱服务商对你"人品"的打分。这个隐形的评分系统——发件方信誉体系——是邮件投递领域最关键也最不透明的机制。本文为你拆解全球主流邮箱服务商的信誉评估逻辑。

## 一、什么是发件方信誉

发件方信誉（Sender Reputation）是邮箱服务商为每个发送源（IP 地址和发送域名）维护的一组**动态评分**，用于判断来自该源的邮件是否可信。信誉越好，邮件越有可能进入收件箱；信誉越差，越容易被过滤到垃圾箱或被直接拒绝。

发件方信誉通常分为两层：

* **IP 信誉（IP Reputation）：** 与发件 IP 地址绑定的评分，历史行为、发送量、投诉率等都会影响
* **域信誉（Domain Reputation）：** 与发件域名（发件人 @后面的部分）绑定的评分，独立于 IP

在 Gmail 等先进系统中，域信誉的权重已经超过 IP 信誉，这意味着即使更换 IP，如果你的域名信誉良好，仍然可以获得较好的送达效果。

## 二、Gmail 信誉体系

### 2.1 双轨信誉模型

Gmail 采用**IP 信誉 + 域信誉**双轨评估模型：

* **IP 信誉：** 基于发送 IP 的历史行为，包括日发送量、投诉率、未知用户率、黑名单状态等
* **域信誉：** 基于 DKIM 签名域名（d=domain）的信誉，与发送 IP 解耦。即使 IP 变化，只要 DKIM 域名不变，域信誉得以延续

Google 官方指出，域信誉在 Gmail 中的权重更高，因为域更难以伪造且更稳定。这也是为什么即使使用第三方邮件服务商（如 Mailchimp、SendGrid），使用自己的发送域名进行 DKIM 签名仍然至关重要。

### 2.2 Google Postmaster Tools 指标

通过 [Google Postmaster Tools](https://postmaster.google.com/)，你可以查看以下关键指标：

* **IP 信誉（IP Reputation）：** Good / Medium / Poor / Bad 四个等级
* **域信誉（Domain Reputation）：** Good / Medium / Poor / Bad 四个等级
* **投诉率（Spam Rate）：** 用户标记垃圾邮件的比例
* **送达率（Delivery Errors）：** 被 Gmail 临时限制或拒绝的比例
* **反馈回环（Feedback Loop）：** Gmail 用户投诉数据（需申请并配置反馈回环）
* **身份认证（Authentication）：** SPF/DKIM/DMARC 的通过率统计
* **加密（Encryption）：** TLS 加密传输的比例

### 2.3 Gmail 信誉阈值的经验数据

| 指标 | Good | Medium | Poor | Bad |
| --- | --- | --- | --- | --- |
| 投诉率 | <0.1% | 0.1-0.3% | 0.3-1.0% | >1.0% |
| 未知用户率 | <3% | 3-8% | 8-15% | >15% |
| 身份认证通过率 | >95% | 80-95% | 50-80% | <50% |

## 三、Outlook / Microsoft 365 信誉体系

### 3.1 SNDS（Smart Network Data Service）

Microsoft 通过 [SNDS](https://sendersupport.olc.protection.outlook.com/snds/) 向发件方提供 IP 级别的信誉数据，包括：

* **日发送量：** 每天各 IP 向 Outlook.com / M365 发送的邮件总数
* **投诉率：** Outlook.com 用户的垃圾邮件投诉比例
* **垃圾邮件陷阱命中：** 是否命中 Microsoft 的蜜罐地址
* **过滤器判定：** Microsoft 智能过滤系统的最终判定结果（正常邮件 / 垃圾邮件 / 钓鱼邮件）

### 3.2 Microsoft 智能过滤系统

Outlook 和 Exchange Online Protection（EOP）使用多层过滤引擎：

1. **连接过滤：** 基于 IP 信誉、发送速率、反向 DNS 记录
2. **策略过滤：** SPF/DKIM/DMARC 验证结果
3. **内容过滤：** 机器学习引擎分析邮件内容与行为模式
4. **高级过滤：** Microsoft Defender for Office 365（原 ATP）的检测机制

Microsoft 对**域基础信誉（Domain-based Reputation）**也越来越重视。如果 DKIM 签名的域有良好信誉，即使 IP 是新分配的，也仍能保持较高送达率。

### 3.3 提交者信誉（Submitter Reputation）

Microsoft 特有的概念——如果你通过第三方服务（如 SendGrid、Amazon SES 等）发送，该服务商的 IP 信誉（称为 Submitter Reputation）也会被纳入评估。这是 Microsoft 与 Gmail 的一个重要区别。

## 四、Yahoo / AOL 信誉体系

### 4.1 投诉率驱动的动态评分

Yahoo 和 AOL（现统一由 Yahoo 管理）的信誉模型以**投诉率为核心**。Yahoo 提供 [Yahoo Postmaster](https://postmaster.yahoo.com/) 平台，展示以下数据：

* **日投诉数据：** 每日详细投诉数（需配置反馈回环）
* **信誉状态：** Normal / Throttled / Blocked 三级状态
* **身份认证状态：** SPF/DKIM/DMARC 通过情况

### 4.2 Yahoo 的信誉阈值

* **Normal：** 投诉率 < 0.1%，正常送达
* **Throttled：** 投诉率 0.1% - 0.3%，限速发送
* **Blocked：** 投诉率 > 0.3% 或在 24 小时内收到大量投诉，IP 被临时或永久阻止

Yahoo 对**未知用户率（Unknown User Rate）**也高度敏感。向不存在的 Yahoo 邮箱发送大量邮件，会迅速导致 IP 信誉恶化。

## 五、国内邮箱（QQ / 163）信誉体系

### 5.1 QQ 邮箱

QQ 邮箱采用**封闭的信誉评分机制**，不对外公开详细评分标准。基于行业经验和公开文档，影响 QQ 邮箱信誉的因素包括：

* **QQ 邮箱开放平台认证：** 通过平台认证的域名享有更高的信任度
* **SPF/DKIM/DMARC：** 认证配置的完整性和一致性直接影响信誉
* **发件行为模式：** 突然的大批量发送、频繁变更发送 IP 会触发风控
* **用户反馈：** QQ 邮箱用户标记垃圾邮件的投诉数据
* **IP 段信誉：** 如果整个 IP 段被用于发送垃圾邮件，该段内的新 IP 也会背负负面信誉

QQ 邮箱提供**发信量统计**功能（需申请），可查看每日发送量、送达量、垃圾箱量等基本数据。

### 5.2 163 邮箱（网易）

国内主流邮箱服务商的信誉体系与 QQ 邮箱类似，也采用封闭式评分模型。关键特点：

* **反垃圾评分系统：** 综合 IP、域名、内容特征进行评分
* **投诉敏感度高：** 网易用户投诉后，信誉下降较快
* **需要申请发信资质：** 大批量发送需提前向网易申请
* **白名单机制：** 通过审核的发件方可加入白名单，获得较高发送配额

## 六、影响信誉的通用因素

无论在哪个邮箱服务商，以下因素都会对发件方信誉产生直接影响：

| 因素 | 影响程度 | 说明 |
| --- | --- | --- |
| 投诉率 | 最高 | 所有服务商都将投诉率作为最核心的负面指标 |
| 未知用户率 | 高 | 向无效地址发送邮件会迅速降低 IP 和域信誉 |
| 垃圾邮件陷阱命中 | 非常高 | 一旦命中蜜罐地址，信誉可能瞬间归零 |
| SPF 对齐 | 中高 | SPF 未通过或未对齐，邮件可能被标记为可疑 |
| DKIM 签名 | 中高 | 缺少或无效的 DKIM 签名损害域信誉 |
| DMARC 策略 | 中 | p=none 不会提升信誉，p=quarantine/p=reject 表明发件方负责任的姿态 |
| 发送量稳定性 | 中 | 突然的大幅增加或停发会被视为异常行为 |
| 黑名单状态 | 高 | 列入主要 DNSBL 会立即触发所有服务商的过滤 |

## 七、如何提升和维护信誉

1. **认证先行：** 完整配置 SPF、DKIM、DMARC，确保 p 策略至少为 quarantine
2. **管理投诉：** 提供显式退订链接，收到投诉立即处理
3. **清洁列表：** 定期清洗邮箱列表，移除硬弹回和长期不活跃用户
4. **稳定节奏：** 保持每日发送量的相对稳定，避免剧烈波动
5. **监控工具：** 至少配置 Google Postmaster Tools 和 Microsoft SNDS
6. **反馈回环：** 申请各平台的反馈回环服务，主动获取投诉数据
7. **及时响应：** 一旦发现信誉下降，立即排查原因并整改

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/sender-reputation-framework.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
