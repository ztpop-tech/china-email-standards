---
title: "如何调试 Exim 的 router / transport 匹配（用 -bt / -d）？"
source: "https://ztpop.net/kb/exim-router-transport-debug-bt.html"
license: CC-BY 4.0
---

# 如何调试 Exim 的 router / transport 匹配（用 -bt / -d）？

1
如何调试 Exim 的 router / transport 匹配（用 -bt / -d）？
▼

**-bt 地址测试**

运行 exim -bt user@domain 让 Exim 对该地址执行 router 选择，打印它命中了哪条 router、最终由哪个 transport 投递，以及任何 defer/redirect 信息，是最常用的"这封信会去哪"诊断。

**-d 调试输出**

exim -d<selector> 或 exim -d+all 打开调试；可针对路由阶段用 exim -bt -d+route user@domain 只看 router 决策细节。调试输出会显示每条 router 为何被跳过（条件不满足、域不匹配等）与最终命中。

**日志与实测**

实际投递可用 exim -v 看 SMTP 对话；结合 mainlog（如 /var/log/exim4/mainlog）看 delivery 记录与 transport 返回。-bt 只读不发送，安全。

**注意**

调试输出可能含敏感信息，勿公开。

参考：Exim 官方文档（exim -bt / -d 调试 router 与 transport）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-router-transport-debug-bt.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
