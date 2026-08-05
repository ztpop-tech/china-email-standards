---
title: "BIMI 品牌邮件标识深度解析 — DMARC 前置条件、BIMI TXT/PSD 记录与 VMC 证书全链路"
source: "https://ztpop.net/kb/bimi-guide.html"
license: CC-BY 4.0
---

# BIMI 品牌邮件标识深度解析 — DMARC 前置条件、BIMI TXT/PSD 记录与 VMC 证书全链路

BIMI（Brand Indicators for Message Identification）是 IETF 草案 draft-brand-indicators-for-message-identification 定义的协议规范，目标是让邮件发送方在经过认证后，其品牌 Logo 能够显示在收件人的邮件客户端界面中。BIMI 不是一套孤立的协议——它建立在一整套邮件身份认证基础设施之上：发送域必须先通过 DMARC 的严格策略（
`p=quarantine`
或
`p=reject`
），再通过 DNS 发布 BIMI TXT 记录和可选的 VMC（Verified Mark Certificate）证书，MUA（Mail User Agent）在验证全部通过后，最终在收件箱中展示品牌标识。本文从 DMARC 前置条件出发，逐层拆解 BIMI TXT 记录格式、SVG Logo Profile（PSD）规范、VMC 证书获取流程以及 Evidence Document 自断言机制，并给出主流邮箱客户端的支持矩阵与排错清单。

## 一、BIMI 三步流程概览

BIMI 的完整工作流可以拆分为三个阶段，从发送域配置到最终用户可见的 Logo 渲染：

### 第一步 — DMARC 达标验证

发送域必须配置 DMARC 记录（RFC 7489），且策略
`p`
值为
`quarantine`
或
`reject`
，同时至少一项认证机制（SPF 或 DKIM）与 From 域对齐（alignment）。MUA 在发起 BIMI 查询之前，优先检查 DMARC 的通过状态——如果
`p=none`
，MUA 直接跳过后续步骤，不会尝试获取或显示 Logo。

### 第二步 — DNS BIMI 记录查询

收件方 MUA 向发送域的
`default._bimi`
子域发起 DNS TXT 查询，解析三条核心标签：
`v=BIMI1`
（协议版本）、
`l=`
（Logo HTTPS URL）、
`a=`
（可选的 BIMI Evidence 自断言 URL）。所有 URL 必须使用 HTTPS 协议。

### 第三步 — Logo 获取与渲染

MUA 从
`l=`
标签指定的 HTTPS URL 下载 SVG 文件，按 PSD（SVG Tiny Portable/Secure Profile）规范验证格式合规性。若
`a=`
标签存在，则额外交叉验证 VMC 证书链或 Evidence Document（取决于 MUA 实现）。全部验证通过后，Logo 渲染于收件人 UI 的发送者头像位置。

## 二、DMARC 前置条件：为什么 p=none 不触发 BIMI

BIMI 工作组草案（Brand Indicators for Message Identification）明确规定：DMARC 策略必须至少为
`p=quarantine`
。背后的逻辑并不难理解——BIMI 的核心价值是「品牌担保」：MUA 在邮件旁展示一个 Logo，本质上是在向用户断言「这封邮件确实来自该品牌」。如果发送域只处于
`p=none`
的纯监控模式，说明域所有者尚未建立起对自身邮件流的充分控制，此时展示品牌 Logo 反而可能被欺骗者利用，放大钓鱼邮件的危害面。BIMI 草案在设计上就内置了对 DMARC（RFC 7489）的强依赖，确保只有认证基础设施成熟的域才有资格触发 BIMI 显示。

**DMARC 前置条件清单：**

二、DMARC 前置条件：为什么 p=none 不触发 BIMI

| 条件 | 要求 | 验证方法 |
| DMARC p 值 | `quarantine` 或 `reject` | `dig TXT _dmarc.domain.com +short` |
| SPF 或 DKIM 对齐 | 至少一项与 Header From 域严格/宽松对齐 | 发送测试邮件到 Gmail，查看 Authentication-Results 头 |
| pct 值 | 若设置，建议 `pct=100` ；低于 100 时部分 MUA 可能不触发 BIMI | 同上 DMARC 记录 |
| 子域策略 sp | 如有子域发信需求，sp 值同样须满足 ≥quarantine | `dig TXT _dmarc.sub.domain.com +short` |
| 策略稳定期 | Gmail 等 MUA 要求 DMARC 策略稳定执行 ≥ 24-48h | 通过 Postmaster Tools 或 DMARC 聚合报告确认 |

