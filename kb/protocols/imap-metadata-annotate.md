---
title: "IMAP 的 METADATA / ANNOTATE（RFC 5464/5257）能存“邮件/文件夹的自定义元数据”吗？"
source: "https://ztpop.net/kb/imap-metadata-annotate.html"
license: CC-BY 4.0
---

# IMAP 的 METADATA / ANNOTATE（RFC 5464/5257）能存“邮件/文件夹的自定义元数据”吗？

1
IMAP 的 METADATA / ANNOTATE（RFC 5464/5257）能存“邮件/文件夹的自定义元数据”吗？
▼

**机制**

IMAP METADATA 扩展（RFC 5464）允许在“服务器/邮箱/邮件”上存键值对注解（annotation），如“颜色标记、备注、共享注释”，由服务器统一管理。

**场景**

多客户端同步“私有/共享元数据”：例如把某封邮件标为“待法务复核”的注释、文件夹的显示名/图标，跨设备一致，不依赖本地存储。

**权限**

注解可分 私有（/private）与 共享（/shared）两类；共享注解需 ACL 权限（见 RFC 4314），避免越权读写。

**实践**

邮件系统支持 METADATA 后，高级客户端可做“服务端笔记/分类同步”；实现需注意配额与滥用（注解体积/数量限制）。

参考：RFC 5464（IMAP METADATA 扩展）；RFC 5257（ANNOTATE 旧草案，被 5464 体系吸收）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-metadata-annotate.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
