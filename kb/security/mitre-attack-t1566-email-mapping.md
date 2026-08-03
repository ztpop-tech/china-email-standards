---
title: "MITRE ATT&CK 中邮件攻击战术（T1566）如何映射与防御？"
source: "https://ztpop.net/kb/mitre-attack-t1566-email-mapping.html"
license: CC-BY 4.0
---

# MITRE ATT&CK 中邮件攻击战术（T1566）如何映射与防御？

1
MITRE ATT&CK 中邮件攻击战术（T1566）如何映射与防御？
▼

**战术总览**

T1566（Phishing）是 MITRE ATT&CK 中通过钓鱼邮件投递恶意载荷的战术，是初始访问（TA0001）的主要手段。其子技术描述三类投递载体，对应不同的检测与阻断策略，便于在检测工程中对齐覆盖度。

**T1566.001 鱼叉附件**

在邮件中携带恶意附件（带宏的 Office 文档、PDF、压缩包、HTML）。防御：邮件安全网关对附件做多引擎与沙箱（detonation）动态分析、阻断危险文件类型、启用宏策略（默认禁用）、对脚本容器（`.js/.hta/.iso`）重点告警。

**T1566.002 鱼叉链接**

诱导点击恶意链接（托管凭证钓鱼页或漏洞利用）。防御：URL 改写与实时信誉/分类检查、点击时再判定（时间差防御）、隔离可疑链接、结合品牌冒充检测与 DMARC 对齐校验阻断伪造发件人。

**T1566.003 服务性钓鱼**

借用可信第三方服务（云盘、SaaS 通知、文件共享）绕过信誉与过滤。防御：对已知 SaaS 域名做内容级检查而非单纯放行、检测异常共享与 OAuth 授权请求、通过安全意识培训识别伪装通知。

**映射与度量**

将每条检测/阻断规则映射到具体子技术，并在 SIEM/SOAR 中统计各子技术的命中与处置率。身份认证侧（SPF/DKIM/DMARC）抑制伪造，是降低 T1566 成功率的基础防线。

参考：MITRE ATT&CK T1566（Phishing）及子技术 T1566.001/002/003、NIST SP 800-61《计算机安全事件处理指南》、NIST SP 800-92《日志管理指南》。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mitre-attack-t1566-email-mapping.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
