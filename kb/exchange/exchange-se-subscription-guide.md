---
title: "Exchange Server SE 订阅版技术详解：升级路径、许可与功能变化"
source: "https://ztpop.net/kb/exchange-se-subscription-guide.html"
license: CC-BY 4.0
---

# Exchange Server SE 订阅版技术详解：升级路径、许可与功能变化

# Exchange Server SE 订阅版技术详解：升级路径、许可与功能变化

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤

发布于 2026-07-20

Microsoft Exchange Server Subscription Edition（SE）是 Exchange Server 产品线的下一代里程碑版本，于2025年下半年正式发布。其 RTM 代码基础与 Exchange 2019…

## 摘要

Microsoft Exchange Server Subscription Edition（SE）是 Exchange Server 产品线的下一代里程碑版本，于2025年下半年正式发布。其 RTM 代码基础与 Exchange 2019 CU15 等效，这意味着 Exchange 2019 用户可以通过原地升级（In-Place Upgrade）平滑过渡到 SE。然而，SE 带来的不仅是技术上的延续，更包括许可模型的根本性变革——从永久授权转向年度订阅制。本文基于 Microsoft Learn 官方文档，全面解析 SE 的系统要求、升级路径、许可变化与功能演进，为 Exchange 运维团队的技术决策提供权威参考。

## 1. 背景：Exchange Server SE 的定位

Exchange Server Subscription Edition 是微软为本地部署（On-Premises）Exchange 客户提供的长期演进方案。Exchange 2016 和 Exchange 2019 均已在2025年进入扩展支持末期，且 Exchange 2013 及更早版本早已完全停止支持。SE 并未推翻 Exchange 2019 的架构基础——其 RTM 代码与 Exchange 2019 CU15 等效，这意味着微软选择了"延续性演进"路线而非"推倒重来"。这对现有 Exchange 客户而言是重大利好：运维团队在 Exchange 2019 上积累的经验和配置可以大部分延续到 SE 环境。

SE 的发布也标志着微软本地 Exchange 产品线的战略调整：SE 将不再仅仅是"下一个 Exchange 大版本"，而是转型为以订阅制为核心的持续交付平台。微软承诺 SE 将通过累积更新（CU）持续演进，而不再规划"Exchange 2022"之类的独立主版本[1]。

## 2. 升级路径全解析

### 2.1 支持的直接升级路径

Exchange SE 支持的升级路径如下[1][4]：

* **Exchange 2019 CU14/CU15 → Exchange SE：**原地升级（In-Place Upgrade），这是最平滑的迁移路径。管理员在现有 Exchange 2019 服务器上直接运行 SE 安装程序，安装程序检测到已安装的 Exchange 2019 CU14/CU15 后将执行架构升级。整个过程保留所有数据库、虚拟目录配置、接收连接器和发送连接器。
* **Exchange 2016 → 需先升级到 Exchange 2019 CU14/CU15 → 再升 SE：**Exchange 2016 无法直接原地升级到 SE。必须先执行 Exchange 2016 → Exchange 2019 CU14/CU15 的过渡升级，再升级到 SE。这一中间步骤不可省略，因为 SE 仅向后兼容到 Exchange 2019 CU14。

### 2.2 不支持或不再支持的路径

* **Exchange 2013 及更早版本：**无法直接或间接升级到 SE。这些版本已在多年前结束生命周期，与 SE 之间存在不可逾越的架构鸿沟。运行 Exchange 2013 的组织需要规划完整的"重建迁移"（而非升级），例如在新建 SE 环境中通过跨林移动邮箱（Cross-Forest Mailbox Move）或第三方迁移工具进行迁移。
* **不支持 Exchange 2016 直接升 SE：**跳过 Exchange 2019 中间步骤直接升级到 SE 是不支持的。

### 2.3 升级注意事项

升级前务必完成下述准备工作：确保所有 Exchange 2019 数据库处于健康状态，DAG（Database Availability Group）所有副本同步完整；安装最新的 Exchange 2019 CU15 及所有安全更新（SU）；升级前执行完整的 Schema 扩展和 AD 准备（`Setup.exe /PrepareSchema` 和 `/PrepareAD`）；备份所有 Exchange 数据库、配置文件和 IIS 设置；在实验环境中先用生产数据副本走一遍升级流程，验证兼容性。

