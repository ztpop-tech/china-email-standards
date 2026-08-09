---
title: "从传统专有协议邮件平台迁到国产化邮件系统，SMTP 层要注意什么？"
source: "https://ztpop.net/kb/xc-legacy-platform-smtp-migration-compat.html"
license: CC-BY 4.0
---

# 从传统专有协议邮件平台迁到国产化邮件系统，SMTP 层要注意什么？

**先做协议面盘点：把专有能力和标准协议区分开**

传统专有平台的很多能力并不走标准 SMTP/IMAP，而是走厂商自有的客户端协议与目录接口。迁移前必须逐项列出，判断每一项在标准协议下如何承接：

* **能直接对应的**：邮件收发（SMTP/IMAP/POP）、通讯录查询（目录服务协议）、Web 访问。
* **需要替代方案的**：日历与会议室预定、任务与便签、共享邮箱与委托访问、离线缓存同步、消息撤回。**这些是专有协议特性，标准协议下的行为不完全等价，必须逐项与业务确认可接受度。**
* **需要重新开发的**：依赖专有接口的业务系统集成（如工作流发信、报表推送）。

**盘点产出物：**一张「功能—协议—替代方案—影响用户范围」对照表。**迁移失败的项目，绝大多数败在这张表没做，而不是败在服务器搭不起来。**

**业务系统发信：最容易被漏掉的一群「用户」**

组织内往往有大量非人类发信方：监控告警、工单系统、财务对账、扫描仪、打印机、旧版脚本。它们的共同特点是**配置分散、无人认领、故障后才被发现**。

**可操作做法：**

1. 在旧平台上开启连接级日志，按源 IP 与认证账号聚合，统计一个完整业务周期（含月末、季末）的全部发信来源。
2. 逐一确认归属，登记为「已认领/待认领」。
3. 为每个来源单独分配认证凭据，不要共用一个万能账号——共用账号会让后续的审计与故障定位彻底失效。
4. 对无法改造的老旧设备，设立受限中继入口：限定源 IP、限定发件地址、限定收件域、单独限速并全量记日志。

**提交与认证：把明文路径一次性关掉**

迁移是清理历史包袱的最佳时机。依据 RFC 8314 Cleartext Considered Obsolete: Use of TLS for Email Submission and Access，明文的邮件提交与访问应视为过时；RFC 4954 SMTP Service Extension for Authentication 定义的 AUTH 扩展要求认证在受保护的通道内进行。

**可操作配置：**

* 提交统一走 465（隐式 TLS）；保留 587 时必须要求先 STARTTLS 再 AUTH，并在未加密状态下不通告 AUTH 能力。
* 禁用明文认证机制在未加密通道上的可用性。
* 访问侧统一 993/995，关闭 143/110 的对外可达。
* **迁移期保留一个明文端口「以防万一」是最常见的错误**——它会一直存在下去，并在测评时被直接开不符合项。正确做法是把这些客户端登记出来单独改造。

**客户端自动配置与地址格式**

专有平台的客户端通常自动发现服务器；换成标准协议后，需要提供自动配置能力，否则会产生大量人工配置工单。RFC 6186 Use of SRV Records for Locating Email Submission/Access Services 定义了用 SRV 记录定位提交与访问服务的方法，可作为标准化的自动发现手段之一。

地址与邮件头方面，RFC 5322 Internet Message Format 是唯一裁判。迁移中的高频问题：

* **专有平台的内部地址格式**（非标准形式的收件人标识）在标准协议下不可用，需在迁移时统一映射为标准邮件地址。
* **显示名中的特殊字符与非 ASCII 编码**需按标准编码，否则对端显示乱码。
* **历史邮件中的专有头字段**迁移后失去意义，但不要删除——它们对追溯原始来源有价值。

**并存期路由：一个域两套系统怎么不丢信**

迁移几乎不可能一夜完成，必然有一段时间同一域名下用户分处两套系统。设计要点：

1. **选定唯一入口**：外部邮件统一先进入一套系统（通常是新系统），由它按用户清单决定本地投递还是转投旧系统。**两套系统都直接对外收信是灾难性设计**——会出现循环、双投与不可追溯。
2. **维护权威用户清单**：路由判定必须基于一份实时同步的清单，而非静态配置文件。清单滞后会直接导致退信。
3. **处理未知用户**：并存期对未知收件人应**暂时接受并投递到人工处理队列**，而不是直接拒绝——避免清单同步延迟造成真实丢信。切换完成后再恢复严格拒绝。
4. **保留 RFC 5321 Simple Mail Transfer Protocol 定义的信封信息与投递轨迹**，使跨系统流转可追溯。

**切换判定条件与回退**

不要用「感觉稳定了」作为切换依据。可验证的判定条件：

* 试点用户组连续一个完整业务周期内，退信率与投递延迟与旧平台基线持平或更优。
* 全部已认领的业务发信源在新系统上验证通过。
* 外部主要往来域的双向收发实测通过，且传输加密协商结果符合预期。
* 邮件数据校验通过（计数一致、抽样内容一致）。
* **回退路径经过实际演练**，而不只是写在方案里。

迁移期间的邮件安全通用实践可参考 NIST SP 800-177 Rev.1 Trustworthy Email。

参考：[RFC 8314 Cleartext Considered Obsolete: Use of TLS for Email Submission and Access](https://www.rfc-editor.org/rfc/rfc8314.html) ｜ [RFC 4954 SMTP Service Extension for Authentication](https://www.rfc-editor.org/rfc/rfc4954.html) ｜ [RFC 6186 Use of SRV Records for Locating Email Submission/Access Services](https://www.rfc-editor.org/rfc/rfc6186.html) ｜ [RFC 5321 Simple Mail Transfer Protocol](https://www.rfc-editor.org/rfc/rfc5321.html) ｜ [RFC 5322 Internet Message Format](https://www.rfc-editor.org/rfc/rfc5322.html) ｜ [NIST SP 800-177 Rev.1 Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/xc-legacy-platform-smtp-migration-compat.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
