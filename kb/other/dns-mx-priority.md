---
title: "MX 记录的优先级（Preference）如何工作？多 MX 如何实现容灾？"
source: "https://ztpop.net/kb/dns-mx-priority.html"
license: CC-BY 4.0
---

# MX 记录的优先级（Preference）如何工作？多 MX 如何实现容灾？

1
MX 记录的优先级（Preference）如何工作？多 MX 如何实现容灾？
▼

**定义**

MX 记录带一个 16 位整数“优先级（preference）”，值越小越优先。发信方先尝试优先级最低（数字最小）的 MX，失败再试次小的，直到成功或列表用尽。

**容灾**

典型配置：主 MX（如 10）指向主邮件服务器，备 MX（如 20/30）指向灾备/第三方中继；主宕机时自动流向备，保证入站不丢信（备机排队等主恢复再转发）。

**注意**

优先级只决定“尝试顺序”，不代表“主备身份”由 DNS 定义；所有列出的 MX 都应能最终投递到同一域，否则备机拒收会退信。

**运维**

改 MX 注意 TTL 缓存；新增备 MX 要确保它能正确路由到本域邮箱，且不被当作开放中继。

参考：RFC 5321 §5.1（MX 查找与优先级）；RFC 1035（DNS MX 记录）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dns-mx-priority.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
