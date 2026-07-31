---
title: "退信（bounce）里的 SMTP 代码 4xx 与 5xx 分别代表什么？"
source: "https://ztpop.net/kb/mailops-faq-01.html"
license: CC-BY 4.0
---

# 退信（bounce）里的 SMTP 代码 4xx 与 5xx 分别代表什么？

1
退信（bounce）里的 SMTP 代码 4xx 与 5xx 分别代表什么？
▼

**分类**

SMTP 回复码为三位数字：以 `4` 开头表示**临时失败（soft bounce）**，接收方建议发送方稍后重试；以 `5` 开头表示**永久失败（hard bounce）**，通常不应再重试。

**常见例子**

450/451 多为临时策略或连接问题；550 常见于“用户不存在/拒收”；552 多为邮件过大；554 常为策略拒绝或被列入黑名单。诊断时应结合增强状态码（如 5.1.1、5.7.1）与服务器提示文本。

参考：RFC 5321（SMTP 回复码）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailops-faq-01.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
