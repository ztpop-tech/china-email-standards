---
title: "显示名冒充（用高管名字发信但地址是真域名）怎么防？"
source: "https://ztpop.net/kb/display-name-spoofing-defense.html"
license: CC-BY 4.0
---

# 显示名冒充（用高管名字发信但地址是真域名）怎么防？

1
显示名冒充（用高管名字发信但地址是真域名）怎么防？
▼

**手法**

攻击者用任意邮箱但把「显示名」设为「张总」「财务李经理」，收件人只看名字易轻信。由于发件地址本身是真实域名（甚至免费邮箱），SPF/DKIM/DMARC 全过，技术校验无法拦。

**内部防护**

禁止员工用外部邮箱把显示名设成内部高管；对来自外部的邮件在客户端明确标注「外部」并隐藏对内部通讯录的姓名伪装。

**用户侧**

培训员工对「老板要你买礼品卡/转账」类请求一律带外确认；邮件网关可对「显示名命中高管但发件域非内部」做告警或隔离。

参考：CISA 显示名冒充警示、Agari 钓鱼态势报告、企业内部邮件标识实践。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/display-name-spoofing-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
