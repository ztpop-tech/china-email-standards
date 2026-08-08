---
title: "SPF 校验结果里的 neutral / permerror / temperror 各是什么意思？"
source: "https://ztpop.net/kb/spf-result-codes-neutral-permerror-temperror.html"
license: CC-BY 4.0
---

# SPF 校验结果里的 neutral / permerror / temperror 各是什么意思？

1
SPF 校验结果里的 neutral / permerror / temperror 各是什么意思？
▼

**结果码总览**

RFC 7208 定义了 SPF 校验结果码（§2.6 与 §4 处理语义）。常见值：none（域无 SPF 记录或无可匹配记录）、neutral（?all，明确"不授权也不否认"）、pass（发送 IP 在授权范围内）、fail（-all，未授权，应拒绝/标记）、softfail（~all，弱否定，通常标记而非拒绝）。

**permerror**

永久错误。例如 DNS 记录语法错误或超出机制数量限制（RFC 7208 §4.6 限制单次评估最多 10 次 DNS 查询等）。接收方应把 permerror 当作 none 类处理，并可触发告警以便域主修复记录。

**temperror**

临时错误，如 DNS 解析超时、记录暂时不可读。RFC 7208 §4.7 建议可稍后重试，不应仅因 temperror 就直接拒绝邮件（避免把临时故障变成丢信）。

参考：RFC 7208 §2.6 / §4.6 / §4.7

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spf-result-codes-neutral-permerror-temperror.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
