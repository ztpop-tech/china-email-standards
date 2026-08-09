---
title: "攻击者用不存在的子域发信怎么办？DMARC 的 np 标签解决什么问题？"
source: "https://ztpop.net/kb/ir-psd-dmarc-nonexistent-subdomain-2026.html"
license: CC-BY 4.0
---

# 攻击者用不存在的子域发信怎么办？DMARC 的 np 标签解决什么问题？

1
攻击者用不存在的子域发信怎么办？DMARC 的 np 标签解决什么问题？
▼

**问题场景**

攻击者常以本不存在的子域作为 From 域发信。这类子域没有任何 DNS 记录，自然也没有独立的 SPF/DKIM 配置，接收方在做 DMARC 求值时会回退到组织域或上级策略。若组织域策略较宽松，这类仿冒就可能被放行。

**np 标签的规范定义**

RFC 9091《Experimental Domain-Based Message Authentication, Reporting, and Conformance (DMARC) Extension for Public Suffix Domains》第 3.2 节（Changes in Section 6.3, "General Record Format"）对 DMARC 记录格式作出扩展，在 fo 标签之后引入新标签 np：其含义是「针对不存在的子域所请求的接收方策略」（Requested Mail Receiver policy for non-existent subdomains），为可选的纯文本标签，语法与 p 标签相同。

**与 p、sp 的优先关系——这是配置时最容易错的地方**

同样在第 3.2 节，规范同步修订了既有标签的表述：p 标签的说明改为「策略适用于被查询的域及其子域，除非子域策略已由 sp 或 np 标签明确指定」；sp 标签的说明改为「当 sp 标签缺失、且 np 标签缺失或不适用时，才必须对子域套用 p 标签所指定的策略」。即优先级为：针对不存在子域，np 优先于 sp，sp 又优先于 p。此外该节明确 np 标签在组织域或 PSD 的子域记录中会被忽略。

**配置示例与判定**

在组织域的 DMARC 记录中，可在保持既有 p 与 sp 不变的前提下追加 np，对不存在的子域直接请求最严策略。这样做的好处是：正常业务子域仍按 sp/p 处置，不受影响；而根本不存在的子域被单独收紧，攻击面直接关闭。配置后应通过聚合报告确认没有把实际在用但未登记的子域误判为不存在。

**注意其规范状态**

RFC 9091 的状态是 Experimental（实验性），这意味着不同接收方对 np 的支持程度不一致，不能假定所有接收方都会执行该标签。因此 np 应作为纵深防御的一层，而不能替代对组织域与在用子域本身的 SPF/DKIM/DMARC 基础配置。

**研判侧的用法**

在聚合报告中若发现大量以陌生子域为 From 的失败记录，先核对该子域是否为本方在用；确认不存在的，说明正被用于仿冒，除配置 np 外还应把该构造特征加入入站检测规则。

参考：[RFC 9091](https://www.rfc-editor.org/rfc/rfc9091.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ir-psd-dmarc-nonexistent-subdomain-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
