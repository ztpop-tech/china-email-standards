---
title: "凭据钓鱼落地页（Landing Page）如何分析与取证？"
source: "https://ztpop.net/kb/credential-phishing-landing-page-analysis.html"
license: CC-BY 4.0
---

# 凭据钓鱼落地页（Landing Page）如何分析与取证？

1
凭据钓鱼落地页（Landing Page）如何分析与取证？
▼

**检测指标**

识别线索：邮件内短链跳转到仿冒登录页、页面引用与正版高度相似的 Logo 与 CSS、表单 `action` 指向陌生域名或第三方收集服务、页面含隐藏字段收集浏览器或 OTP。邮件网关可据 URL 信誉与页面相似度预筛。

**防御措施**

* 在隔离沙箱（非生产网）用无头浏览器抓取页面与提交流量，避免直接交互泄露真实凭据。
* 提取收集终点域名、IP、证书指纹，下发网关拦截与 DNS sinkhole。
* 对用户输入做「假凭据蜜罐」：提交后呈现成功页但不外传，同时告警。

**真实攻击手法**

攻击者克隆 Office 或银行登录页，表单提交到自建收集脚本或 Telegram Bot；常用 URL 重定向、字符混淆、检测虚拟机即跳转正常页等反分析手段。部分把凭据实时转发到攻击者频道，缩短利用窗口。

**基准控制项**

取证需留存完整 HTTP 请求与响应、证书与 Whois，符合 NIST SP 800-61 事件响应与证据链要求；CIS Controls v8 控制项 13（监控）与 8（审计日志）确保可追溯；结合 RFC 7489 DMARC 阻断伪造发件域。

参考：APWG 钓鱼活动报告、PhishTank、MITRE ATT&CK T1566.002、RFC 7231（HTTP 方法）与取证日志留存规范

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/credential-phishing-landing-page-analysis.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
