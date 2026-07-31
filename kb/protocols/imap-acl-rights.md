---
title: "IMAP 的 ACL（访问控制列表，RFC 4314）如何做“共享邮箱/文件夹授权”？"
source: "https://ztpop.net/kb/imap-acl-rights.html"
license: CC-BY 4.0
---

# IMAP 的 ACL（访问控制列表，RFC 4314）如何做“共享邮箱/文件夹授权”？

1
IMAP 的 ACL（访问控制列表，RFC 4314）如何做“共享邮箱/文件夹授权”？
▼

**机制**

IMAP ACL 扩展让所有者给其它用户授予“对某个邮箱的细粒度权限”：l(列表)/r(读)/s(写状态)/w(写标记)/i(插入)/p(发帖)/c(建子箱)/d(删信)/a(管理ACL) 等（RFC 4314）。

**共享场景**

支持邮箱/文件夹共享（如团队信箱、部门公共文件夹），所有者 SETACL 授权成员，成员按权限访问，比“共用密码”安全得多。

**操作**

SETACL/DELETEACL/GETACL/LISTRIGHTS 管理权限；a 权限（管理）应只给可信者。

**实践**

企业“共享信箱/公共文件夹”依赖 ACL；邮件系统对 ACL 的支持度决定团队邮箱、委托访问能否落地，需与后台账号体系联动。

参考：RFC 4314（IMAP ACL 扩展）；RFC 2086（原 ACL，被 4314 更新）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-acl-rights.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
