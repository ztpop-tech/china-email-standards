---
title: "Google Workspace 的“拆分递送（Split delivery）”与“双重递送（Dual delivery）”有何区别，怎么配？"
source: "https://ztpop.net/kb/google-workspace-split-delivery-dual-delivery.html"
license: CC-BY 4.0
---

# Google Workspace 的“拆分递送（Split delivery）”与“双重递送（Dual delivery）”有何区别，怎么配？

1
Google Workspace 的“拆分递送（Split delivery）”与“双重递送（Dual delivery）”有何区别，怎么配？
▼

**二者定位**

都属于 Gmail 邮件路由（Routing）能力，用于让同一域的邮件同时涉及 Gmail 与另一套邮件系统（如本地旧服务器）。

**拆分递送**

同一域内，部分用户用 Gmail、部分用另一系统。做法是先把 MX 指向 Google，再在 Routing 加规则：对 Inbound 消息选 Modify message › Change route 到你在 Hosts 中定义的非 Gmail 服务器，并在"账户类型"里只勾选 All inactive and unrecognized accounts（未识别/停用地址），使未知收件人转发到旧服务器。典型场景是 Gmail 与本地服务器混合迁移。

**双重递送**

同一用户同时收到 Gmail 与另一邮箱的副本。通常走 Default routing 设置 dual delivery，把邮件既投递到 Gmail 又复制到另一系统。

**关键差异与注意**

拆分 = 按收件人分流（一个地址只去一边）；双重 = 同一地址两边都收。MX 必须指向 Google 才由 Gmail 先处理；旧服务器要配为入站网关提升 SPF 准确性；SPF 记录需同时包含两边服务器。

参考：Google Workspace Help · 2685650 / 12971016 / 9228551

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/google-workspace-split-delivery-dual-delivery.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
