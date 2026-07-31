---
title: "DKIM 密钥如何平滑轮转（key rotation）？OpenDKIM 怎么做？"
source: "https://ztpop.net/kb/opendkim-faq-07.html"
license: CC-BY 4.0
---

# DKIM 密钥如何平滑轮转（key rotation）？OpenDKIM 怎么做？

1
DKIM 密钥如何平滑轮转（key rotation）？OpenDKIM 怎么做？
▼

**为何轮转**

DKIM 私钥长期不变会增加泄露风险，应定期轮换；但密钥一旦更换，仍缓存旧公钥的对端可能验证失败，因此需要在不中断邮件的前提下过渡。

**双选择器并行**

OpenDKIM 通过不同选择器（如 sel1 / sel2）实现零中断轮转：先在 DNS 发布新选择器对应的新公钥，将 MTA 改为用新选择器签名，旧选择器（旧密钥）保留一段时间后再撤销。

**并行期与权限**

双选择器并行期间，无论对端缓存哪把公钥都能验证通过。私钥文件权限须严格（仅 milter 运行用户可读），轮转完成后及时下线旧密钥以降低泄露面。

参考：RFC 6376（DKIM 密钥轮转）；OpenDKIM 文档

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
