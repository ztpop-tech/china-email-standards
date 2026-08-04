---
title: "RFC 8460 TLS-RPT 的策略记录与 JSON 报告格式是怎样定义的？"
source: "https://ztpop.net/kb/rfc8460-tlsrpt-report-schema.html"
license: CC-BY 4.0
---

# RFC 8460 TLS-RPT 的策略记录与 JSON 报告格式是怎样定义的？

1
RFC 8460 TLS-RPT 的策略记录与 JSON 报告格式是怎样定义的？
▼

**策略记录：\_smtp.\_tls TXT**

RFC 8460 §3 规定，收报策略发布在策略域名的 `_smtp._tls` 子域下。例如策略域为 `example.com` 时，查询名为 `_smtp._tls.example.com`。记录的形式化定义要求以 `v=TLSRPTv1` 开头，并携带 `rua=` 标签指定收报端点。**若解析器返回多条 `_smtp._tls` TXT 记录，不以 `v=TLSRPTv1;` 开头的记录一律丢弃**。§3.1 给出两种典型发布方式：

```
_smtp._tls.example.com. IN TXT "v=TLSRPTv1;rua=mailto:reports@example.com"
_smtp._tls.example.com. IN TXT "v=TLSRPTv1; rua=https://reporting.example.com/v1/tlsrpt"
```

**报告 JSON 的顶层字段（§4.4）**

报告为 JSON 文档，关键字段含义如下：

* `organization-name`：出具报告的组织名称，字符串。
* `date-time`：报告时间区间起止，按 RFC 3339 §5.6 的「Internet Date/Time Format」表示；**报告区间应为完整 UTC 日（00:00–24:00）**。
* `contact-info` / `email-address`：报告责任方联系邮箱，按 RFC 5322 §3.4.1 的 addr-spec 格式。
* `report-id`：报告唯一标识，生成方案由出报方自定。
* `policy-type`：发送域实际套用的策略类型，目前**仅三个合法取值**：`tlsa`、`sts`、以及字面量 `no-policy-found`。
* `policy-string`：所应用策略的编码，以 JSON 字符串数组呈现，既可能是 TLSA 记录（RFC 6698 §2.3），也可能是 MTA-STS 策略。
* `domain`：MTA-STS 或 DANE 策略所针对的策略域；国际化域名（RFC 5891）**MUST 使用 Punycode A-label，不得用 U-label**。
* `mx-host-pattern`：`policy-type` 为 `sts` 时，策略中的 MX 主机名模式数组，按 RFC 8461 §4.1 的「MX Host Validation」规则解释。

**失败明细字段与结果类型（§4.3）**

每条失败明细包含 `result-type`、`sending-mta-ip`、`receiving-mx-hostname`、`receiving-mx-helo`、`receiving-ip`、`failed-session-count`、`additional-information`、`failure-reason-code`。结果类型初始集合分四类：

* **协商失败（§4.3.1）**：`starttls-not-supported`（对端 MX 不支持 STARTTLS）、`certificate-host-mismatch`（证书不符合 MTA-STS/DANE 约束，如 MX 主机名未出现在 SAN 中）、`certificate-expired`（证书过期）、`certificate-not-trusted`（涵盖不受信/未知 CA、名称约束、证书链错误等，使用时 SHOULD 以 `failure-reason-code` 补充细节）、`validation-failure`（不属于以上类别的通用失败，同样 SHOULD 补充原因码）。
* **DANE 相关策略失败（§4.3.2.1）**：`tlsa-invalid`（TLSA RRset 中无一条有效）、`dnssec-invalid`（递归解析器未返回有效记录）、`dane-required`（发送方按 RFC 7672 §6 的强制 DANE 配置要求目标域所有 MX 均有 TLSA，但报告所涉 MX 无经 DNSSEC 校验的 TLSA 记录）。
* 另有策略类（MTA-STS）失败、通用失败与瞬时失败（§4.3.2–4.3.4）。

**报告文件名与压缩（§5.1–5.2）**

推荐文件名 ABNF 为 `sender "!" policy-domain "!" begin-timestamp "!" end-timestamp [ "!" unique-id ] "." extension`。其中两个时间戳均为自 1970-01-01 00:00:00 UTC 起的秒数，分别标记报告区间起止；扩展名 **MUST 为 `json`（纯 JSON）或 `json.gz`（gzip 压缩）**；`unique-id` 可选，用于区分同一策略域在同一时刻由不同源并发产生的多份报告。示例：`mail.sndr.example.com!example.net!1470013207!1470186007!001.json.gz`。§5.2 强调无论走邮件还是 HTTPS 传输，报告都 SHOULD 做 gzip 压缩（RFC 1952）——不压缩容易超过接收方处理上限，**业界常见的接收上限约为 10 MB**。

参考：RFC 8460《SMTP TLS Reporting》，https://www.rfc-editor.org/rfc/rfc8460 —— 章节 3 / 3.1 / 4.3.1–4.3.4 / 4.4 / 5.1 / 5.2

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc8460-tlsrpt-report-schema.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
