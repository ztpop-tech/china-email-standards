---
title: "仿冒域名（Lookalike Domain）如何检测与拦截？"
source: "https://ztpop.net/kb/lookalike-domain-detection.html"
license: CC-BY 4.0
---

# 仿冒域名（Lookalike Domain）如何检测与拦截？

1
仿冒域名（Lookalike Domain）如何检测与拦截？
▼

**仿冒域名的构造**

仿冒域名（Lookalike / Typosquatting Domain）用细微差异冒充正品：字符替换（`rn` 代替 `m`）、插入/删除字符（`ztpop-secure`）、TLD 替换（`.com`→`.co`）、以及同形异义字（homoglyph，如西里尔 `о` 混入拉丁 `o`，经 Punycode 编码为 `xn--...`）。

真实攻击：攻击者批量注册数十个变体域名，用于钓鱼邮件发件域、伪造登录页托管或品牌污名化；证书透明日志（CT Log）会记录其申请 TLS 证书的行为，成为可观测线索。

**检测方法**

* **同形解码**：将域名 Punycode 解码，比对 Unicode 混淆字符是否映射到品牌字母。
* **编辑距离**：计算与品牌域名的 Levenshtein 距离，低于阈值即疑似仿冒。
* **证书透明日志**：订阅 CT Log，对新签发含品牌关键词的证书实时告警。
* **被动 DNS / 威胁情报**：关联新域名的解析 IP、历史声誉与已知恶意集群。

**拦截与缓解**

* **主动防御注册**：提前注册核心变体域名收归己有，缩小可被滥用的空间。
* **阻断**：将确认仿冒域名注入邮件网关与 Web 代理黑名单，浏览器侧对 homoglyph 域名提示。
* **认证**：DMARC 拒绝伪造发件，使仿冒域名难以成功投递钓鱼邮件。
* **下线**：通过注册商/托管商 Abuse 流程与法务渠道申请撤销。

参考：CISA 品牌仿冒域名预警、APWG 反钓鱼建议、ICANN 同形异义字安全报告、MITRE ATT&CK T1637（Phishing: Domain）。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/lookalike-domain-detection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
