---
title: "OAuth 应用同意钓鱼怎么防？用户同意策略应该收紧到什么程度？"
source: "https://ztpop.net/kb/cloud-oauth-app-consent-abuse.html"
license: CC-BY 4.0
---

# OAuth 应用同意钓鱼怎么防？用户同意策略应该收紧到什么程度？

**攻击路径：不偷密码，直接要授权**

同意钓鱼不尝试获取凭据，而是诱导用户为一个攻击者控制的第三方应用**授予邮箱访问权限**。用户看到的是一个形式完全正常的授权页面，点击「接受」即完成。

它之所以危险，在于绕过了两道主要防线：

* **绕过密码：**全程不需要用户输入密码，因此密码强度策略与泄露检测都不起作用。
* **绕过多因素认证：**用户是在**已完成认证的会话**中主动授权的，多因素认证在此之前就已通过。

**为什么改密码不足以处置**

授权产生的是**独立于密码的访问令牌与刷新令牌**。只要授权关系还在，攻击者就能持续刷新访问权限——**重置密码并不会终止它**。

这是应急响应中最容易出错的一步：处置了账号却没有处置授权，攻击者的访问从未中断。

**正确处置顺序：**吊销该应用的授权 → 吊销相关会话与刷新令牌 → 重置凭据 → 检查邮箱是否被创建了转发规则或委派权限。**第四步不能省**——攻击者常在失去访问前留下持久化的转发配置。

**收紧用户同意：三个档位**

1. **允许用户同意任意应用（默认最宽松）：**不建议在任何生产租户保留。
2. **仅允许对已验证发布者的低影响权限同意（推荐起点）：**把面向普通用户的同意范围限制在风险较低的权限上，邮件读写这类高影响权限一律走管理员审批。这一档在安全性与体验之间较为平衡。
3. **完全禁止用户同意：**安全性最高，但**必须配套管理员同意工作流**，否则用户的合理需求无法满足，会转而寻找绕过方式（例如把数据导出到个人环境），反而制造更大风险。

**关键判断：**收紧的档位取决于你能否及时处理审批请求。审批长期积压的收紧，最终都会被业务压力打回原形。

**管理员同意工作流要能真正跑起来**

禁止用户自行同意之后，必须给出一条通畅的申请路径，否则策略无法长期维持。配套要素：

* **明确的审批人**，且有备份审批人，避免单人休假造成阻塞。
* **承诺的响应时限**，并实际度量达成率。
* **审批清单：**发布者是否已验证、申请的权限是否超出功能所需、是委派权限还是应用权限（后者不受用户范围限制，影响面大得多，应更严格）、该应用是否已有同类替代。

**检测：关注权限与行为，而非应用名称**

恶意应用的名称往往刻意模仿常见办公工具，靠名字判断不可靠。应关注：

* **权限组合是否与用途匹配：**一个日程小工具申请邮件读写权限，本身就是强信号。
* **授权增长模式：**某应用在短时间内被大量用户集中授权，通常意味着一次进行中的钓鱼活动。
* **应用的实际行为：**授权后是否出现大批量邮件读取、异常时间的访问、来自异常位置的调用。
* **发布者信息：**是否已验证、注册时间是否很短。

**盘点存量，不要只防新增**

收紧策略只影响后续授权，**历史上已经授予的权限依然有效**。因此必须做一次存量盘点：

* 导出全部已授权应用及其权限范围与授权用户数。
* 优先审查具备邮件读写、文件全量访问、目录读取能力的应用。
* 对无人认领、长期无活动、或发布者不可考的应用，先吊销再观察——有业务影响会很快反馈，而放着不管的风险是持续的。
* 把这项盘点固化为周期性任务，并纳入云服务安全基线的检查项。

参考：[Microsoft Learn：Configure how users consent to applications](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-user-consent)、[Microsoft Learn：Configure the admin consent workflow](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-admin-consent-workflow)、[Microsoft Learn：Investigate risky OAuth apps](https://learn.microsoft.com/en-us/defender-cloud-apps/investigate-risky-oauth)、[Microsoft Learn：App governance anomaly detection alerts](https://learn.microsoft.com/en-us/defender-cloud-apps/app-governance-anomaly-detection-alerts)、[CISA：Secure Cloud Business Applications (SCuBA) Project](https://www.cisa.gov/resources-tools/services/secure-cloud-business-applications-scuba-project)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-oauth-app-consent-abuse.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
