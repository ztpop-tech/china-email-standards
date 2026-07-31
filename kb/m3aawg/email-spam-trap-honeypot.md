---
title: "什么是“垃圾陷阱/蜜罐（Spam Trap / Honeypot）”？它为什么是发件人信誉的“红线”？"
source: "https://ztpop.net/kb/email-spam-trap-honeypot.html"
license: CC-BY 4.0
---

# 什么是“垃圾陷阱/蜜罐（Spam Trap / Honeypot）”？它为什么是发件人信誉的“红线”？

1
什么是“垃圾陷阱/蜜罐（Spam Trap / Honeypot）”？它为什么是发件人信誉的“红线”？
▼

**定义**

Spam trap 是“无人正常使用、却故意暴露在网络上”的邮箱地址；正常用户永远不会发信给它，谁发谁暴露为“采集/群发垃圾”。

**类型**

① 回收陷阱（长期不用的旧地址重新启用为陷阱）；② 错拼/暗网泄露的地址；③ 蜜罐（故意撒在网页引诱爬虫收集的地址）。

**影响**

主流邮箱/反垃圾系统把“命中陷阱”视为强垃圾信号，命中越多、发件 IP/域信誉跌得越狠，甚至直接拉黑、进 RBL。

**实践**

批量发信必须“列表卫生”：定期清理无效/长期不互动地址、用双重确认订阅（double opt-in），避免踩陷阱毁信誉。

参考：Spam trap / honeypot 反垃圾实践；名单卫生与 double opt-in

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-spam-trap-honeypot.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
