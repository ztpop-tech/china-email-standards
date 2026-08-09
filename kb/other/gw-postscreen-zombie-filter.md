---
title: "postscreen 前置过滤怎么配？哪些测试可以安全启用？"
source: "https://ztpop.net/kb/gw-postscreen-zombie-filter.html"
license: CC-BY 4.0
---

# postscreen 前置过滤怎么配？哪些测试可以安全启用？

**它解决的是「进程被占满」这个问题**

POSTSCREEN\_README 说明了 postscreen 的定位：在 smtpd 进程之前挡住大量来自僵尸网络的连接，避免这些连接占满有限的 smtpd 进程数，使合法邮件排不上队。它是容量保护手段，其次才是过滤手段。

重要限制：postscreen 只处理入站 25 端口，不应用于提交端口。提交端口面向的是已认证客户端，套用连接层的可疑性判定会造成误伤。

**两类测试的风险完全不同**

连接前测试（pregreet、dnsbl、blacklist）在客户端发出任何命令之前即可判定，不会中断合法会话，误判成本低，适合直接启用。

连接后深度测试（pipelining、non-SMTP command、bare newline）需要观察客户端行为，一旦触发会要求客户端断开并稍后重连——POSTSCREEN\_README 明确指出，这类测试会给合法邮件带来延迟，因此不建议对未加白的合法发送方长期开启。

落地建议：连接前测试设为 `enforce`，连接后深度测试初期设为 `ignore` 或仅记录，确认误判可控后再逐项收紧。

**pregreet 与 DNSBL 的加权**

pregreet 利用了 RFC 5321 的会话规则：客户端必须等待服务端的 220 问候后才能发送命令。postscreen 故意延迟完整问候，抢先说话的客户端即判定为违规——这条对批量发送工具命中率很高，且几乎不会误伤实现规范的 MTA。

DNSBL 部分用 `postscreen_dnsbl_sites` 配置，可为每个站点设置权重（如 `zen.example.org*2`），再用 `postscreen_dnsbl_threshold` 设总分阈值。多源加权比单源硬拒更稳健：任何单一列表都可能出现误列，加权后单源误列不足以致拒。

同时用 `postscreen_dnsbl_whitelist_threshold` 配置负权重的白名单源，让高信誉发送方直接跳过后续测试。

**缓存与白名单**

通过测试的客户端会被写入 `postscreen_cache_map`，在有效期内直接放行，避免每次连接重复检测。有效期由各测试的 `*_ttl` 参数控制。缓存文件应放在持久化路径下，重启后不丢失，否则重启瞬间会出现一波集中重测。

永久白名单用 `postscreen_access_list` 指定，把内部中继、监控探针、以及确认可信的对端网段列入。这份清单要纳入变更管理——它是绕过全部前置检测的通道。

**分阶段上线与观测**

第一阶段全部测试设为 `ignore`，只记录日志，跑满一个完整周期，统计各测试的命中量与命中源；第二阶段把 pregreet 与 dnsbl 改为 `enforce`，观察是否有已知合法源被拒；第三阶段再评估深度测试。

观测指标：被 postscreen 拒绝的连接占入站连接总数的比例、smtpd 进程占用峰值的变化、以及白名单命中率。若启用后 smtpd 峰值占用没有明显下降，说明真正的压力不在僵尸网络连接上，应重新定位瓶颈而不是继续加严规则。

参考：[Postfix POSTSCREEN\_README](https://www.postfix.org/POSTSCREEN_README.html) ｜ [Postfix postconf(5) 配置参数手册](https://www.postfix.org/postconf.5.html) ｜ [RFC 5321 Simple Mail Transfer Protocol](https://www.rfc-editor.org/rfc/rfc5321.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-postscreen-zombie-filter.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
