---
title: "邮件列表（Mailman / Google Groups / 企业列表）用什么头字段标识自己？List-Id 有什么用？"
source: "https://ztpop.net/kb/mailing-list-listid-rfc2919.html"
license: CC-BY 4.0
---

# 邮件列表（Mailman / Google Groups / 企业列表）用什么头字段标识自己？List-Id 有什么用？

1
邮件列表（Mailman / Google Groups / 企业列表）用什么头字段标识自己？List-Id 有什么用？
▼

**标准头**

RFC 2919 定义 List-Id 头，唯一标识一个邮件列表，形如 示例列表 ；RFC 2369 定义一组 List-\*（List-Post、List-Unsubscribe、List-Archive、List-Help 等）。

**List-Id 用途**

客户端与过滤器据 List-Id 把同一列表的邮件归类到文件夹、批量建规则、去重；比用 Subject 前缀可靠（主题可变，List-Id 稳定）。

**List-Unsubscribe 重点**

List-Unsubscribe（及 List-Unsubscribe-Post，RFC 8058）是“一键退订”的核心；邮件客户端据它显示退订按钮，Yahoo / Google 2024 新规要求大发送方必须提供且可用。

**运维**

列表服务器应正确注入这些头；网关 / 转发勿剥离 List-\*；发送营销或列表邮件必须含合规退订头，否则严重影响送达率。

参考：RFC 2919（List-Id）；RFC 2369（List-\*）；RFC 8058（List-Unsubscribe-Post）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailing-list-listid-rfc2919.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
