---
title: "OpenDMARC 的 PublicSuffixList 与 TrustedAuthRes 有什么用？"
source: "https://ztpop.net/kb/opendkim-faq-04.html"
license: CC-BY 4.0
---

# OpenDMARC 的 PublicSuffixList 与 TrustedAuthRes 有什么用？

1
OpenDMARC 的 PublicSuffixList 与 TrustedAuthRes 有什么用？
▼

**TrustedAuthRes（可信认证源）**

为防止下游或中间设备伪造认证结论，OpenDMARC 只信任由受信任的上游 MTA 注入的 Authentication-Results 头。TrustedAuthRes 列出允许信任的主机名/域名，其余来源的认证结果一律忽略，避免被伪造的 dkim=/spf= 骗过 DMARC 判定。

**PublicSuffixList（公共后缀列表）**

DMARC 对齐与子域策略（sp=）判定需要知道“组织域（org domain）”。PublicSuffixList 提供如 .co.uk、.com.cn 等公共后缀，使 OpenDMARC 能正确剥离到真正的注册域，避免把 a.b.example.com 的 DMARC 策略错误地应用到 example.com 的层级，也保证子域（sp）判定与对齐计算准确。

**运维建议**

两者都应按网络拓扑正确配置：TrustedAuthRes 仅列内部受控中继，PublicSuffixList 保持定期更新以覆盖新公共后缀。

参考：OpenDMARC 官方文档（TrustedAuthRes / PublicSuffixList）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
