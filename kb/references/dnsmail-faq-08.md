---
title: "如何用 dig / nslookup 排查邮件相关 DNS 问题？"
source: "https://ztpop.net/kb/dnsmail-faq-08.html"
license: CC-BY 4.0
---

# 如何用 dig / nslookup 排查邮件相关 DNS 问题？

1
如何用 dig / nslookup 排查邮件相关 DNS 问题？
▼

**查 MX**

dig MX example.com +short 可直接列出收件域的 MX 主机与优先级；确认返回的主机名存在且能解析到 IP（dig A mail.example.com）。

**查 SPF/DKIM/DMARC TXT**

dig TXT example.com 查看 SPF（v=spf1）；dig TXT \_dmarc.example.com 看 DMARC；dig TXT selector.\_domainkey.example.com 看 DKIM 公钥。注意 TXT 多段串接需合并解读。

**查反向 DNS**

dig -x  查看 PTR；再用 dig A  验证 FCrDNS 是否闭环。任何一步为空或不符，都可能导致送达或认证异常，应据此修正相应记录。

参考：dig/nslookup 使用手册；RFC 7208/6376（记录查询）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dnsmail-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
