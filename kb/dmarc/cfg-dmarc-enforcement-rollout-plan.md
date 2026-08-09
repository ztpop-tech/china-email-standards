---
title: "DMARC 从 p=none 推到 p=reject 该按什么节奏？有没有可参照的强制时间表？"
source: "https://ztpop.net/kb/cfg-dmarc-enforcement-rollout-plan.html"
license: CC-BY 4.0
---

# DMARC 从 p=none 推到 p=reject 该按什么节奏？有没有可参照的强制时间表？

**一份可参照的强制时间表**

CISA 发布的约束性操作指令 BOD 18-01 要求美国联邦民事机构强化邮件与网站安全，其中对邮件部分提出了带时限的分阶段要求：在指令下发后的较短期限内完成 STARTTLS、SPF 与 DMARC 的初始部署，DMARC 起步策略为 p=none 并配置聚合报告接收地址；随后在约一年的期限内将 DMARC 策略提升至 p=reject。该指令同时要求禁用已不安全的协议与加密套件。对其他类型的组织而言，这份时间表的价值在于它证明了「一年内从 none 走到 reject」是一个被大规模实践验证过的可行节奏。

**阶段一：只观测，不影响投递**

以 `p=none` 起步，并务必配置 rua 聚合报告地址——没有报告的 p=none 是纯粹的空转。本阶段的唯一任务是把发信来源摸清：报告会揭示大量此前无人知晓的发信源，典型的包括业务系统通知、营销平台、工单与监控告警、以及各类历史遗留脚本。退出条件是报告中出现的发信源基本都能被归属到明确的责任方。

**阶段二：逐个修 SPF 与 DKIM 对齐**

把摸出来的合法发信源逐个补齐认证。需要特别注意 DMARC 要求的是对齐而不仅仅是通过：SPF 通过但信封发件域与显示发件域不一致，同样不算对齐。因此对第三方代发场景，通常需要配置专用子域并让其 DKIM 签名域与显示域对齐。SPF 记录还需留意 DNS 查询次数上限，把多个第三方 include 层层嵌套很容易超限而导致整体失效。退出条件是聚合报告中通过对齐的邮件量占比稳定在高位，且剩余未对齐部分已能逐条解释。

**阶段三：用 pct 做灰度**

切到 `p=quarantine` 时配合 `pct=` 参数按比例灰度，从一个较小的百分比开始，观察一段时间后逐步抬高。灰度期间要同时盯两个信号：聚合报告中的失败量，以及来自业务方的投递异常反馈。任一信号异常时先回调比例、定位原因，而不是硬扛过去。

**阶段四：切 reject 并保持观测**

quarantine 全量稳定运行一段完整周期后再切 `p=reject`。切换后不能停止看报告——新的发信源会随业务上线不断出现，而在 reject 策略下，一个未及时纳入认证的新发信源意味着邮件被直接拒收。因此需要把「新增发信源必须先完成认证配置」固化为上线流程的一环。

**覆盖不发信的域名**

组织通常持有一批仅用于品牌保护、不发邮件的域名。这类域名应直接配置最严格的策略，即 SPF 声明不授权任何主机发信，DMARC 直接设为 p=reject。它们没有存量发信源需要梳理，可以跳过灰度阶段一步到位，是整个推进过程中收益最快的部分，建议优先处理。

参考：[CISA Binding Operational Directive 18-01](https://www.cisa.gov/news-events/directives/bod-18-01-enhance-email-and-web-security) ｜ [NIST SP 800-177 Rev. 1 Trustworthy Email](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-177r1.pdf)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cfg-dmarc-enforcement-rollout-plan.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
