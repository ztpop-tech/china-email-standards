---
title: "DANE/TLSA 怎么给 SMTP 加密加一层「证书钉选」？为什么比纯 STARTTLS 更抗降级？"
source: "https://ztpop.net/kb/dane-tlsa-smtp-security.html"
license: CC-BY 4.0
---

# DANE/TLSA 怎么给 SMTP 加密加一层「证书钉选」？为什么比纯 STARTTLS 更抗降级？

1
DANE/TLSA 怎么给 SMTP 加密加一层「证书钉选」？为什么比纯 STARTTLS 更抗降级？
▼

**机会型 DANE TLS 的定义**

RFC 7672 标题即「SMTP Security via Opportunistic DNS-Based Authentication of Named Entities (DANE) TLSA」。核心思想是：当目标域发布了「可用的（usable）」DANE TLSA 记录、且经 DNSSEC 验证，MTA 之间就使用**抗降级的 TLS**；没有发布 TLSA 记录的域则退回普通的「机会型 TLS」甚至明文 SMTP（RFC 7672 第 1 节及第 2 节开头）。这种「有 TLSA 才强化、无则降级到普通机会型」的特性正是「机会型（opportunistic）」之义。

**TLSA 记录挂在哪里**

RFC 7672 第 2.2.3 节（TLSA Record Lookup）规定，SMTP 的 TLSA 记录位于 `_25._tcp.<mx 主机名>`。即把邮件投递端口 25、TCP 协议、以及接收方 MX 主机名拼成一条 TLSA 查询名，由 DNSSEC 保护其完整性。

**证书用法（Certificate Usages）**

RFC 7672 第 3.1 节列出 TLSA 证书用法：**DANE-TA（用法 2）**与 **DANE-EE（用法 3）**用于 SMTP 的 DANE 场景，也可使用 PKIX-TA（0）与 PKIX-EE（1）。其中 DANE-EE（3）直接把「终端实体证书」钉选，最契合邮件场景——只要服务器出示的证书与 TLSA 记录匹配即信任，无需依赖公开 CA 链。

**为什么抗降级**

因为启用机会型 DANE TLS 的前提是存在经 DNSSEC 验证的 TLSA 记录（RFC 7672 第 1 节背景与第 2 节）。主动攻击者若想发动降级（去掉 STARTTLS、伪造证书、伪装「无加密」），必须同时攻破 DNSSEC 才能伪造/篡改 TLSA 记录；否则接收方会坚持按 TLSA 钉选的证书完成 TLS 握手。RFC 7672 明确指出机会型 DANE TLS 对「发布了可用 TLSA 的目的地」抵抗降级与主动攻击。

**与 MTA-STS 的关系**

两者互补而非替代：DANE 依赖 DNSSEC 与 TLSA 钉选具体证书；MTA-STS 依赖 HTTPS 与 Web PKI，只约束「必须使用 TLS 且只认这些 MX」，并不钉选某张证书。对安全要求极高的域可同时启用两者，使加密既防降级又有证书绑定。

参考：https://www.rfc-editor.org/rfc/rfc7672.txt

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dane-tlsa-smtp-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
