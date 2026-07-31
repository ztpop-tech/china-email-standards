---
title: "Yahoo 为何要求一键退订（RFC 8058）？退订须在多久内处理？"
source: "https://ztpop.net/kb/yahoo-faq-03.html"
license: CC-BY 4.0
---

# Yahoo 为何要求一键退订（RFC 8058）？退订须在多久内处理？

1
Yahoo 为何要求一键退订（RFC 8058）？退订须在多久内处理？
▼

**一键退订是强制项**

Yahoo 要求批量发送方支持可用的 List-Unsubscribe 头，对营销与订阅类邮件支持一键退订。Yahoo 高度推荐 RFC 8058 的 Post 方式（邮件头一键），mail-to: 方式也可接受；同时邮件正文须有清晰可见的退订链接（可指向偏好设置页）。

**处理时限**

退订请求须在 2 天内处理完毕。Yahoo 还要求退订流程明显可见、无需用户登录，以降低投诉率。

参考：Yahoo《Sender Best Practices》— Support easy unsubscribe (RFC 8058)；Additional Recommendations

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/yahoo-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