## 3. 许可模型：从永久授权到订阅制

### 3.1 许可模式的根本性变革

Exchange SE 采用订阅许可（Subscription License），不再提供永久授权[3]。这是 Exchange 本地产品线二十余年来最重大的商业模式变化。在新的许可模型下：

* **订阅周期：**年度订阅制，每年续费。许可证在订阅到期后失效，邮件服务不受影响但不再能获得安全更新和新功能。
* **Windows Server 许可：**仍需独立购买 Windows Server 许可（标准版或数据中心版），SE 的订阅许可仅覆盖 Exchange 本身。
* **客户端访问许可（CAL）：**CAL 要求继续存在，每个访问 Exchange 邮箱的用户或设备需要对应的 CAL。SE 的 CAL 同样采用订阅模式。
* **与 Exchange Online 的区别：**Exchange Online 的订阅包含在 Microsoft 365 计划中，无需额外购买 Windows Server 许可和底层基础设施管理。Exchange SE 面向需要将数据完全保留在自有数据中心内的组织。

### 3.2 对现有客户的影响

对于从 Exchange 2019 永久授权升级到 SE 的客户，微软提供了过渡政策：拥有有效 Exchange 2019 许可（含 Software Assurance）的客户可在 SE 发布后的特定窗口期内享受订阅费减免或过渡优惠。详细的过渡条款因客户规模和授权协议类型（EA/EAS/MPSA/CSP）而异，建议联系微软授权经销商获取准确报价[3]。

### 3.3 许可合规建议

* 评估现有 Exchange 2019 Server License + CAL 的剩余有效价值，计算切换到 SE 订阅的 TCO（总拥有成本）变化。
* 如果组织计划在未来2-3年内迁移至 Exchange Online 或国产邮件系统，应计算"短期待在 Exchange 2019 并延保"与"升级到 SE 并支付订阅费"的损益平衡点。
* 混合部署场景（Exchange SE + Exchange Online）涉及额外的许可考量——本地 SE 服务器需完整订阅许可，即使仅用于管理收件人或 SMTP 中继。

## 4. 系统要求

### 4.1 硬件要求

Exchange SE 的硬件要求与 Exchange 2019 基本一致[2]：

* **处理器：**支持 SSE4.2 指令集的 x64 架构处理器。Intel 方面为 Nehalem 微架构（2008年）及更新，AMD 方面为 Bulldozer 微架构（2011年）及更新。这意味着几乎所有近十年的服务器级 x64 CPU 均可满足要求。
* **内存：**邮箱角色（Mailbox Role）最低 128GB。这个数值是微软经过大规模生产环境验证后给出的建议——实际使用中，内存需求与邮箱数量、并发连接数和数据库缓存配置强相关。对于仅部署边缘传输角色（Edge Transport）的服务器，内存需求可以降至 64GB。
* **磁盘空间：**安装驱动器至少 30GB 可用空间；数据库和日志驱动器需额外空间，具体取决于邮箱数量和预期增长率。强烈建议将操作系统、Exchange 程序文件、数据库文件和事务日志分别放置在不同的物理磁盘或 LUN 上。
* **分页文件：**建议为物理内存的 1.5 倍，最小值不低于物理内存大小。

### 4.2 Active Directory 要求

Exchange SE 对 Active Directory 的要求显著提高[2]：

* **域功能级别：**最低 Windows Server 2012 R2。这意味着所有域控制器必须运行 Windows Server 2012 R2 或更高版本。
* **林功能级别：**最低 Windows Server 2012 R2。
* **Schema 扩展：**必须运行 Exchange SE 安装程序中的 Schema 扩展步骤，将 AD Schema 更新至包含 Exchange SE 新增属性和类的级别。
* **全局编录（GC）：**每个包含 Exchange 服务器的 Active Directory 站点中至少需要一台全局编录服务器。
* **DNS：**AD 集成的 DNS 区域是推荐配置，确保 Exchange 服务器能够正确解析域名和定位域控制器。

