---
title: "Authentication-Results 信头如何解读与判定？"
source: "https://ztpop.net/kb/authentication-results-header-parse.html"
license: CC-BY 4.0
---

# Authentication-Results 信头如何解读与判定？

1
Authentication-Results 信头如何解读与判定？
▼

**头部结构**

格式为 `Authentication-Results: authserv-id; method=result; properties`。其中 `authserv-id` 是填写该头的组织标识，下游判定时应只信任**本域自己网关**所写的结果，忽略外部邮件中夹带的同名头，以防伪造误导。

**方法与结果枚举**

常见方法：

* `spf`：结果有 none/pass/neutral/fail/softfail/temperror/permerror；
* `dkim`：结果有 none/pass/fail/neutral/policy/error；可带 `header.d=` 域名与 `header.i=` 标识域；
* `dmarc`：结果有 none/pass/fail，并附 `action=` 处置。

**判定要点**

示例：`Authentication-Results: mx.y.com; spf=pass smtp.mailfrom=x.com; dkim=pass header.d=x.com; dmarc=pass header.from=x.com`。三项均 pass 表示身份对齐良好。若 `dkim=fail` 但 `spf=pass`，需看 DMARC 是否仍放行（取决于对齐方式）。注意结果为 `none` 仅代表未做校验，不等于失败。

参考：RFC 8601《Message Header Field for Indicating Message Authentication Status》（取代 RFC 7001/7601）、RFC 7208 SPF、RFC 6376 DKIM、RFC 7489 DMARC。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/authentication-results-header-parse.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
