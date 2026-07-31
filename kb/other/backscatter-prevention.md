---
title: "什么是退信散射（Backscatter）？如何防止我的服务器成为散射源？"
source: "https://ztpop.net/kb/backscatter-prevention.html"
license: CC-BY 4.0
---

# 什么是退信散射（Backscatter）？如何防止我的服务器成为散射源？

1
什么是退信散射（Backscatter）？如何防止我的服务器成为散射源？
▼

**定义**

Backscatter 指：攻击者伪造你的域名发 spam，接收方把退信（NDR）发到被伪造的“发件人”地址（其实不是你发的），于是你无辜收到/转发大量退信，且可能被反向列入黑名单。

**成因**

向“信封发件人（MAIL FROM）不存在或伪造”的邮件生成退信，而退信本身无可信认证，收件方无法判断你是否真发过。

**防护**

① 对入站先验证 SPF/DKIM，对伪造明显的直接拒收不收信，自然不产生退信；② 仅对“本地确实接受过的收件人”产生的真正投递失败才发 NDR；③ 出站对发往外域的退信做限制；④ 部署 BATV/签名信头识别本域发出的信。

**价值**

防止你的 IP/域名因“散射退信”被误封，保护发送信誉；是反垃圾与信誉管理的重要一环。

参考：RFC 5321 §6.2（对未知收件人的处理避免散射）；M3AAWG 反散射建议

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/backscatter-prevention.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
