---
title: "如何把 Postfix 配置成某远程站点的备份 MX（backup MX）？"
source: "https://ztpop.net/kb/postfix-faq-07.html"
license: CC-BY 4.0
---

# 如何把 Postfix 配置成某远程站点的备份 MX（backup MX）？

1
如何把 Postfix 配置成某远程站点的备份 MX（backup MX）？
▼

**步骤**

在 relay\_domains 中加入该域，启用 permit\_mx\_backup，并用 relay\_recipient\_maps 列出合法收件人；主 MX 不可达时邮件暂存于本机，恢复后转发。

**注意**

务必配 relay\_recipient\_maps，否则可能被当作开放中继滥用。

参考：Postfix FAQ “Configuring Postfix as MX host for a remote site”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-faq-07.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
