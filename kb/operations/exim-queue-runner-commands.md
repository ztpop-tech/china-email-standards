---
title: "Exim 的队列运行（queue runner）相关命令怎么用（exim -q / -M / -qf 等）？"
source: "https://ztpop.net/kb/exim-queue-runner-commands.html"
license: CC-BY 4.0
---

# Exim 的队列运行（queue runner）相关命令怎么用（exim -q / -M / -qf 等）？

1
Exim 的队列运行（queue runner）相关命令怎么用（exim -q / -M / -qf 等）？
▼

**队列运行**

Exim 的队列由 queue runner 进程处理，也可手动触发。exim -q 启动一次队列运行尝试投递全部排队邮件；-q 常与时间间隔合用如 -q30m（每 30 分钟自动跑，由 daemon 负责）。

**强制与冻结**

exim -qf 强制运行队列，包括原本被冻结（frozen）的邮件；exim -qq 只跑队列、不尝试已软失败很久的邮件。

**单封操作**

exim -M <message-id> 立即尝试投递指定邮件；exim -Mrm <id> 从队列删除；exim -Mf <id> 强制解冻并重投；exim -Mg <id> 生成可投递报告。

**查看与注意**

exim -bp（同 mailq）列出队列；exim -bpc 计数；exim -bpr 详细。frozen 邮件通常因反复软失败或无法路由被冻结以免反复重试；先查原因（DNS/对方拒收）再 -Mf 强投。

参考：Exim 官方文档（queue runner：-q / -qf / -M 系列）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exim-queue-runner-commands.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
