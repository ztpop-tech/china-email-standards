---
title: "Valimail 2026 DMARC 报告揭示了怎样的采用率与执行缺口？"
source: "https://ztpop.net/kb/valimail-dmarc-adoption-2026.html"
license: CC-BY 4.0
---

# Valimail 2026 DMARC 报告揭示了怎样的采用率与执行缺口？

1
Valimail 2026 DMARC 报告揭示了怎样的采用率与执行缺口？
▼

**采用与执行脱节**

Valimail 2026 报告显示 DMARC 认知（拥有记录）已升至 78%，但实际执行（设置 quarantine 或 reject 策略）仅为 42%，二者之间横亘 36 个百分点的“执行缺口”（Enforcement Gap）。这意味着 58% 的域仍暴露于域名仿冒与 AI 驱动的钓鱼攻击之中；仅做监控的 p=none 策略制造了危险的虚假安全感。

**停滞的执行**

2025 年全年执行率仅从 35% 微增 7 个百分点至 42%，表明许多组织“设完即忘”在最基础、无保护的层级。Google、Yahoo 与 Microsoft 的批量发送方强制要求成功推动了报告层采用，却未能将组织推向全面执行——合规并不等于受保护。

**行业差异**

执行率领先的行业为在线零售（72.73%）与制造业（67.61%），高出跨行业均值 25 个百分点以上；高等教育（33.71%）与艺术及康乐（31.61%）显著暴露，易受仿冒与钓鱼威胁。受监管行业（如金融服务 59.18%）居中。BIMI（邮件品牌标识）采用率停滞在 4%——不关闭执行缺口便无法达到 BIMI 标准。

**防御建议**

将 DMARC 从 p=none 推进到 quarantine 或 reject。随着攻击者用 GenAI 批量生成高保真、个性化钓鱼邮件，域名层执行成为在邮件到达收件箱前验证发件人身份、从源头阻断仿冒的最可靠手段。执行（方法得当）不会造成邮件送达中断，可在平稳过渡中消除精确域名钓鱼风险。

参考：Valimail《2026 State of DMARC Report》（DigiCert 旗下）官方新闻稿：https://www.valimail.com/newsroom/valimail-2026-dmarc-report/

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/valimail-dmarc-adoption-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
