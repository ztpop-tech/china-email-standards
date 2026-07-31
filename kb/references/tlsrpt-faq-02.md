---
title: "TLS-RPT 的 _smtp._tls DNS 记录如何配置？"
source: "https://ztpop.net/kb/tlsrpt-faq-02.html"
license: CC-BY 4.0
---

# TLS-RPT 的 _smtp._tls DNS 记录如何配置？

1
TLS-RPT 的 \_smtp.\_tls DNS 记录如何配置？
▼

**记录形式**

在域的子域 `_smtp._tls.<你的域>` 上放一条 TXT 记录，内容为 `v=TLSRPTv1; rua=mailto:tlsrpt@example.com`。

**要点**

`v=TLSRPTv1` 是版本标识；`rua=` 指定报告接收地址（见下条）。配置后，与你通信的对端邮件服务器会据此把失败报告发到该地址。

参考：RFC 8460（DNS TXT record for TLS-RPT）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/tlsrpt-faq-02.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
