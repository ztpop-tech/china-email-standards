---
title: "邮件的“信封发件人(Mail From)”和“信头 From”是一回事吗？为何常不一致？"
source: "https://ztpop.net/kb/email-mail-from-vs-from.html"
license: CC-BY 4.0
---

# 邮件的“信封发件人(Mail From)”和“信头 From”是一回事吗？为何常不一致？

1
邮件的“信封发件人(Mail From)”和“信头 From”是一回事吗？为何常不一致？
▼

**两重身份**

Mail From（信封）是 SMTP 会话里 MAIL FROM 指定的“投递/退信地址”，收件人一般看不到；信头 From 是信里显示的“发件人”，用户看到的就是它。

**为何不同**

转发、邮件列表、外包发送会让两者不同：列表把 Mail From 改成列表域（便于退信管理），但 From 头保留原作者；DMARC 等认证正是校验“信头 From 与 SPF/DKIM 对齐”。

**影响**

退信发往 Mail From（或空发件人）；用户回复/显示看 From 头；垃圾常伪造 From 头而 Mail From 逼真，需靠认证区分。

**实践**

排查送达/退信要分清两者；DMARC 对齐看的是“信头 From 域”与 SPF/DKIM 域关系，不是 Mail From。

参考：RFC 5321（信封 vs 信头）；RFC 7489（DMARC 对齐基于信头 From）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-mail-from-vs-from.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
