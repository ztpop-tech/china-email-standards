---
title: "灰名单（Greylisting）为什么能让大部分垃圾邮件自己消失？"
source: "https://ztpop.net/kb/greylisting-defence.html"
license: CC-BY 4.0
---

# 灰名单（Greylisting）为什么能让大部分垃圾邮件自己消失？

1
灰名单（Greylisting）为什么能让大部分垃圾邮件自己消失？
▼

灰名单（Greylisting，RFC 6647 记录其实践与问题）是 SMTP 层一道**低成本过滤**。

#### 一、工作步骤

* 首次见到陌生三元组 `(客户端IP, 信封发件人, 信封收件人)`，MTA 返回**临时错误 4xx** 拒收，但记录该元组。
* 符合规范的合法 MTA 会按重试策略**稍后重发**，此时元组已在「放行名单」，邮件被接受。
* 大量群发/僵尸程序不重试或短时间换 IP 猛发，**多数就此放弃**，垃圾流量显著下降。

#### 二、收益与代价

优点是不依赖内容扫描、几乎零误杀内容；代价是**首次投递延迟**（通常几分钟到半小时），且对「一次性成功投递即切换」的高质量垃圾源效果有限。常与 DNSBL、内容过滤组合使用。

#### 三、注意

灰名单依赖对方**遵守 SMTP 重试语义**，对大型正规发信平台通常无碍，但需为重要合作方的已知 IP 设白名单以免误延。

参考：https://www.rfc-editor.org/rfc/rfc6647

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/greylisting-defence.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
