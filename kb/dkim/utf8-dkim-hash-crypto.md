---
title: "DKIM Ed25519/SHA-256加密升级"
source: "https://ztpop.net/kb/utf8-dkim-hash-crypto.html"
license: CC-BY 4.0
---

# DKIM Ed25519/SHA-256加密升级

## DKIM加密算法演变脉络

DomainKeys Identified Mail（DKIM）自RFC 4871（2007年）和后续的RFC 6376（2011年）标准化以来，RSA-SHA256一直是邮件签名的首选算法。随着时间推移，RSA算法的局限性逐渐显现：2048位密钥的计算开销大、签名体积膨胀，且量子计算威胁正在逼近。RFC 8301率先禁止了SHA-1和512位以下RSA密钥的使用，而RFC 8463则正式引入了Ed25519-SHA256椭圆曲线签名算法。

RFC 8301 §1明确规定了DKIM签名的最低安全标准：签名算法必须为rsa-sha256，且RSA密钥长度不得小于1024位（推荐2048位以上）。SHA-1已被全面禁用，因为其碰撞攻击成本已降至可实际执行的水平。

## Ed25519-SHA256的技术原理

Ed25519是EdDSA签名方案在Curve25519椭圆曲线上的实现，由RFC 8032定义。与ECDSA相比，Ed25519具有以下关键优势：

* 固定签名长度：64字节（远低于RSA-2048的256字节签名）
* 恒定时间执行：无分支条件，天然抗侧信道攻击
* 确定性签名：每次签名相同消息产生相同签名值，消除随机数漏洞
* 高性能：签名验证速度约为RSA-2048的8-10倍
* 公钥极小：仅32字节嵌入DNS TXT记录中

RFC 8463 §1正式将Ed25519-SHA256定义为DKIM的有效签名算法。标签h=sha256，算法标识为ed25519-sha256。DNS记录中的公钥格式为Base64编码的32字节Ed25519公钥（不含任何ASN.1包装）。

## SHA-256在DKIM中的核心角色

SHA-256作为DKIM消息的哈希摘要算法，作用于规范化后的邮件正文（body）和头部（header）。RFC 6376 §3.7定义了正文哈希的增量计算策略：邮件正文的规范化结果被分割为4096字节的块，逐块计算SHA-256哈希。这种设计允许DKIM验证方在收到完整消息之前即可开始验证，同时限制了签名内存占用。头部哈希则基于选定的头部字段列表，按规范化顺序排列后计算SHA-256摘要。

SHA-256的重要性在于其抗第二原像攻击的能力。DKIM签名验证中，攻击者无法通过修改任意头部字段来伪造有效签名，因为任何内容修改都会改变SHA-256哈希值。RFC 8301明确要求仅支持SHA-256（h=sha256），全面淘汰了SHA-1。

## 从RSA迁移到Ed25519的部署策略

### 双密钥共存

迁移过程中，最安全的做法是同时在DNS中发布RSA和Ed25519两种公钥记录。使用不同的选择器名称区分：例如传统RSA密钥使用选择器s1，Ed25519密钥使用选择器s2。

```
# DNS: RSA公钥选择器 s1._domainkey
s1._domainkey TXT "v=DKIM1; h=sha256; k=rsa; p=MIGfMA0GCSqGSIb4..."

# DNS: Ed25519公钥选择器 s2._domainkey
s2._domainkey TXT "v=DKIM1; h=sha256; k=ed25519; p=3f3b9e2c9d4b..."
```

### MTA配置迁移

以OpenDKIM为例，配置双签名策略。

```
# /etc/opendkim.conf
# RSA签名器（保持现有）
Domain                  example.com
KeyFile                 /etc/opendkim/keys/rsa.private
Selector                s1

# Ed25519签名器
KeyFile                 /etc/opendkim/keys/ed25519.private
Selector                s2
Algorithm               ed25519-sha256

# 同时签名两个选择器
SignHeaders             yes
OversignHeaders         From,Subject,Date,Message-ID
AddAllSignatureResults  yes
```

建议的迁移时间表：先在DNS中同时发布两种记录（维持30-60天），观察接收方对Ed25519签名的验证成功率。当确认接收方支持率超过95%后，逐步减少RSA签名频率，最终保留Ed25519单签名。

## 量子安全考虑

Ed25519作为椭圆曲线签名方案，并不能抵御Shor算法对大整数分解的攻击。RFC 8463的引入更多是出于性能和安全工程而非量子安全的考虑。IETF的CFRG（Crypto Forum Research Group）正在评估后量子签名算法在DKIM中的应用可能性，目前考虑的候选方案包括CRYSTALS-Dilithium和FALCON。邮件系统管理员应关注IETF的LAMPS工作组动态，为未来的后量子DKIM迁移做好准备。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/utf8-dkim-hash-crypto.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
