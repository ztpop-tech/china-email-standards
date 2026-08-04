---
title: "IMAP QUOTA 扩展（RFC 9208）如何工作？"
source: "https://ztpop.net/kb/rfc9208-imap-quota.html"
license: CC-BY 4.0
---

# IMAP QUOTA 扩展（RFC 9208）如何工作？

1
IMAP QUOTA 扩展（RFC 9208）如何工作？
▼

**概述与能力**

§1：RFC 9208 定义对 IMAP（RFC 3501/9051）的若干扩展，用于查询与操纵管理性资源使用上限（配额），取代 RFC 2087。§3.1.1：支持的资源名须以 `QUOTA=RES-` 前缀作为能力通告（如 `QUOTA=RES-STORAGE`）；设置能力为 `QUOTASET`——SETQUOTA 命令要求服务器通告该能力。

**命令**

§4.1 定义命令：`GETQUOTA`（参数 quota root，返回 QUOTA 响应）、`GETQUOTAROOT`（参数邮箱名，返回 QUOTAROOT 与 QUOTA 响应）、`SETQUOTA`（参数 quota root 与资源上限列表，需 QUOTASET）。§4.1.4 还为 STATUS 新增 `DELETED` 与 `DELETED-STORAGE` 两个属性。

**资源类型**

§5 列出资源：`STORAGE`（物理空间估计，单位 1024 octets，能力 QUOTA=RES-STORAGE）、`MESSAGE`（邮件数）、`MAILBOX`（邮箱数）、`ANNOTATION-STORAGE`（注释最大大小，单位 1024 octets）。每种资源对应一个 QUOTA=RES-<name> 能力。

**响应与超额处理**

§4.2：`QUOTA` 响应携带 quota root 名与各资源的（名称、usage、limit）三元组；`QUOTAROOT` 响应携带邮箱名与零或多个 quota root 名。§4.3.1：当 APPEND/COPY/MOVE 导致超额时，服务器在 NO 响应中返回 `OVERQUOTA` 响应码（如 `A003 NO [OVERQUOTA] APPEND Failed`）。

参考：RFC 9208（IMAP QUOTA Extension），https://www.rfc-editor.org/rfc/rfc9208 —— 章节 1 / 3.1.1 / 4.1 / 4.2 / 4.3 / 5（注：RFC 9208 实为 IMAP QUOTA 扩展，并非 Sieve 扩展，本篇按真实主题撰写）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc9208-imap-quota.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
