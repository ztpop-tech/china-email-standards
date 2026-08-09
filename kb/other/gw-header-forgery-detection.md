---
title: "邮件头伪造怎么识别？From 显示名和信封发件人不一致算不算问题？"
source: "https://ztpop.net/kb/gw-header-forgery-detection.html"
license: CC-BY 4.0
---

# 邮件头伪造怎么识别？From 显示名和信封发件人不一致算不算问题？

**先厘清三个「发件人」**

SMTP 信封中的 MAIL FROM（RFC 5321 路径，也叫 Return-Path）用于退信，是 SPF 校验的对象；RFC 5322 第 3.6.2 节定义的头部 `From:` 是用户看到的发件人；`Sender:` 在代发场景下标识实际提交者。

两者不一致本身完全合法且普遍存在——邮件列表、代发平台、转发都会造成不一致。所以「不一致」不能直接判定为伪造，真正的判定标准是 RFC 7489 的对齐：DMARC 要求头部 From 的域与通过校验的 SPF 域或 DKIM 签名域在组织域层面一致。不对齐且发送域发布了强制策略，才构成可处置的伪造证据。

**显示名欺骗是最难靠协议解决的一类**

`From: "财务部 张经理" <attacker@example.net>` 在协议层完全合规：地址真实、SPF/DKIM 都能通过（攻击者用自己的域），DMARC 也对齐。所有认证机制在这里都不会报错，因为被伪造的是显示名而非域名。

网关侧的可行规则有三条：其一，检查显示名中是否内嵌了不同于实际地址的邮箱地址（常见于把真实地址塞进显示名骗过窄屏客户端）；其二，把显示名与内部通讯录比对，若显示名匹配到内部高管或财务岗位而地址域为外部，则标记；其三，对首次出现的「外部地址 + 内部人名」组合强制加显式外部标识。

**同形字与近似域名**

近似域名（如把 rn 拼成 m、混入西里尔字母 а）需要在归一化后比对。做法是把 From 域做 IDNA 转换到 A-label，再计算与自有域及常用往来域的编辑距离，距离为 1 到 2 且此前从未通信过的，判定为高风险。

补充信号：域名注册时间很短、该域首次与本组织通信、且邮件内含付款或凭据类意图——三者叠加时应直接隔离而非仅标记。

**Received 链与认证结果头的信任边界**

`Received` 头可被发送方任意伪造，只有你自己的网关追加的那几跳才可信。判定原则是：从最上方（最后追加）开始，只信任到你控制的第一台主机为止，再往下的内容一律视为不可信输入。

RFC 8601 定义的 `Authentication-Results` 头同理——它由验证方写入，携带 authserv-id 标识来源。入站时必须剥除外部携带的、authserv-id 与本域一致的同名头，否则攻击者可以直接伪造一条 `dmarc=pass` 混过下游判定。这是该头字段最重要的部署要求，也是实际部署中最常见的疏漏。

**落地的判定顺序**

建议按此顺序：先剥除不可信的认证结果头并写入自己的结果；再按 DMARC 对齐判定域级伪造；对齐通过后，进入显示名与近似域名检测；最后叠加行为信号（首次通信、附件与链接类型）。前两步是确定性判定，后两步是概率性判定，前者可拒收，后者宜隔离或加标识。

参考：[RFC 5322 Internet Message Format](https://www.rfc-editor.org/rfc/rfc5322.html) ｜ [RFC 8601 Message Header Field for Indicating Message Authentication Status](https://www.rfc-editor.org/rfc/rfc8601.html) ｜ [RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/gw-header-forgery-detection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
