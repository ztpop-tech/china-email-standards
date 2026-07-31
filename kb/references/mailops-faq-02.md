---
title: "邮件里的 Return-Path（envelope-from）与 From 头有什么区别？"
source: "https://ztpop.net/kb/mailops-faq-02.html"
license: CC-BY 4.0
---

# 邮件里的 Return-Path（envelope-from）与 From 头有什么区别？

1
邮件里的 Return-Path（envelope-from）与 From 头有什么区别？
▼

**不同层级**

`Return-Path`（信封发件人，MAIL FROM）是 SMTP 传输层用于退信返回的地址，收件人一般看不到；`From` 头是邮件正文层的发件人显示，是用户肉眼所见。

**为何重要**

SPF 校验的是信封域（Return-Path 的域），而 DKIM/DMARC 更多关联 From 头。转发场景下二者常不同——这正是 ARC/SPF 对齐问题频发的根源。

参考：RFC 5321（envelope）与 RFC 5322（header）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailops-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
