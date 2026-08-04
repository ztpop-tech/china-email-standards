---
title: "AiTM 钓鱼平台如何绕过 MFA 实现 Microsoft 365 邮箱接管？"
source: "https://ztpop.net/kb/abnormal-aitm-account-takeover-2026.html"
license: CC-BY 4.0
---

# AiTM 钓鱼平台如何绕过 MFA 实现 Microsoft 365 邮箱接管？

1
AiTM 钓鱼平台如何绕过 MFA 实现 Microsoft 365 邮箱接管？
▼

**三阶段攻击链**

Abnormal 追踪的 Matrix 平台展示了当前 AiTM 邮箱接管的标准形态。**投递阶段**：邮件从某个无关第三方的**真实被攻陷 Microsoft 365 邮箱**发出，伪装为 OneDrive 文档通知，因此 SPF 与 DKIM 均正常通过并被投递；恶意链接不在正文，而是藏在嵌套的 `message/rfc822` 附件内部。**跳转阶段**：链接先经 QuestionStar 问卷与 Zoho Insights 点击跟踪器两个「被滥用但合法」的 SaaS 服务，再抵达攻击者控制的、由 Cloudflare 前置的免费 DNS 区。**收割阶段**：落地页后端与真实微软登录服务保持一条实时已认证会话，随受害者输入同步推进。

**MFA 是如何被绕过的**

这不是「存储转发式」的凭据表单，而是**实时中继**。受害者提交口令后，后端向真实微软服务发起登录，微软返回该账号已注册的 MFA 方式数组（推送数字匹配、Authenticator 一次性口令、短信），钓鱼页据此**自适应地只显示该账号真实可用的选项**；页面还会显示真实的 Authenticator 数字匹配码，并拉取目标组织真实的 Entra 徽标与背景图。因此，被窃取的产物是**一条已经满足 MFA 的活会话**——Abnormal 明确指出：「重置密码并不能使其失效。」这也解释了为什么大量组织在「已全员开启 MFA」的前提下仍然发生邮箱接管。

**规避检测的七类手法**

* **嵌套附件藏链**：恶意链接从不出现在邮件网关与 URL 扫描器读取的字段中，基于链接的检测与狩猎因此完全失明。
* **Cloaking 拦截页**：`index.php` 运行会话计数状态机，自动化抓取与扫描器只拿到隐藏诱饵，真实交互浏览器才被送往收割页。
* **零宽字符填充**：页面标题显示为「Microsoft 365 Secure Sign-In」，但字符串中填充了 84 个零宽字符以破坏字符串匹配。
* **内联 favicon**：favicon 以 data URI 内联，不产生外部请求，使 urlscan、Shodan、FOFA 的 favicon 哈希关联无从下手。
* **脚本加固**：181 KB 脚本经 Obfuscator.io 处理，含字符串数组轮转、自防御代码、`constructor('debu'+'gger')` 反调试陷阱与 console 方法劫持。
* **字形仿冒发件人**：显示发件人伪装为 `one1drvs[.]com`（用数字 1 仿冒 onedrive[.]com），该域从不解析，只用于装点诱饵。
* **邮箱放在 URL 片段**：收件人邮箱置于 `location.hash` 中，因而永远不会进入服务器或网关日志。

**处置与狩猎要点**

Abnormal 给出的动作清单具有普适性。**吊销会话而非只改密码**：对任何到达过收割页的用户，吊销 Entra 刷新令牌与全部活动会话，并重新注册 MFA。**把嵌套附件型文档通知当作一等检测面**：来自罕见第三方发件人、通过认证、携带嵌套 `message/rfc822` 或 `octet-stream` 附件且渲染成 OneDrive／文档就绪通知的邮件，应直接作为高价值信号。**假定 AiTM，监控会话层**：对「来自异常网络的交互式 MFA 成功后不久出现新会话登录」这一模式告警，它与会话中继高度吻合。**狩猎工具包而非本周域名**：以持久的文件哈希与后台调用的端点做枢轴，而不是追逐速变域名。**维护不阻断清单**：被滥用的合法 SaaS 跳转器、被接管的第三方 SaaS 主域与共享的 Cloudflare 边缘 IP 必须排除在封禁列表之外，否则会造成大面积误伤。

参考：Abnormal AI 威胁情报《Introducing Matrix: A Microsoft 365 AiTM Platform Overlapping the Sneaky2FA Lineage》（2026-08-03）：<https://abnormal.ai/blog/matrix-microsoft-365-aitm-panel-sneaky2fa-lineage>

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/abnormal-aitm-account-takeover-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
