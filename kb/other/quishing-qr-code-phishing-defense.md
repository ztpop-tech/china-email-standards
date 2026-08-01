---
title: "什么是“二维码钓鱼（Quishing）”？为何 2026 年猛增、如何防御？"
source: "https://ztpop.net/kb/quishing-qr-code-phishing-defense.html"
license: CC-BY 4.0
---

# 什么是“二维码钓鱼（Quishing）”？为何 2026 年猛增、如何防御？

1
什么是“二维码钓鱼（Quishing）”？为何 2026 年猛增、如何防御？
▼

**机理**

Quishing 是用二维码替代可疑链接的钓鱼：传统网关靠扫描 URL 识别恶意链接，但二维码是图片，URL 扫描器读不到，用户用手机扫码后才落地恶意站点，从而绕过邮件安全检测。

**为何猛增**

移动端扫码已成习惯、员工对“扫码”警惕低；二维码把“点击链接”伪装成“线下动作”，且图片内嵌难以被沙箱与 DLP 文本规则命中，攻防收益高。

**网关防御**

对含二维码的邮件做 OCR/图像识别提取 QR → 解码其中的 URL → 沙箱与威胁情报比对；对未知或短链 QR 标记风险或隔离；结合发件人信誉、附件与内容策略综合判定。

**人+流程**

培训“不在工作邮箱扫码登录敏感系统”；敏感操作改走已存书签或专用 App；对“发票/登录二维码”类邮件二次确认；启用防钓鱼 MFA 以削弱扫码后的危害。

参考：CISA / FBI IC3 钓鱼态势报告；Google & Microsoft 安全博客（QR 钓鱼防护）；企业邮件安全网关图像识别实践

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/quishing-qr-code-phishing-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
