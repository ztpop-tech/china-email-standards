---
title: "SPF 的“include 扁平化（flattening）”是什么？为什么大域名需要它？"
source: "https://ztpop.net/kb/email-spf-include-flattening.html"
license: CC-BY 4.0
---

# SPF 的“include 扁平化（flattening）”是什么？为什么大域名需要它？

1
SPF 的“include 扁平化（flattening）”是什么？为什么大域名需要它？
▼

**10 次查询上限**

SPF（RFC 7208）规定一次校验最多做 10 次 DNS 查询（含 include/redirect/a/mx 等），超出即 PermError（视为失败），邮件可能被拒。

**扁平化**

把多层 include 链“展开成一组 ip4/ip6 直写”到本域 SPF，减少嵌套查询数，避免触顶 10 次限制；需工具定期刷新（因上游 IP 会变）。

**权衡**

扁平化牺牲“上游变更自动同步”，要有人维护刷新；过度扁平还可能超 TXT 长度（DNS 单记录 ~255/总 450 字节软限）。

**实践**

第三方发信源很多（多 ESP/云）的域名容易超 10 查，用扁平化或“按功能拆子域各管 SPF”来控查询数。

参考：RFC 7208 §4.6（DNS 查询上限 10）；§8.1（限制实践）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-spf-include-flattening.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
