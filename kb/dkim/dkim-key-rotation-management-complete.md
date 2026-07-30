---
title: "DKIM 密钥轮转完整指南：选择器策略、自动化方案与最佳实践"
source: "https://ztpop.net/kb/dkim-key-rotation-management-complete.html"
license: CC-BY 4.0
---

# DKIM 密钥轮转完整指南：选择器策略、自动化方案与最佳实践

参考 RFC 8301、M3AAWG DKIM 操作指南

DKIM 密钥是邮件认证体系中最容易被忽视的安全组件之一。长期不更换的 DKIM 密钥是企业的重大安全隐患——一旦私钥泄露，攻击者可以使用该密钥为任何伪装域发出的邮件签名，从而使所有收件方信任该邮件。

## DKIM 密钥轮转的必要性

RFC 8301 推荐 DKIM 密钥长度至少 1024-bit，建议使用 2048-bit。然而，长密钥的破解计算复杂度随着攻击者算力的增长而降低。2026 年的量子计算发展已使得 1024-bit 的破解时间大幅缩短。M3AAWG 建议所有发件方将 DKIM 密钥轮转周期缩短至 90 天。

## DKIM 密钥轮转标准流程

### 多密钥并行策略

DKIM 选择器（Selector）机制支持多密钥并行使用。轮转策略如下：

1. **生成新密钥对**：使用 2048-bit RSA 或 Ed25519 算法生成
2. **发布新公钥**：在新选择器名的 DNS 中添加公钥记录（例如从 s1 切换到 s2）
3. **开始使用新私钥签名**：MTA 配置开始对新邮件使用新私钥签名
4. **等待 DNS TTL 过期**：等旧公钥的 DNS TTL 在整个 DNS 层级中过期（通常 24-72 小时）
5. **移除旧公钥**：删除旧选择器的 DNS 记录
6. **彻底销毁旧私钥**：使用安全擦除工具从服务器彻底删除

### 过渡期避免的问题

* 不要同时删除旧私钥和旧公钥——先停止签名（换新签名域），等旧签名在传输中的邮件全部被处理后（3-5 天），再移除 DNS 记录
* 使用 DNS 监控工具验证新公钥的 DNS TXT 记录在全球各级递归服务器中已正确传播
* Ed25519（RFC 8463）密钥签名验证性能好但部分邮箱服务商不支持，需提前验证收件方的兼容性

## 自动化轮转方案

推荐使用 DNS API 实现自动化零停机轮转。例如使用 OpenDKIM 的密钥轮转工具：

```
# 生成新密钥
opendkim-genkey -D /etc/opendkim/keys/ -d example.com -s s2 -b 2048
# DNS 更新：通过 API 发布公钥
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://api.dnsprovider.com/v1/zones/example.com/txt \
  -d '{"name":"s2._domainkey.example.com","value":"v=DKIM1; h=sha256; k=rsa; p=MIGfMA0..."}'
# MTA 配置切换
sed -i 's/KeyFile.*s1\.private/KeyFile \/etc\/opendkim\/keys\/s2.private/' /etc/opendkim.conf
```

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dkim-key-rotation-management-complete.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
