---
title: "M3AAWG 公共后缀列表（PSL）的现状与未来——互联网关键基础设施的脆弱依赖"
source: "https://ztpop.net/kb/m3aawg-psl-guide.html"
license: CC-BY 4.0
---

# M3AAWG 公共后缀列表（PSL）的现状与未来——互联网关键基础设施的脆弱依赖

#### 📑 目录

1. [背景：什么是公共后缀列表](#s1)
2. [PSL 的技术作用详解](#s2)
3. [PSL 的格式与局限](#s3)
4. [矛盾的设计目标](#s4)
5. [脆弱依赖：志愿者维护的关键基础设施](#s5)
6. [M3AAWG 建议与行动路线](#s6)
7. [中国域名体系下的解读](#s7)
8. [参考与延伸阅读](#s8)

## 一、背景：什么是公共后缀列表

公共后缀列表（Public Suffix List，以下简称 PSL）是一份手工维护的域名后缀清单，列举了所有可以在其下直接注册新域名（即私有域名）的顶级域（TLD）和有效顶级域（eTLD）。截至 2023 年 4 月，PSL 共收录 9,087 条记录。

域名由点号分隔的多个标签（label）组成。最右侧的标签称为顶级域（TLD），例如 `.com`、`.net`、`.org`。而有效顶级域（eTLD）则是包含多个标签的"复合后缀"，例如 `bj.cn`（北京行政区）、`co.uk`、`k12.or.us`。这些 eTLD 的特点是：在其之下，普通用户或组织可以直接注册次级域名。

eTLD 的主要产生场景包括：

* **动态 DNS 提供商**（如 `dyndns.org`、`freeddns.org`）
* **云应用平台**（如 `blogspot.com`、`github.io`）
* **云基础设施提供商**（AWS、Azure、阿里云等）
* **消费级网络设备提供商**（如 `myfritz.net`）
* **CDN 服务商**（如 `fastly.net`、`cloudflare.net`）
* **域名转售商**（如 `br.com`、`cn.com`）
* **政府行政后缀**（如 `homeoffice.gov.uk`）

中国大陆场景：`.cn` 顶级域下各省市行政缩写如 `bj.cn`（北京）、`sh.cn`（上海）、`gz.cn`（广州）等均属 eTLD 范畴。CIDR 分配的域名系统结构天然符合 PSL 的设计需求。

## 二、PSL 的技术作用详解

### 2.1 SSL/TLS 证书签发的范围限定

PSL 帮助证书颁发机构（CA）正确界定通配符证书的范围。没有 PSL 的话，一个 CA 可能错误地签发 `*.k12.or.us` 这样的通配符证书——它适用于俄勒冈州所有学校的域名——而申请者的本意可能仅仅是 `*.springfield.k12.or.us`（仅限一所学校）。

CA/Browser Forum 的基线要求中明确引用 PSL 作为判断通配符范围的依据来源。这意味着 PSL 错误或遗漏直接影响 TLS 证书的安全性边界。

### 2.2 Web 认证 Cookie 的隔离

PSL 在浏览器中用于确定 Cookie 的作用域边界。例如，`salkeiz.k12.or.us` 的 Cookie 无法被 `springfield.k12.or.us` 读取或设置，因为 PSL 知道 `k12.or.us` 是一个 eTLD，两个域名属于不同的实体。

如果 PSL 中没有正确登记某个 eTLD，浏览器就会将其视为普通二级域名结构，导致跨实体的 Cookie 泄露——这是一个严重的安全漏洞。

### 2.3 浏览器同源策略（Same-Origin Policy）

现代浏览器（Chromium、Firefox、Safari）均内置 PSL 数据用于同源判定。两个域名是否"同源"不仅取决于协议和端口，还取决于 PSL 对有效顶级域边界的识别。在标准 Web 安全模型中，`app1.example.com` 和 `app2.example.com` 属于同一域，通过 `document.domain` 可以互相访问——但 `site1.blogspot.com` 和 `site2.blogspot.com` 不会，因为 PSL 知道 `blogspot.com` 是一个 eTLD。

表 1：PSL 在各主流浏览器和系统的集成情况

| 产品/组件 | 使用方式 | 数据来源 |
| --- | --- | --- |
| Chromium / Chrome | 内置 PSL 副本，编译时嵌入 | GitHub publicsuffix/list |
| Firefox | 内置 PSL 副本 | GitHub publicsuffix/list |
| Safari / WebKit | 内置 PSL 副本 | GitHub publicsuffix/list |
| curl / libcurl | 可选编译时引入 | GitHub publicsuffix/list |
| Python (tldextract, publicsuffix2) | 运行时下载/引用 | GitHub publicsuffix/list |
| Go (golang.org/x/net/publicsuffix) | 编译时嵌入 | GitHub publicsuffix/list |
| Rust (psl-types / publicsuffix) | 编译时嵌入 | GitHub publicsuffix/list |

中国大陆浏览器场景：国内主流浏览器如 360 浏览器、QQ 浏览器、搜狗浏览器等均基于 Chromium 内核，因此仍然依赖于同一份 PSL 数据源。这意味着 PSL 的错误或过时数据同样会影响国内用户的浏览安全。

### 2.4 邮件安全中的 PSL

在邮件安全领域，PSL 也扮演着角色。DMARC 策略中的域名对齐（Alignment）判定——发件域名是否与 DKIM d= 域或 SPF 域一致——在某些实现中参考了 PSL 来判定域名的注册边界。同时，邮件服务器在判断是否应该接受外域邮件的中转时，也可能使用 PSL 来识别组织边界。

## 三、PSL 的格式与局限

### 3.1 文件格式

PSL 是一个纯文本文件，包含 9,087 条记录（截至 2023 年 4 月）。记录类型分为四种：

* **注释行**：以 `//` 开头
* **精确匹配**：直接写 `tld` 或 `etld`
* **通配符**：`*.domain` 表示该域下的所有子域都是可注册的
* **例外**：`!domain` 用于排除某个子域，使其不被视为 eTLD

```
// === Example PSL entries ===
bj.cn
sh.cn
gz.cn

// Wildcard: all subdomains of blogspot.com are treated as separate domains
*.blogspot.com

// Exception: foo.bar is a specific registered domain, not an eTLD
!foo.bar
```

### 3.2 结构性问题

PSL 在当前纯文本格式下存在几个结构性局限：

* **无法随互联网规模扩展**：随着新 TLD（尤其是 ICANN 新通用顶级域）的大量开放，手工维护变得越来越困难
* **缺乏元数据关联**：每条记录无法携带维护者信息、更新日期、变更原因等
* **非结构化格式**：纯文本无法表达区域归属、注册规则等语义信息
* **更新延迟**：GitHub PR 到合并发布存在时间差，影响安全性

国内场景：`.cn` 域下的行政后缀变更通常通过 CNNIC 公告发布，但与 GitHub PSL 仓库之间缺乏自动同步机制。这意味着中国域名体系的 eTLD 变更可能需要更长时间才能反映在全球浏览器中。

## 四、矛盾的设计目标

PSL 的不同使用方对它有截然不同的诉求，这些诉求之间存在根本性矛盾：

表 2：PSL 各方诉求的冲突矩阵

| 诉求 | 描述 | 冲突方 |
| --- | --- | --- |
| 准确性 | 每条 eTLD 记录必须及时更新、来源可靠 | 与简洁性冲突——维护得越详细，列表越大 |
| 简洁性 | 文件体积小、加载快 | 与准确性冲突——越精准的列表越长 |
| 文件稳定性 | 条目变动少，浏览器缓存友好 | 与时效性冲突——新注册局需要及时入表 |
| 解析便捷性 | 机器可快速解析 | 纯文本格式虽然简单但缺乏结构化语义 |
| 访问模型 | 一些用户希望离线静态文件，另一些期望 DNS 查询 | 两者的存储和查找效率差异显著 |

其中最关键的结构性约束是：PSL 的主要用户是网页浏览器，浏览器需要无网络延迟的本地判定能力，因此 PSL 被设计为编译时嵌入的静态数据。这个设计决策决定了 PSL 无法轻易演进为 DNS 查询方案——虽然 DNS 方案可以解决实时性问题，但会增加每次网页加载的 DNS 查询次数，对用户体验产生负面影响。

> **IETF DBOUND 工作组**（DNS-Bound public suffixes）正在探索将 eTLD 信息嵌入 DNS 的机制。但截至目前，该方案尚未达成广泛共识，PSL 的替代方案仍处于研究阶段。

## 五、脆弱依赖：志愿者维护的关键基础设施

### 5.1 维护现状

PSL 托管在 GitHub 仓库 `publicsuffix/list`，通过 Google Cloud CDN 分发，由 Mozilla 基金会提供基础设施支持。然而，实际的维护工作仅由 1-2 名个人志愿者以"尽力而为"的方式完成，没有任何服务等级协议（SLA），也没有正式的合同保障。

这与 XKCD #2347 所描述的"开源基础设施脆弱依赖"问题如出一辙：成千上万的关键系统依赖一个由业余时间维护的项目，而维护者没有获得与其责任相匹配的资源或保障。

### 5.2 风险推演

如果 PSL 停止维护，可能引发以下连锁反应：

* **短期（数天）**：新注册的 eTLD 无法被浏览器识别，出现 Cookie 跨域泄露和安全漏洞
* **中期（数周）**：新 TLD 的 TLS 证书范围界定混乱，CA 可能签发过宽的通配符证书
* **长期（数月）**：各浏览器厂商各自维护自己的 PSL 分支，数据碎片化导致安全策略不一致
* **极端情况**：全网范围内，基于域名的安全策略（Cookie 同源、TLS 证书范围、邮件认证对齐）出现系统性裂缝

### 5.3 行业响应

M3AAWG 报告指出，需要可持续的资金支持和基金会级别的治理结构来保障 PSL 的长期可用性。部分互联网企业已经表达了支持意愿，但尚未形成稳定的资金机制。

> PSL 的问题并非孤例。它代表了互联网基础设施中一类典型的脆弱依赖模式：一个广泛使用但缺乏治理保障的开源项目，支撑着数十亿用户的日常安全。类似的问题也存在于根区（Root Zone）维护、RDAP（注册数据访问协议）等基础设施中。

国内观察：中国域名注册体系由 CNNIC 统一管理，`.cn`、`.中国`、`.公司`、`.网络` 等国别域名（ccTLD）在国内有完善的注册管理机制。但 PSL 作为一个全球性的开源项目，中国域名体系的 eTLD 变更同样需要通过 GitHub PR 提交，这对国内注册管理机构而言，参与国际开源协作的门槛较高。

## 六、M3AAWG 建议与行动路线

M3AAWG 在报告中对不同角色提出了相应建议：

### 6.1 如果你是 PSL 的使用方

确保你的应用程序使用最新版本的 PSL 数据。建议建立自动化机制，定期从 PSL 官方仓库拉取更新。如果你的产品将 PSL 编译到二进制中（如 Go 语言的 `golang.org/x/net/publicsuffix`），请关注该依赖的版本更新。

### 6.2 如果你是 TLD 或 eTLD 的管理者

检视你的域名结构是否已经正确登记在 PSL 中。如果缺失，请通过 GitHub `publicsuffix/list` 提交 Pull Request。更新内容包括：

* 确认你的域名是否属于 eTLD 范畴
* 根据 RFC 的规范要求，提供正确的通配符或精确匹配条目
* 在 PR 中附上说明，解释为何该域名应被纳入 PSL

### 6.3 如果你是协议或平台开发者

积极参与 IETF DBOUND 工作组的工作，推动基于 DNS 的 eTLD 发现机制标准化。长远来看，DNS 原生方案比手工维护的 PSL 更具可持续性。

### 6.4 支持 PSL 的维护

考虑以下方式为 PSL 的可持续发展做出贡献：

* **作为志愿者**：协助审核 Pull Request、响应 issue、参与维护
* **作为赞助商**：提供资金支持，帮助建立全职维护团队和正式治理结构
* **作为基础设施支持方**：提供 CDN、CI/CD、测试环境等资源

国内行动建议：CNNIC 及各行政 eTLD 管理机构应主动与 PSL 维护团队建立沟通渠道，确保 `.cn` 体系下的 eTLD 变更能及时反映到 PSL 中。同时，建议国内浏览器厂商建立 PSL 更新预警机制，在官方更新延迟时能够自我校正。

## 七、中国域名体系下的解读

### 7.1 .CN 域名体系中的 eTLD

中国的 `.cn` 域名体系有着精细的行政层级结构。以下是在 PSL 中有登记的 `.cn` 系 eTLD 示例：

表 3：.CN 行政 eTLD 示例

| eTLD | 所属行政区 | 说明 |
| --- | --- | --- |
| `bj.cn` | 北京市 | 北京行政区 ccTLD |
| `sh.cn` | 上海市 | 上海行政区 ccTLD |
| `gz.cn` | 广州市 / 贵州省 | 省级行政二级域 |
| `com.cn` | 全国 | 商业机构二级域 |
| `net.cn` | 全国 | 网络服务二级域 |
| `org.cn` | 全国 | 非盈利组织二级域 |
| `gov.cn` | 全国 | 政府机关二级域 |
| `edu.cn` | 全国 | 教育机构二级域 |
| `ac.cn` | 全国 | 科研机构二级域 |

### 7.2 中国互联网企业在 PSL 中的参与

在国内互联网生态中，以下场景也与 PSL 密切相关：

* **云平台服务**：阿里云的 `alicdn.com`、腾讯云的 `tencent-cloud.com` 等平台级域名如果在 PSL 中缺失，可能导致同平台不同租户之间的安全边界模糊
* **博客与托管平台**：类似 `github.io` 的模式，国内部分服务商也提供子域名分配服务，需要纳入 PSL 以防止 Cookie 泄露
* **CDN 服务**：国内 CDN 厂商的边缘节点域名结构如果涉及多租户的子域名分配，应考虑 PSL 登记

### 7.3 对国内互联网治理的启示

PSL 的风险案例对国内互联网基础设施治理提供了重要启示：

* **关键基础设施的归一化管理**：`.cn` 域名体系虽然由 CNNIC 统一管理，但与全球 PSL 的同步机制尚不完善
* **开源治理经验**：志愿者维护模式在发展到一定规模后需要治理升级，这一规律对国内开源社区同样适用
* **安全供应链管理**：PSL 等基础数据的可靠性与完整性应当纳入企业的安全供应商管理体系

## 八、参考与延伸阅读

### 📚 相关阅读

* [M3AAWG 停放域名最佳实践——减少域名滥用的操作指南](https://www.ztpop.net/kb/m3aawg-parked-domains-bcp.html)
* [邮件认证生态全景：SPF/DKIM/DMARC 的协同与局限](https://www.ztpop.net/kb/email-authentication-ecosystem.html)
* [TLS 邮件加密实践：从 STARTTLS 到 MTA-STS](https://www.ztpop.net/kb/tls-email-encryption.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-psl-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
