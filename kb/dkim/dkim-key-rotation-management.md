---
title: "DKIM 密钥轮转与安全管理指南"
source: "https://ztpop.net/kb/dkim-key-rotation-management.html"
license: CC-BY 4.0
---

# DKIM 密钥轮转与安全管理指南

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤DKIM 签名密钥的定期轮转让已泄漏或濒临过期的密钥失效。RFC 6376 要求签名方提供密钥管理机制。

## 1. 密钥生成

```
opendkim-genkey -D /etc/opendkim/keys/ -d example.com -s s202607
opendkim-genkey -D /etc/opendkim/keys/ -d example.com -s s202607 -b 256 -a ed25519
chown opendkim:opendkim /etc/opendkim/keys/*.private
chmod 640 /etc/opendkim/keys/*.private
```

## 2. 多选择器管理

命名规范 sYYYYMM（年月），轮转时两个选择器同时在线。

```
s202607._domainkey.example.com.  IN  TXT  "v=DKIM1; k=rsa; p=..."
# 轮转：生成 s202608，发布 DNS，切签名，7天后删 s202607
```

## 3. 密钥泄露响应

1. 从 DNS 删除泄露选择器的公钥记录。
2. 生成新密钥对并发布。
3. 配合 DNSSEC（RFC 6781）确保 DNS 完整性。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-key-rotation-management.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
