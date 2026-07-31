---
title: "Postfix 报错“fatal: unknown service: smtp/tcp”是哪里出了问题？"
source: "https://ztpop.net/kb/postfix-faq-06.html"
license: CC-BY 4.0
---

# Postfix 报错“fatal: unknown service: smtp/tcp”是哪里出了问题？

1
Postfix 报错“fatal: unknown service: smtp/tcp”是哪里出了问题？
▼

**原因**

Postfix 在 /etc/services 中查不到 smtp 服务条目（或名称服务缓存异常），无法把 smtp/tcp 解析为端口 25。

**解决**

确认 /etc/services 含 “smtp 25/tcp” 一行；若使用了 nscd 等缓存服务，重启使其重新加载服务数据库。

参考：Postfix FAQ “What does fatal: unknown service: smtp/tcp mean?”

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/postfix-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
