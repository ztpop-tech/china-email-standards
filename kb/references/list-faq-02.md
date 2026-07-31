---
title: "List-Unsubscribe 头与“一键退订”是什么？RFC 8058 做了什么改进？"
source: "https://ztpop.net/kb/list-faq-02.html"
license: CC-BY 4.0
---

# List-Unsubscribe 头与“一键退订”是什么？RFC 8058 做了什么改进？

1
List-Unsubscribe 头与“一键退订”是什么？RFC 8058 做了什么改进？
▼

**基础机制**

RFC 2369 的 List-Unsubscribe 头给出一个或多个退订 URI（通常是 mailto: 或 https: 链接），告诉收件方如何退订该列表。

**RFC 8058 的 POST 方法**

传统 mailto 退订需要用户发邮件，体验差且易被忽略。RFC 8058 允许在 List-Unsubscribe-Post 头配合下，用一次 HTTPS POST 请求完成退订，邮件客户端可显示一个“一键退订”按钮，无需离开收件箱。

**必填趋势**

主流邮箱服务商已将 List-Unsubscribe（尤其一键 POST）作为批量发送的送达率前置条件之一；缺失或不生效会拉低信誉、增加进垃圾箱概率。

参考：RFC 2369；RFC 8058（一键退订）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/list-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
