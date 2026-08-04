---
title: "MITRE ATT&CK 中与邮件相关的攻击技术如何映射到检测覆盖？"
source: "https://ztpop.net/kb/mitre-attack-email-techniques-detection-coverage.html"
license: CC-BY 4.0
---

# MITRE ATT&CK 中与邮件相关的攻击技术如何映射到检测覆盖？

1
MITRE ATT&CK 中与邮件相关的攻击技术如何映射到检测覆盖？
▼

**T1566 及其子技术**

ATT&CK 企业矩阵中，**T1566（Phishing）**属于「初始访问」战术，描述对手发送钓鱼消息以获取受害者系统访问权限的行为。其官方子技术为：

* **T1566.001 Spearphishing Attachment**：以恶意附件为载荷的定向钓鱼。
* **T1566.002 Spearphishing Link**：以恶意链接为载荷的定向钓鱼。
* **T1566.003 Spearphishing via Service**：借助第三方服务（社交平台、协作与招聘平台等）而非企业邮件通道投递。
* **T1566.004 Spearphishing Voice**：结合语音通话实施的定向钓鱼。

需要注意 T1566 的定位：它描述的是**投递**，不描述受害者的动作。用户点击链接或打开附件属于「执行」战术下的 **T1204（User Execution）**，其子技术 T1204.001（Malicious Link）与 T1204.002（Malicious File）才是终端侧检测的落点。把两者混为一谈，是邮件检测覆盖度评估中最常见的错误。

**侦察与资源开发：攻击发生之前**

* **T1598 Phishing for Information**（侦察）：对手发送钓鱼消息以**套取信息**而非投递载荷，子技术包括 T1598.001（Spearphishing Service）、T1598.002（Spearphishing Attachment）、T1598.003（Spearphishing Link）与 T1598.004（Spearphishing Voice）。它与 T1566 的区别在于目的——前者要的是凭据与情报，后者要的是系统访问。凭据收割型钓鱼常同时映射到两者。
* **T1585.002 Establish Accounts: Email Accounts**（资源开发）：对手**自行注册**邮件账号用于后续行动。
* **T1586.002 Compromise Accounts: Email Accounts**（资源开发）：对手**攻陷他人已有**的邮件账号加以利用——这正是供应商邮箱失陷类 BEC 的技术根源，也解释了为何此类邮件能通过 SPF/DKIM/DMARC 全部校验。

这两项的区分对防御有直接意义：针对 T1585.002 可用新注册域名监测与域名相似度告警；针对 T1586.002 则只能依靠内容与行为异常检测，因为发信身份完全真实。

**失陷之后：发现、收集、规避与横向**

* **T1087.003 Account Discovery: Email Account**（发现）：对手枚举邮件账号列表，为后续定向做准备。
* **T1114 Email Collection**（收集）：获取用户邮件以搜集情报，含 T1114.001 本地邮件收集、T1114.002 远程邮件收集、T1114.003 邮件转发规则三个子技术。
* **T1564.008 Hide Artifacts: Email Hiding Rules**（防御规避）：创建收件箱规则自动移动或删除特定邮件，隐藏自身活动并阻断受害者获知异常。
* **T1534 Internal Spearphishing**（横向移动）：利用已控制的内部账号向组织内其他用户发送钓鱼邮件。由于发件人是真实同事、邮件走内部通道、认证结果全部通过，这类攻击对以边界为中心的邮件防护几乎完全免疫。
* **T1078 Valid Accounts**：贯穿初始访问、持久化、提权与防御规避，描述对手使用合法凭据的行为，是邮箱失陷后活动的总纲。
* **T1550.001 Use Alternate Authentication Material: Application Access Token**：说明为何仅重置口令不足以完成遏制。

**如何做覆盖度评估**

ATT&CK 为每项技术提供缓解措施（Mitigation，M 编号）与数据源（Data Source，DS 编号）字段，这正是覆盖度评估的接口。建议按四列建表：**技术编号 → 现有检测手段 → 数据源是否已采集 → 缺口与计划**。评估中反复出现的结构性缺口通常有三类：

* **只覆盖投递、不覆盖执行**：网关规则齐全，但缺少终端侧对附件落地执行、脚本宿主启动与远程模板拉取的检测，T1204 完全空白。
* **只覆盖入站、不覆盖内部与出站**：T1534 内部钓鱼与 T1114.003 转发外发因不经过入站网关而无检测，需依赖邮箱审计日志与内部投递日志。
* **只覆盖邮件、不覆盖身份**：T1078、T1550.001 的证据在身份平台而非邮件系统，若两侧日志未做关联，凭据收割型钓鱼的后半段就会失明。

评估须诚实区分「有日志」与「有检测」：数据源已采集只是必要条件，没有对应告警规则的数据源在覆盖度表中应记为未覆盖。

**使用 ATT&CK 的注意事项**

ATT&CK 是基于真实世界观察构建的对手战术与技术知识库，由 MITRE 维护并**持续更新版本**——技术会新增、拆分为子技术、重命名，也可能被弃用（deprecated）或合并。因此：

* 引用时应**以官方站点 attack.mitre.org 上的当前条目为准**，并在内部文档中记录所依据的 ATT&CK 版本，避免长期沿用已变更的编号。
* 不要臆造技术编号或子技术编号；不确定时以官方页面检索确认。
* ATT&CK 描述的是**已被观察到**的对手行为，不是威胁的全集；覆盖率 100% 不等于安全，未被 ATT&CK 收录的手法同样存在。
* 映射的价值在于沟通与缺口发现，而非计分。把覆盖率当作 KPI 会诱导团队为凑数字部署低价值规则。

参考：MITRE ATT&CK T1566 Phishing，https://attack.mitre.org/techniques/T1566/ ；T1598 Phishing for Information，https://attack.mitre.org/techniques/T1598/ ；T1534 Internal Spearphishing，https://attack.mitre.org/techniques/T1534/ ；T1114 Email Collection，https://attack.mitre.org/techniques/T1114/ ；T1564.008 Email Hiding Rules，https://attack.mitre.org/techniques/T1564/008/ ；T1087.003 Account Discovery: Email Account，https://attack.mitre.org/techniques/T1087/003/ ；T1585.002 Establish Accounts: Email Accounts，https://attack.mitre.org/techniques/T1585/002/ ；T1586.002 Compromise Accounts: Email Accounts，https://attack.mitre.org/techniques/T1586/002/ ；T1204 User Execution，https://attack.mitre.org/techniques/T1204/ ；MITRE ATT&CK 官方站点，https://attack.mitre.org/

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mitre-attack-email-techniques-detection-coverage.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
