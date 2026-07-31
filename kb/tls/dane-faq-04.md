---
title: "TLSA 的 certificate usage（证书用法 0/1/2/3）各代表什么？"
source: "https://ztpop.net/kb/dane-faq-04.html"
license: CC-BY 4.0
---

# TLSA 的 certificate usage（证书用法 0/1/2/3）各代表什么？

1
TLSA 的 certificate usage（证书用法 0/1/2/3）各代表什么？
▼

**四种用法**

`0 PKIX-TA`：信任的 CA 锚（公共 CA 体系）；`1 PKIX-EE`：被公共 CA 签发的终端实体证书；`2 DANE-TA`：由 TLSA 声明的私有 CA 锚；`3 DANE-EE`：声明“确切的终端实体证书”（不依赖任何 CA）。

**取舍**

用法 0/1 仍走公共 CA 路径（只是加了 DNS 约束）；用法 2/3 完全脱离公共 CA，是 DANE 最具价值的模式——尤其 `3 DANE-EE`，直接锁定具体证书。

参考：RFC 6698（Certificate Usage 枚举）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-faq-04.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
