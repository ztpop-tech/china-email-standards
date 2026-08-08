---
title: "MTA-STS 是什么？怎么部署才能强制对端用 TLS 加密投递我的邮件？"
source: "https://ztpop.net/kb/mta-sts-deployment.html"
license: CC-BY 4.0
---

# MTA-STS 是什么？怎么部署才能强制对端用 TLS 加密投递我的邮件？

1
MTA-STS 是什么？怎么部署才能强制对端用 TLS 加密投递我的邮件？
▼

**MTA-STS 解决什么**

RFC 8461 把 MTA-STS 定义为一种机制，让一个「策略域（Policy Domain）」对外声明自己支持 TLS，并承诺只接受来自策略所列邮件交换主机的邮件。关键点在于：**它不改变 MX 记录的 DNS 查找本身**，而是在 MX 解析完成之后叠加一层「必须使用 TLS，且只认这些 MX」的承诺（见 RFC 8461 第 1 节术语与第 3.1 节概述）。这样可把普通「尽力而为的 STARTTLS」升级为可被强制执行的加密策略。

**三个组成部分**

部署需要三件套：①一条名为「\_mta-sts」的 TXT 记录，携带版本与 id（用于让对端判断策略是否更新）；②一份放在 `https://mta-sts.<域>/.well-known/mta-sts.txt` 的策略文件（RFC 5785 的 well-known 路径）；③通过 HTTPS 传输策略。注意策略完整性依赖 Web PKI（CA 证书链），**不依赖 DNSSEC**——这是它与 DANE 的根本区别（RFC 8461 第 3.1、3.2、9.3 节）。

**策略文件字段**

RFC 8461 第 9.3 节（MTA-STS Policy Fields）规定策略含：**mode**（取 enforce、testing、none 之一）、**mx**（允许接收邮件的主机名列表，支持「\*.」通配前缀）、**max\_age**（策略缓存秒数）。典型策略形如「mode: enforce」后接若干「mx: mail.example.com」行。

**三种模式语义**

mode 决定对端行为（RFC 8461 第 3.2 节）：**enforce（强制）**——对端 MTA 必须走 TLS，且只可向策略列出的 MX 主机投递，否则拒收；**testing（测试）**——执行同样的校验但只生成报告、不拦截，用于上线前观察误伤；**none（关闭）**——不启用 MTA-STS 约束。建议先用 testing 观察，再切到 enforce。

**对端的校验流程**

发送方解析收件域 MX 后，拉取 mta-sts 策略并做「MX 主机校验」：RFC 8461 第 4.1 节要求，接收 MTA 在支持 MTA-STS 时**必须验证证书确实对该 MX 主机名有效，且投递目标 MX 必须在策略列表内**；任一不满足，则按 mode 处置（enforce 下拒收，testing 下仅记录）。对端据此在握手阶段发现降级或无 TLS 时直接失败，而非悄悄退回明文。

参考：https://www.rfc-editor.org/rfc/rfc8461.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mta-sts-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
