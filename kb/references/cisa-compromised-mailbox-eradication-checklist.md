---
title: "确认邮箱账号失陷后，完整的处置清单有哪些步骤？"
source: "https://ztpop.net/kb/cisa-compromised-mailbox-eradication-checklist.html"
license: CC-BY 4.0
---

# 确认邮箱账号失陷后，完整的处置清单有哪些步骤？

1
确认邮箱账号失陷后，完整的处置清单有哪些步骤？
▼

**处置框架与顺序**

CISA 于 2021 年 11 月发布的《联邦政府网络安全事件与漏洞响应手册》，把事件响应流程组织为准备、检测与分析、遏制、根除与恢复、事后活动，并将协调作为贯穿全程的环节。邮箱失陷的处置须严格遵循这一顺序，尤其不可跳过「保全」直接清理：一旦删除了恶意收件箱规则，攻击者的意图证据与时间线即随之消失。

推荐的宏观顺序为：**保全 → 遏制 → 调查范围 → 根除持久化 → 恢复 → 通报与复盘**。其中遏制应在分钟级完成，调查可并行推进。

**第一组：保全与遏制**

* **先导出后清理**：完整导出该邮箱事件窗内的邮件（含已删除项、可恢复项）、邮箱审计日志、统一审计/登录日志、以及当前的规则与授权配置快照。
* **重置口令**，并要求使用与其他系统不重复的新口令。
* **强制吊销全部活动会话、刷新令牌与访问令牌**。这是最容易被遗漏也最致命的一步：ATT&CK T1550.001 描述了对手窃取应用访问令牌后以此绕过常规认证控制的手法，仅重置口令并不会使已签发的令牌失效，攻击者可继续访问直至令牌自然过期。
* **临时禁用高风险协议**：对该账号关闭 IMAP/POP/SMTP AUTH 等不支持现代认证的遗留协议。
* **阻断外发扩散**：若邮箱已在向内外部发送钓鱼邮件（对应 ATT&CK T1534 Internal Spearphishing，即对手利用已控制的内部账号向组织内其他用户发送钓鱼邮件以横向移动），应立即限制其外发能力并对已发出的邮件执行全域回收。

**第二组：确定攻击者做了什么**

ATT&CK T1114（Email Collection）描述对手为收集情报而获取用户邮件的行为，包含三个子技术：T1114.001 本地邮件收集（从终端本地邮件文件获取）、T1114.002 远程邮件收集（直接访问邮件服务器或云端邮箱）、T1114.003 邮件转发规则（创建转发规则持续获取邮件副本）。调查须逐项回答：

* **访问时间线**：首次异常登录时间、来源 IP 与 ASN、客户端标识、是否通过 MFA、MFA 方式是否被更改或新增。
* **数据访问范围**：是否执行了大批量邮件下载或搜索；搜索关键词往往直接暴露攻击目的（如发票、口令、合同）。
* **外发行为**：以该邮箱名义发出的邮件清单，特别是对内钓鱼与对外的账户变更请求。
* **是否触及其他资源**：同一凭据是否用于 VPN、SSO 下的其他 SaaS、代码仓库或运维后台（对应 T1078 Valid Accounts——对手利用合法凭据获取初始访问、持久化、提权与防御规避，且此类活动因使用真实账号而难以与正常行为区分）。

**第三组：根除全部持久化点**

邮箱失陷的持久化点分散在多个配置面，必须逐一清点，任一遗漏都会导致重新失陷：

* **收件箱规则**：删除全部指向外部地址的转发规则；ATT&CK T1564.008（Email Hiding Rules）指出对手会创建规则自动移动或删除邮件以隐藏活动痕迹，需重点排查将特定关键词邮件移入「RSS 源」「垃圾邮件」「已删除邮件」或直接删除的规则。
* **账户级转发设置**：与收件箱规则相互独立，需单独检查并关闭。
* **委派与代发权限**：mailbox delegation、send-as、send-on-behalf、共享邮箱成员关系。
* **OAuth 应用授权**：撤销可疑第三方应用对邮箱的读写授权；此类授权在口令重置后依然有效。
* **MFA 注册项**：删除攻击者新注册的验证器、电话号码或备用邮箱，这是最常见的隐蔽后门。
* **应用专用口令与设备令牌**：全部作废并重新签发。
* **邮箱签名与自动回复**：攻击者可能在其中植入恶意链接。
* **连接的设备与客户端**：移除未知设备的邮箱同步授权。

**第四组：恢复、通报与复盘**

* **恢复的前提是可信凭据**：重置须在已确认干净的设备上进行；若终端本身可能被植入信息窃取程序，应先完成终端处置或重装，否则新口令会被立即再次窃取。
* **强化认证**：为该账号（并推广至同类高风险岗位）启用抗钓鱼的多因素认证，禁用短信等易被中间人代理绕过的因素。
* **提高监控灵敏度**：对该账号在后续一段时间内设置增强告警（新建转发规则、异地登录、大批量邮件访问、新增 OAuth 授权），验证根除是否彻底。
* **对内对外通报**：向收到该邮箱所发钓鱼邮件的内外部相关方发出告知；若涉及个人数据或受监管信息，须按适用法律与合同评估通知义务与时限，并同步法务与合规。政府与关键基础设施相关组织可通过 https://www.cisa.gov/report 报告事件。
* **复盘**：定位初始入口（钓鱼落地页、口令喷洒、中间人代理会话窃取、第三方泄露口令复用），并把结论转化为控制改进。NIST SP 800-61 Rev.3 以 CSF 2.0 的治理功能强调事件响应与组织风险管理的融合，其含义正是：单次账号恢复只是终点的一半，控制层面的改进才是另一半。

参考：CISA《Federal Government Cybersecurity Incident and Vulnerability Response Playbooks》，2021 年 11 月，https://www.cisa.gov/resources-tools/resources/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks ；NIST SP 800-61 Rev. 3，2025 年 4 月，https://csrc.nist.gov/pubs/sp/800/61/r3/final ；MITRE ATT&CK T1114 Email Collection，https://attack.mitre.org/techniques/T1114/ ；T1564.008 Hide Artifacts: Email Hiding Rules，https://attack.mitre.org/techniques/T1564/008/ ；T1078 Valid Accounts，https://attack.mitre.org/techniques/T1078/ ；T1550.001 Use Alternate Authentication Material: Application Access Token，https://attack.mitre.org/techniques/T1550/001/ ；T1534 Internal Spearphishing，https://attack.mitre.org/techniques/T1534/

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cisa-compromised-mailbox-eradication-checklist.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