**验证命令：**

```
# 检查 DMARC 记录
$ dig TXT _dmarc.example.com +short
"v=DMARC1; p=reject; rua=mailto:dmarc-reports@example.com; pct=100; sp=reject"

# 如果返回 "p=none" 或查询无结果，BIMI 不会生效
$ dig TXT _dmarc.not-ready.com +short
"v=DMARC1; p=none; rua=mailto:dmarc@not-ready.com"
# ↑ 这种情况下，即使发布了 BIMI 记录，MUA 也不会显示 Logo
```

**⚠️ 注意：**

部分 MUA（尤其是 Gmail）不仅校验 DMARC 策略值本身，还会交叉参考域名的发信信誉（sending reputation）和 DMARC 聚合报告的持续达标率。仅把 p 值改成 quarantine 但 SPF/DKIM 对齐率不稳定，同样可能导致 BIMI Logo 不显示。

## 三、BIMI TXT 记录格式

BIMI 记录存放在发送域的一个专用 DNS TXT 记录中，查询路径固定为：

```
default._bimi.example.com.  IN  TXT  "v=BIMI1; l=https://cdn.example.com/brand/logo.svg; a=https://example.com/bimi-evidence.pem"
```

三、BIMI TXT 记录格式

| 标签 | 必选 | 格式 | 说明 |
| `v=BIMI1` | 是 | 固定值 | 协议版本，当前仅支持 BIMI1（BIMI Working Group 草案定义） |
| `l=` | 是 | HTTPS URL | Logo 文件的完整 URL，必须使用 `https://` 协议，不支持 HTTP |
| `a=` | 否 | HTTPS URL 或 data URI | BIMI Evidence Document 或自签名证书（PEM）URL，用于 MUA 额外验证 |

**关键约束：**

* 所有 URL
  **必须使用 HTTPS**
  ——MUA 对 HTTP 协议的
  `l=`
  标签直接拒绝，不尝试降级或提示。
* Logo URL 的域名
  **可以与发送域不同**
  （允许 CDN 托管），但该域名的 TLS 证书必须有效且主机名匹配。
* DNS TXT 记录的总长度受 RFC 1035 限制（单条 ≤ 255 字节），建议将长 URL 分段或使用短域名。
* `a=`
  标签指向的文件可以是 PEM 格式的 X.509 自签名证书，也可以是 JSON 格式的 BIMI Evidence Document（详见第六节）。

**查询命令：**

```
# 查询 BIMI TXT 记录
$ dig TXT default._bimi.example.com +short
"v=BIMI1; l=https://cdn.example.com/brand/logo.svg"

# 包含 a= 标签的完整记录
$ dig TXT default._bimi.brand.com +short
"v=BIMI1; l=https://brand.com/logo.svg; a=https://brand.com/evidence.pem"

# 如果查询返回空，说明 BIMI 记录未配置或 DNS 尚未同步
$ dig TXT default._bimi.nonexample.com +short
# 无输出
```

## 四、SVG Logo Profile（PSD）规范

BIMI 对 Logo 文件的格式要求极为苛刻——这不是一个「差不多就行」的规范。BIMI SVG Logo Profile（PSD / Portable Secure Document）基于 SVG Tiny 1.2 的一个严格子集，禁止了标准 SVG 中的大部分「花活」。以下是 BIMI Working Group 草案规定的硬性约束：

四、SVG Logo Profile（PSD）规范

| 规范项 | 要求 |
| 文件格式 | SVG Tiny 1.2（非完整 SVG 1.1），必须声明 `xmlns="http://www.w3.org/2000/svg"` |
| 宽高比 | 严格 1:1（正方形），不支持非正方形 Logo 居中裁切 |
| 渲染尺寸 | 缩放后以 24×24 dp（device-independent pixels）渲染 |
| 颜色模式 | 仅支持纯色填充（solid color）， **禁止** 渐变（ / ） |
| 透明度 | **禁止** `opacity` 属性、 `rgba()` 颜色、 `fill-opacity` |
| 背景形状 | 可选 Rounded Rectangle（ ）或 Circle 裁剪作为底色 |
| 脚本 | **禁止** 任何 `参考：datatracker.ietf.org` |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
