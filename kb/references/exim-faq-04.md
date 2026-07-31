---
title: "Exim 无法路由到任何远程域，提示无法访问 DNS，怎么办？"
source: "https://ztpop.net/kb/exim-faq-04.html"
license: CC-BY 4.0
---

# Exim 无法路由到任何远程域，提示无法访问 DNS，怎么办？

1
Exim 无法路由到任何远程域，提示无法访问 DNS，怎么办？
▼

**排查**

运行 `exim -d+resolver -bt 远程地址`：`-d` 开启调试，附加 `+resolver` 会让 Exim 显示它构造的解析器查询及 DNS 查询结果。

**常见原因**

若看起来连不上任何名字服务器，请检查 `/etc/resolv.conf` 的内容与权限。确认其中配置了可达的 nameserver，且 Exim 运行用户有权读取该文件。

参考：Exim FAQ Q0012（exim.org/exim-html-4.40/doc/html/FAQ\_0.html）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
