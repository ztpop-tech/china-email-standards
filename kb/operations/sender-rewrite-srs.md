---
title: "SRS（Sender Rewriting Scheme）是什么？转发时为何要重写 Return-Path？"
source: "https://ztpop.net/kb/sender-rewrite-srs.html"
license: CC-BY 4.0
---

# SRS（Sender Rewriting Scheme）是什么？转发时为何要重写 Return-Path？

1
SRS（Sender Rewriting Scheme）是什么？转发时为何要重写 Return-Path？
▼

**背景**

SRS（Meng Wong 草案，非 RFC 标准但事实广泛部署）用于转发场景中重写 envelope-from（Return-Path），使 SPF 在转发后仍可能通过，并保留退信能正确回送原作者的能力。

**动机**

纯转发改 envelope-from 为转发方 IP 会使原域 SPF 失败；若不改写又无法把退信路由回原作者。SRS 用可逆编码把原 Return-Path 信息加密嵌进转发方地址。

**机制**

转发出向用转发域的 SRS 地址作 Return-Path（SPF 对其自己通过）；退信回到转发方后，反向解码还原原作者地址再转发回去。需转发方持有密钥防伪造。

**实践**

邮件列表/转发服务用 SRS 配合 DKIM 重签，缓解 SPF 在转发下的失败；注意 SRS 地址较长，部分老旧系统有长度限制，且仅为实践草案而非标准。

参考：SRS 草案（Meng Wong）；与 RFC 7208 SPF 转发问题相关

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/sender-rewrite-srs.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
