---
title: "DMARC 失败报告（forensic / RUF）与 RUA 有什么区别？什么时候该用？"
source: "https://ztpop.net/kb/dmarc-forensic-report.html"
license: CC-BY 4.0
---

# DMARC 失败报告（forensic / RUF）与 RUA 有什么区别？什么时候该用？

1
DMARC 失败报告（forensic / RUF）与 RUA 有什么区别？什么时候该用？
▼

**区别**

RUA 是周期性聚合统计，不含具体邮件内容；RUF（forensic report，RFC 7489 §6.4，旧称 failure report）在 DMARC 失败时立即发送，并附带触发失败的原始邮件样本（经截断），便于定位攻击源。

**隐私与负载**

forensic 报告含用户邮件片段，数据敏感、体积大，多数运营商默认不发或不建议开启；RFC 6591 定义了报告生成扩展。

**使用建议**

仅在排查主动攻击或新部署验证阶段开启 ruf，并限制报告目标域（ruf 标签 + 指定地址）；生产环境通常只开 rua、关 ruf，以免泄漏隐私与浪费带宽。

**合规**

发送 forensic 须遵守 RFC 6587（传输）与各地隐私法，许多企业因此长期禁用 RUF。

参考：RFC 7489 §6.4（forensic 报告）；RFC 6591；RFC 6587

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-forensic-report.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
