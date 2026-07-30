---
title: "BIMI Guidelines v1.1 更新要点：SVG 格式要求、VMC 策略变化与 BMP 标签"
source: "https://ztpop.net/kb/bimi-vmc-guidelines-v1.1.html"
license: CC-BY 4.0
---

# BIMI Guidelines v1.1 更新要点：SVG 格式要求、VMC 策略变化与 BMP 标签

翻译自 BIMI Group Guidelines v1.1 规范文档

BIMI Group 在 v1.1 版本中对多项规范进行了重大更新，涵盖了 SVG 格式要求、VMC 策略变化、CMC 引入以及 LPS 标签更新。

## SVG Logo 新格式要求

### viewBox 属性要求

v1.1 明确规定 SVG 文件必须包含正确的 viewBox 属性，确保不同邮件客户端中的等比缩放。推荐 viewBox 值为 "0 0 200 200" 或 "0 0 100 100"，宽高比必须为 1:1 的正方形。

### 颜色空间要求

SVG 文件中使用的颜色必须位于 sRGB 颜色空间内。BIMI Group 提供了推荐的品牌颜色十六进制值列表。颜色使用 CMYK 或 PANTONE 色彩体系的 SVG 将被邮箱系统拒绝。

### 字体嵌入限制

SVG 文件中嵌入的字体必须仅限于品牌标志所需的文字标记。SVG 中应首选 path（路径）代替文字渲染。如果必须使用文字，需要使用标准 Web 安全字体（如 Arial、Helvetica），并明确指定 font-family。

### 文件大小上限

SVG 标志文件的原始大小（不含压缩）不得超过 32KB。超过此限制的标志会被邮箱服务商拒绝展示，且可能影响 DMARC 认证通过率。

## VMC 策略变化

### DMARC 要求放宽

VMC 对 DMARC 策略的要求进行了调整：p=quarantine 和 p=reject 仍然是最严格的推荐策略，但 p=none 搭配 pct=100 且认证通过率 >95% 的域也可以申请 VMC（2026 年试点政策）。

### 证书有效期调整

VMC 证书的有效期从此前的最长 3 年调整为最长 825 天（约 2.25 年），与 TLS 证书的行业标准（Apple/Safari 的 CT 策略）对齐。

### 多域名支持

一张 VMC 证书最多支持 5 个发送域，前提是所有域属于同一组织实体。多域 VMC 在验证时需要为每个域分别完成域名验证和 DMARC 配置检查。

## CMC（Common Mark Certificate）引入

v1.1 正式引入了 CMC 概念。CMC 为中小型企业提供了一条低成本的 BIMI 部署路径。CMC 的验证要求比 VMC 宽松，不要求 WebTrust 审计，但接受 CMC 的邮箱服务商数量也相对有限。

## BIMI LPS（Logo Permanent Storage）标签更新

### LPS 标签格式

BIMI DNS TXT 记录新增了 LPS 标签，格式如下：

```
default._bimi.domain.example IN TXT "v=BIMI1; l=https://storage.bimigroup.org/logo.svg; a=https://storage.example.com/vmc.pem; lps=sha256-XXXXX"
```

### LPS 的作用

LPS 提供了一个标志的永久存储哈希引用，使接收方邮箱系统可以验证标志文件是否被篡改。LPS 使用 SHA-256 对 SVG 文件内容进行哈希计算，将哈希值嵌入 BIMI DNS 记录中。邮箱服务商下载 SVG 文件后重新计算哈希值，与 LPS 字段对比。

### SVG 放置建议

建议同时将 SVG 文件托管在自己的域名下和 BIMI 基础设施中。自我托管时需确保 SVG 文件可通过 HTTPS 访问，Content-Type 为 image/svg+xml，并配置正确的 CORS 头。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-vmc-guidelines-v1.1.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
