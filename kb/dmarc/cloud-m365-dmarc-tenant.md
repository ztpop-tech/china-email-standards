---
title: "租户级 DMARC 从 p=none 推进到 p=reject，怎样分阶段才不误伤合法邮件？"
source: "https://ztpop.net/kb/cloud-m365-dmarc-tenant.html"
license: CC-BY 4.0
---

# 租户级 DMARC 从 p=none 推进到 p=reject，怎样分阶段才不误伤合法邮件？

**阶段零：先让两条腿都能站住**

DMARC 本身不做任何新的校验，它只做两件事：**检查 SPF 或 DKIM 是否与 From 域对齐**，以及**告诉对方失败时怎么处置**。所以在发布策略前，SPF 与 DKIM 必须先各自配好并验证对齐。

跳过这一步直接发 DMARC 记录，等于给一个还没修好的判据加上执行力度。

**阶段一：p=none + rua，只观察不处置**

发布 `p=none` 并带上 `rua=` 聚合报告接收地址。此阶段**对邮件流零影响**，唯一目的是把「到底有多少来源在用我的域发信」这件事从猜测变成数据。

**产出物是一张发送源清单**，每一行需要回答三个问题：这个来源是谁？是否合法？如果合法，它的 SPF 或 DKIM 为什么没对齐？

观察周期建议覆盖完整的业务周期，把月结、季度对账、年度通知这类低频发送源也捞进来——只观察一两周就推进，最容易在下个月结时炸。

**阶段二：修对齐，而不是加例外**

针对清单里「合法但不对齐」的来源，正确动作是**让它对齐**：为第三方平台配置 DKIM 签名、把其发送 IP 或 include 纳入 SPF、必要时改用你自己域的子域发信。

错误动作是绕过问题——比如把这些邮件改成用第三方自己的域发送再设置回复地址。那只是把品牌一致性和可追溯性一起丢掉。

**阶段三：用 pct 做灰度进入 quarantine**

`pct` 标签指定策略适用于多大比例的失败邮件。推荐节奏：`p=quarantine; pct=10` → `pct=25` → `pct=50` → `pct=100`，每档之间留出足够观察窗口。

**每次提档前的判据：**聚合报告中「失败且来源未知」的量级是否稳定在可接受水平，以及内部是否收到新的投递投诉。任一项异常就退回上一档，而不是硬推。

**阶段四：p=reject，并单独处理子域**

quarantine 在 pct=100 下平稳运行一段时间后再进 `p=reject`。

**子域是独立的风险面：**`sp=` 标签为子域指定策略。组织常见的坑是主域已经 reject，但从未使用的子域没有任何约束，成为伪造入口。对确实不发信的子域，应当明确发布拒绝性策略，而不是留空。

**三类高频误伤源与处置**

* **邮件列表：**列表软件常改写主题或追加页脚，破坏 DKIM 签名，同时 SPF 因转发失效。处置是让列表方保持签名有效或采用可保留原始认证结果的转发方式。
* **用户自动转发：**与列表同理。这也是必须启用 DKIM 的又一理由。
* **第三方代发未签名：**最常见，也最容易修——补 DKIM 即可。

共同点是：**它们都在 p=none 阶段就会出现在聚合报告里**。阶段一做扎实，后面三个阶段基本不会有意外。

**不要把 DMARC 当成入站防护**

你发布的 DMARC 策略保护的是**别人不被冒充你**；要防住打进来的伪造邮件，靠的是对入站邮件执行校验并按结果处置。两件事经常被混为一谈，导致「我们都 reject 了怎么还收到假冒内部邮件」的困惑。

参考：[Microsoft Learn：Set up DMARC to validate the From address domain](https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dmarc-configure)、[RFC 7489：Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html)、[CISA BOD 18-01：Enhance Email and Web Security](https://www.cisa.gov/news-events/directives/bod-18-01-enhance-email-and-web-security)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-m365-dmarc-tenant.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
