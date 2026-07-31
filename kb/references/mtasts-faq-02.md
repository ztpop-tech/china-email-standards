---
title: "MTA-STS 的 _mta-sts DNS 记录是什么、应如何配置？"
source: "https://ztpop.net/kb/mtasts-faq-02.html"
license: CC-BY 4.0
---

# MTA-STS 的 _mta-sts DNS 记录是什么、应如何配置？

1
MTA-STS 的 \_mta-sts DNS 记录是什么、应如何配置？
▼

**记录形式**

需在域下创建名为 `_mta-sts` 的 DNS 记录（通常 CNAME 到服务商提供的记录，例如 Cloudflare 的 `_mta-sts.mx.cloudflare.net`），并关闭代理模式。

**TXT 内容**

该记录对应的 TXT 形如 `v=STSv1; id=20230615T153000;`，其中 `id` 是策略版本标识。它向尝试连接我方的发送方表明：本域支持 MTA-STS。

参考：Cloudflare “Configure MTA-STS”（\_mta-sts CNAME + TXT v=STSv1）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mtasts-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