### 4.3 操作系统要求

Exchange SE 要求 Windows Server 2022 或更高版本（Windows Server 2025 也可支持），且必须为完整桌面体验安装（Server with Desktop Experience），不支持 Server Core 安装模式。

## 5. 客户端支持与协议变化

### 5.1 支持的客户端

* **Outlook 2019 / 2021 / Microsoft 365：**完整功能支持，包括缓存模式、在线模式以及 MAPI over HTTP 连接。Outlook 2016 虽然仍可连接但功能受限，不再接受针对 Outlook 2016 的兼容性修补。Outlook 2013 及更早版本不再支持[1]。
* **Outlook Web App (OWA)：**现代浏览器（Edge、Chrome、Firefox、Safari 的最新两个大版本）完全支持。Internet Explorer 11 和旧版 Edge（EdgeHTML 内核）不再支持。
* **Exchange ActiveSync (EAS)：**移动设备通过 EAS 协议同步邮件、日历和联系人。
* **IMAP / POP3 / SMTP：**标准邮件协议继续支持，但 Microsoft 不再为这些协议新增功能。

### 5.2 协议变化

* **MAPI over HTTP 成为默认协议：**Exchange SE 中 MAPI over HTTP 是 Outlook 客户端的默认且推荐连接协议。旧的 RPC over HTTP（即 Outlook Anywhere）已被完全移除，不再作为备选协议。这一变化要求所有 Outlook 客户端均支持 MAPI over HTTP（Outlook 2013 SP1 及以上版本均支持）。
* **Outlook Anywhere (RPC/HTTP) 移除：**该协议自 Exchange 2013 以来已逐步被 MAPI over HTTP 替代，Exchange SE 中彻底移除了相关组件。任何依赖 Outlook Anywhere 的外部访问配置（如反向代理规则）需在升级前迁移到 MAPI over HTTP。

### 5.3 EWS 退役时间表

Exchange Web Services (EWS) 正在逐步退役，这对依赖 EWS 的第三方集成和企业应用具有深远影响[5]：

* **2026年10月1日：**微软将默认禁用所有非注册应用的 EWS 访问。已通过 EWSAllowedAppIDs 注册的应用程序可继续使用 EWS。
* **2027年4月：**EWS 完全关闭，所有 EWS 请求将被拒绝。
* **迁移建议：**所有依赖 EWS 的第三方应用（CRM 集成、邮件归档工具、自定义邮件插件等）需要在此时间节点前迁移至 Microsoft Graph API 或 REST API。对于 Exchange 本地部署，Graph API 需要通过混合部署（Hybrid Modern Authentication）来使用。

## 6. 功能变化

### 6.1 已移除的功能

* **统一消息（Unified Messaging, UM）：**UM 角色自 Exchange 2019 起已移除，SE 继续不包含 UM 功能。需要语音邮件集成到 Exchange 的方案应迁移至 Teams Phone System 或第三方 VoIP-PBX 集成。
* **Outlook Anywhere (RPC/HTTP)：**已彻底移除，见上文。

### 6.2 安全增强

Exchange SE 在安全方面进行了系统性加固[7]：

* **TLS 1.2 / 1.3 默认启用：**SE 默认禁用 TLS 1.0 和 1.1，仅接受 TLS 1.2 及以上版本的连接。对于出站 SMTP 连接，SE 优先尝试 TLS 1.3，回退至 TLS 1.2。所有与客户端、其他 Exchange 服务器以及外部 SMTP 服务器的通信均受 TLS 保护。
* **AMSI 集成：**Antimalware Scan Interface（AMSI）集成允许 Exchange 服务器将 HTTP 请求中的可疑内容（如通过 EWS 或 OWA 提交的脚本和数据）提交至已安装的反恶意软件解决方案进行扫描。这对于防御通过 HTTP 层的攻击向量（如 ProxyShell 类漏洞的利用载荷）具有重要意义。
* **Windows Defender 集成：**SE 与 Windows Defender Antivirus 的开箱即用集成进一步优化，预置了 Exchange 文件路径和进程的排除规则，避免反病毒扫描与 Exchange 数据库操作产生性能冲突。
* **现代认证（OAuth 2.0）：**Exchange SE 原生支持基于 OAuth 2.0 的现代认证，替代传统的 NTLM 和基本认证。OAuth 2.0 提供基于令牌的认证机制，支持条件访问策略、MFA 和令牌吊销。混合部署场景下，Exchange SE 与 Azure AD 之间的 OAuth 信任关系是实现 Hybrid Modern Authentication 的前提。

