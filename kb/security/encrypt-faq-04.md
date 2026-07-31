---
title: "PGP / OpenPGP / GPG 是什么？Web of Trust 与密钥分发如何运作？"
source: "https://ztpop.net/kb/encrypt-faq-04.html"
license: CC-BY 4.0
---

# PGP / OpenPGP / GPG 是什么？Web of Trust 与密钥分发如何运作？

1
PGP / OpenPGP / GPG 是什么？Web of Trust 与密钥分发如何运作？
▼

**定义**

PGP（Pretty Good Privacy）及其开放标准 OpenPGP（RFC 4880）是另一套端到端邮件加密体系，实现邮件与文件的加密与签名，常见实现为 GnuPG（GPG）。

**Web of Trust（信任网）**

与 S/MIME 依赖层级 CA 不同，OpenPGP 采用去中心化的“信任网”：用户之间互相签名彼此的公钥，形成信任关系链。你越信任的人的签名，越能让你相信某个陌生密钥确实属于其人。

**密钥分发**

公钥通常发布到公开密钥服务器（keyserver）或直接在沟通中交换指纹（fingerprint）。验证时需比对指纹，防止中间人替换公钥。

参考：RFC 4880（OpenPGP）；GnuPG 文档

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/encrypt-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
