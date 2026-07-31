---
title: "DANE-TA（用法 2）与 DANE-EE（用法 3）有什么区别？"
source: "https://ztpop.net/kb/dane-faq-05.html"
license: CC-BY 4.0
---

# DANE-TA（用法 2）与 DANE-EE（用法 3）有什么区别？

1
DANE-TA（用法 2）与 DANE-EE（用法 3）有什么区别？
▼

**DANE-TA (2)**

TLSA 声明一个“受信任的私有 CA 锚”：凡是由该 CA 签发、且通过 DNSSEC 校验的证书都算数。适合用自有 CA 给多台服务器签发证书的场景。

**DANE-EE (3)**

TLSA 直接声明“本服务此刻应呈现的终端实体证书本身”（或其哈希）。只要握手证书与声明一致即信任，连私有 CA 都不需要。换证书时需同步更新 TLSA 记录。

参考：RFC 6698 第 4 节（证书用法语义）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