### 6.3 持续的改进方向

微软已明确 SE 将采用持续交付模式，通过累积更新（CU）而非独立大版本来发布新功能和安全更新。这与 Windows Server 的 LTSC 模式形成对比——SE 更接近"持续演进"的 SaaS 运维理念，但数据和控制平面完全留在客户本地。

## 7. 共存方案

### 7.1 Exchange 2019 共存

Exchange SE 与 Exchange 2019 可以在同一组织中完全共存（Full Coexistence），支持跨版本的邮箱移动、空闲/忙碌查询、邮件流和客户端重定向[6]。这为分阶段升级提供了技术基础——组织可以逐步将 Exchange 2019 服务器升级到 SE，过程中的邮件流和客户端访问不受影响。

### 7.2 Exchange 2016 共存

Exchange SE 与 Exchange 2016 的共存支持有限（Limited Coexistence）。基本邮件流和客户端重定向功能可用，但某些高级功能（如跨版本的 DAG 成员混合）不被支持。建议在升级路径上尽快将 Exchange 2016 先从共存环境中移除（升级到 2019 或直接退役），以减少兼容性风险。

### 7.3 共存期运维建议

* 使用 Exchange 管理控制台（EAC）和 Exchange Management Shell 确保所有虚拟目录的 InternalURL/ExternalURL 配置正确。
* 监控客户端协议代理（Client Access Services）的健康状态，确保跨版本的重定向逻辑正常工作。
* 在执行跨版本邮箱移动前，在目标 SE 服务器上预创建所有必需的邮箱数据库。

## 8. 部署与迁移规划建议

### 8.1 评估是否升级到 SE

并非所有 Exchange 客户都需要升级到 SE。决策时需考虑以下因素：

* **Exchange 2019 延保 vs SE 订阅费：**如果组织计划在未来 3-5 年内迁移至 Exchange Online 或国产邮件系统，可评估直接购买 Exchange 2019 的延保支持（Extended Security Updates）而非升级 SE 的经济可行性。
* **AD 域功能级别：**如果组织仍运行 Windows Server 2012（非 R2）域控制器，升级到 SE 将强制要求先升级域/林功能级别到 2012 R2 或更高，这可能引发额外的 AD 升级项目。
* **EWS 依赖评估：**盘点所有依赖 EWS 的应用程序，估算迁移到 Graph API 的工作量。如果迁移工作量巨大且无法在 2027 年 4 月前完成，应制定 EWS 退役前的过渡方案（例如将依赖 EWS 的功能先临时改用 SMTP/IMAP 代替）。

### 8.2 分阶段升级计划

推荐的标准升级流程：

1. **评估与准备阶段（1-2周）：**评估现有 Exchange 2019 环境（版本、CU 级别、DAG 状态、AD 级别），确认升级路径。在实验环境中执行完整升级流程测试。
2. **AD 准备（1天，变更窗口）：**执行 Schema 扩展和 AD 准备（`/PrepareSchema`、`/PrepareAD`、`/PrepareDomain`），在所有域控制器上完成复制。
3. **首台 SE 部署（1-2天）：**部署第一台 Exchange SE 服务器（新安装，非原地升级），配置共存，验证邮件流和客户端访问。
4. **分批次原地升级（按服务器数量分周进行）：**将 Exchange 2019 CU15 服务器逐批进行原地升级到 SE。每批升级后在下一个批次开始前验证 48 小时。
5. **退役 Exchange 2019（升级验证完成后）：**所有服务器升级完毕且稳定运行 2 周后，从 AD 中清除 Exchange 2019 的残留对象。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-se-subscription-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
