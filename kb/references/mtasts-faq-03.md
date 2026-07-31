---
title: "MTA-STS 策略文件应放在哪里？为什么用 HTTPS 而不是 DNS？"
source: "https://ztpop.net/kb/mtasts-faq-03.html"
license: CC-BY 4.0
---

# MTA-STS 策略文件应放在哪里？为什么用 HTTPS 而不是 DNS？

1
MTA-STS 策略文件应放在哪里？为什么用 HTTPS 而不是 DNS？
▼

**位置**

策略文件须通过 `mta-sts.<你的域>` 这个 HTTPS 端点提供，路径为 `/.well-known/mta-sts.txt`。例如 `https://mta-sts.example.com/.well-known/mta-sts.txt`。

**为何 HTTPS**

之所以用 HTTPS 而非 DNS 直接承载策略，是因为并非所有域都部署了 DNSSEC；若仅靠 DNS，又会引入新的 MITM 攻击面。借助 HTTPS（依赖 Web PKI 证书链）可更可靠地证明策略真实性。

参考：Cloudflare “Configure MTA-STS”（serve policy over HTTPS）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mtasts-faq-03.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
