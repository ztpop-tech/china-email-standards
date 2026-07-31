---
title: "邮件 Received 头链（Received header chain）是什么？如何用它做邮件溯源与取证？"
source: "https://ztpop.net/kb/received-header-chain.html"
license: CC-BY 4.0
---

# 邮件 Received 头链（Received header chain）是什么？如何用它做邮件溯源与取证？

1
邮件 Received 头链（Received header chain）是什么？如何用它做邮件溯源与取证？
▼

**结构**

每经过一个 MTA，接收方会在邮件顶部前插一条 Received 头（RFC 5321 §4.4），记录接收时间、收发双方主机名/IP、使用的协议（ESMTP/ESMTPS）、TLS 与认证标识等。从最新（最上）到最旧（最下）依次回溯，即构成“投递路径链”。

**溯源**

取证时自上而下读 Received：最上一条是最终接收方，最下一条通常是原始发件 MTA。通过 by/with/for/id 字段与 from/to 主机名，可重建邮件经过的每一跳，定位异常跳（如未加密、陌生 IP、伪造主机名）。

**关键字段**

from（上一跳自称）、by（本跳）、with（传输方式，ESMTPS 表示 TLS）、id（本跳队列 ID）、for（目标收件人）、date（接收时间，注意时区）；TLS 握手信息（cipher、verify=OK/FAIL）可佐证链路加密状态。

**注意**

Received 头由每跳 MTA 自行添加，可被伪造或被某些中继省略；应优先信任“你控制的边界网关”所加的第一条，结合 DKIM 签名域（签名覆盖原始头）与 SPF 路径交叉验证，避免被伪造头误导。

参考：RFC 5321 §4.4（Received 头规范）；DKIM（RFC 6376）签名头校验

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/received-header-chain.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
