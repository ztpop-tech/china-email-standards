---
title: "邮件炸弹和目录收集攻击是什么？邮件服务器该怎样抵御？"
source: "https://ztpop.net/kb/email-bomb-directory-harvest-defense.html"
license: CC-BY 4.0
---

# 邮件炸弹和目录收集攻击是什么？邮件服务器该怎样抵御？

1
邮件炸弹和目录收集攻击是什么？邮件服务器该怎样抵御？
▼

**目录收集攻击（DHA）**

目录收集攻击指攻击者用 SMTP 的 VRFY/EXPN 命令批量为探，判断哪些地址有效。RFC 2505 第 2.11 节（SMTP VRFY and EXPN）明确指出：VRFY 与 EXPN 给垃圾邮件发送者提供了测试地址是否有效（VRFY）、甚至获取更多地址（EXPN）的手段；因此 MTA **应当（SHOULD）**控制谁可使用这两者，EXPN 的默认设置应为「关闭（off）」，VRFY 也应受限。切断 VRFY/EXPN 即切断了目录收集的主要信息源。

**邮件炸弹（Email Bomb）**

邮件炸弹是向单一目标海量投递以制造拒绝服务（DoS）。RFC 2505 多处提示无限制的转发与验证会打开 DoS 攻击面：第 2 节开头、第 2.4 节、第 2.9 节，以及文献中第 233、237、646、875 行附近都指出，验证或转发若不设限会招致拒绝服务；第 2.1 节的中继限制、第 2.4 节的记录、第 2.10 节验证 local-part，都能减少被当作放大器的风险。

**服务器侧防御手段**

对应 RFC 2505 的建议：限制单封邮件大小与每连接/每账户的速率（节流），对验证失败（第 2.9、2.10 节）快速拒绝以减少握手开销，关闭对外的 VRFY/EXPN（第 2.11 节），对异常高量收件人或来源限速。这些措施使邮件炸弹难以打满存储与队列、使目录收集拿不到有效地址清单。

**放到现代体系里看**

RFC 2505 是反中继/反垃圾的建议性文件（BCP 30 的组成部分，性质为 informational），给出的是 MUST/SHOULD 级的运维实践，而非完备方案。实际部署应让这些基础限制与现代邮件网关的速率限制、信誉评分（DNSBL）、内容过滤与威胁情报联动，才能同时应对邮件炸弹与目录收集。

参考：https://www.rfc-editor.org/rfc/rfc2505.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-bomb-directory-harvest-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
