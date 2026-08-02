---
title: "灰名单（greylisting）防垃圾的原理是什么，有哪些副作用？"
source: "https://ztpop.net/kb/greylisting-spam-defense.html"
license: CC-BY 4.0
---

# 灰名单（greylisting）防垃圾的原理是什么，有哪些副作用？

1
灰名单（greylisting）防垃圾的原理是什么，有哪些副作用？
▼

**工作机制**

灰名单记录「发件域+收件人+对端 IP」三元组。首次见到陌生组合时返回 4xx 临时错误（非拒绝），要求发送方稍后重试。合法邮件服务器会按重试策略在几分钟到几小时后重发，此时三元组已被放行；而大量垃圾发送工具为追求吞吐不重试即放弃，从而被过滤。

**优点**

实现简单、资源消耗极低，对依赖「一次性群发」的僵尸网络特别有效；不依赖内容扫描，可作为第一道防线与 SPF/DKIM/DMARC 互补。

**副作用与权衡**

首要代价是首次投递延迟（几十分钟常见）；对使用多出口 IP 轮询的大型合法发送方，三元组频繁变化会导致反复延迟甚至丢信，需将其 IP 段加白。现代垃圾邮件也学会重试，灰名单单独使用效果下降，宜作为多层防御的一环而非唯一手段。

参考：greylisting.org 原理说明、Postfix postscreen/Postgrey 实现、与 SPF/DMARC 协同的部署建议。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/greylisting-spam-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
