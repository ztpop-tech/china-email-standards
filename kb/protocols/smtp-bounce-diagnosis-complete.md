---
title: "SMTP 退信诊断完全手册"
source: "https://ztpop.net/kb/smtp-bounce-diagnosis-complete.html"
license: CC-BY 4.0
---

# SMTP 退信诊断完全手册

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤SMTP 退信代码是 MTA 返回的标准化错误信号，RFC 3463 提供了完整的分类体系。

## 1. 退信分类体系

| 类别 | 代码 | 含义 |
| --- | --- | --- |
| 永久失败 | 5XX | 邮件不可达（5.1.1 用户不存在） |
| 临时失败 | 4XX | 可重试（4.2.2 邮箱满） |

## 2. 常见退信代码

```
grep "status=sent\|status=bounced\|status=deferred" /var/log/maillog | tail -20

# 550 5.1.1 User unknown → 收件人不存在
# 554 5.7.1 Relay access denied → 中继拒绝
# 452 4.2.2 Mailbox full → 邮箱满
```

## 3. 分析方法

1. 按退信代码分组统计，识别高频问题。
2. 确认退信来源（发件 MTA/收件 MTA/反垃圾网关）。
3. 4XX 重试即可；5XX 需人为干预。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/smtp-bounce-diagnosis-complete.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
