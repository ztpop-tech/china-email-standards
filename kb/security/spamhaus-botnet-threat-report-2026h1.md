---
title: "Spamhaus 僵尸网络威胁报告 2026 上半年：C&C 总量 -30%，Sliver 登顶，.cn 域名滥用 +771%"
source: "https://ztpop.net/kb/spamhaus-botnet-threat-report-2026h1.html"
license: CC-BY 4.0
---

# Spamhaus 僵尸网络威胁报告 2026 上半年：C&C 总量 -30%，Sliver 登顶，.cn 域名滥用 +771%

> 本文为 Spamhaus 官方报告《Botnet Threat Update January to June 2026》（2026-07-10 发布，The Spamhaus Team）的翻译与结构化解读。所有数据均直接引自该报告原文及报告 PDF（https://content.spamhaus.org/d32359a1-1665-4dd8-8cf4-a75d2f66fc1d.pdf）。本文仅对 Spamhaus 人类作者文本做翻译与策展，不含 AI 原创观点。

## 一、报告概述

Spamhaus 于 2026 年 7 月 10 日发布 2026 上半年（1 月-6 月）僵尸网络威胁更新报告，核心发现：

- **僵尸网络 C&C 服务器数量下降 30%**，从 2025 下半年的 21,425 台降至 **14,952 台**（月均 2,492 台），回到 2024 年上半年（14,248 台）水平，为 2023 年以来最大跌幅
- **Sliver 超过 Cobalt Strike 成为最常用的 C&C 框架**（+58%），Cobalt Strike 跌至第 4 位（-68%）
- **.cn 顶级域下的 botnet C&C 域名激增 +771%**（106 → 923 个）
- **印度注册商 PDR 被滥用注册量 +901%**（320 → 3,204 个），俄罗斯注册商 REGRU 逆势下降 90%
- 新增观察：Stark Industries Solutions（被评估为新型 bulletproof hosting 提供商，与俄罗斯关联 APT 组织相关）

## 二、C&C 服务器总量变化（历史趋势）

| 周期 | C&C 数量 | 月均 | 变化率 |
|------|---------|------|--------|
| 2023 下半年 | 15,226 | 2,538 | -9% |
| 2024 上半年 | 14,248 | 2,375 | -6% |
| 2024 下半年 | 13,720 | 2,287 | -4% |
| 2025 上半年 | 17,258 | 2,876 | **+26%** |
| 2025 下半年 | 21,425 | 3,571 | **+24%** |
| **2026 上半年** | **14,952** | **2,492** | **-30%** |

2025 年连续两个半年的 C&C 激增（+26%、+24%）在 2026 上半年被显著逆转，总量回落至 2024 年水平。报告将这一下降归因于网络运营商与执法部门对僵尸网络基础设施、恶意软件及 bulletproof hosting 提供商的持续打击。

## 三、Top 20 恶意软件家族变化

### 排名变化（核心数据）

| 排名 | 家族 | 2025 下半年 | 2026 上半年 | 变化率 | 类型 |
|------|------|------------|------------|--------|------|
| **#1** | **Sliver** | 1,904 | **3,008** | **+58%** | Pentest Framework |
| #2 | AsyncRAT | 2,467 | 1,951 | -21% | RAT |
| #3 | Remcos | 2,269 | 1,717 | -24% | RAT |
| #4 | Cobalt Strike | 3,451 | 1,110 | **-68%** | Pentest Framework |
| #5 | Aisuru | 1,023 | 594 | -42% | DDoS Bot |
| #6 | DCRat | 505 | 447 | -11% | RAT |
| #7 | QuasarRAT | 774 | 378 | -51% | RAT |
| #8 | Havoc | 515 | 357 | -31% | Pentest Framework |
| #9 | ValleyRAT | 430 | 356 | -17% | RAT |
| #10 | XWorm | 860 | 289 | -66% | RAT |
| #11 | PureRAT | — | 271 | **新进入** | RAT |
| #12 | Mirai | 380 | 254 | -33% | DDoS Bot |
| #13 | Vidar | 151 | 247 | +64% | Credential Stealer |
| #14 | Coper | 271 | 190 | -30% | Android Backdoor |
| #15 | Tofsee | — | 183 | **新进入** | Spambot |
| #16 | Joker | 279 | 145 | -48% | Credential Stealer |
| #17 | Venom | 185 | 113 | -39% | Remote Access Stealer |
| #18 | DeimosC2 | — | 102 | **新进入** | Pentest Framework |
| #19 | Socks5Systemz | — | 90 | **新进入** | Backdoor |
| #20 | NetSupportManagerRAT | — | 65 | **新进入** | RAT |

### 关键观察

- **Sliver 登顶**（+58% 至 3,008 个）：Sliver 是 BishopFox 开源的攻击性安全测试框架，其被滥用规模超过传统王者 Cobalt Strike，反映攻击者向开源、难以检测的 C2 框架迁移
- **Cobalt Strike 暴跌 68%**（3,451 → 1,110）：执法打击（Operation Endgame 系列）与检测能力提升的叠加效果
- **新进入 Top 20 的 5 个家族**：PureRAT、Tofsee（Spambot，与垃圾邮件直接相关）、DeimosC2、Socks5Systemz、NetSupportManagerRAT
- **退出 Top 20**：BianLian、Flubot、Latrodectus、PureLogs Stealer、Rhadamanthys
- **类型占比**：RAT（远程访问木马）46.13% + Pentest Framework（渗透测试框架）38.57%，合计 **>84%**——攻击者对「持久访问」的偏好压倒一切

## 四、域名与注册商滥用数据

### Top 20 最滥用 TLD

| 排名 | TLD | 2025 下半年 | 2026 上半年 | 变化率 | 类型 |
|------|-----|------------|------------|--------|------|
| #1 | .com | 4,287 | **9,285** | **+117%** | gTLD |
| #2 | .top | 627 | 1,126 | +80% | gTLD |
| **#3** | **.cn** | 106 | **923** | **+771%** | ccTLD |
| #4 | .net | 539 | 826 | +53% | gTLD |
| #5 | .ru | 3,726 | 630 | **-83%** | ccTLD |
| #6 | .xyz | 393 | 622 | +58% | gTLD |
| #7 | .io | — | 565 | 新进入 | ccTLD |
| #8 | .org | 341 | 555 | +63% | gTLD |
| #9 | .digital | — | 498 | 新进入 | gTLD |
| #10 | .cc | 256 | 492 | +92% | ccTLD |
| #11 | .info | 339 | 467 | +38% | gTLD |
| #12 | .lat | — | 460 | 新进入 | gTLD |
| #13 | .cyou | 111 | 388 | +250% | gTLD |
| #14 | .garden | — | 372 | 新进入 | gTLD |
| #15 | .lol | — | 369 | 新进入 | gTLD |
| #16 | .online | 238 | 259 | +9% | gTLD |
| #17 | .site | 133 | 236 | +77% | gTLD |
| #18 | .tv | — | 227 | 新进入 | ccTLD |
| #19 | .icu | 88 | 224 | +155% | gTLD |
| #20 | .fun | 100 | 218 | +118% | gTLD |

要点：

- **.com 仍是滥用绝对主力**（9,285 个，+117%），但仅占 .com 1.58 亿活跃域名的 0.006%
- **.cn 激增 +771%**（106 → 923 个）——报告期内中国 ccTLD 下 botnet C&C 域名异常增长
- **.ru 大幅下降 -83%**（3,726 → 630 个）——与 REGRU 注册商滥用 -90% 呼应，俄罗斯方向整体收缩
- 新进入 Top 20：.io、.digital、.lat、.garden、.lol、.tv

### Top 20 最滥用注册商

| 排名 | 注册商 | 2025 上半年 | 2026 上半年 | 变化率 | 国家 |
|------|--------|------------|------------|--------|------|
| #1 | Namecheap | 1,914 | **4,331** | **+126%** | 美国 |
| **#2** | **PDR** | 320 | **3,204** | **+901%** | **印度** |
| #3 | Dynadot Inc | 1,680 | 2,409 | +43% | 美国 |
| #4 | Nicenic International Group | 738 | 1,514 | +105% | 中国 |
| #5 | GoDaddy.com | 516 | 1,144 | +122% | 美国 |
| #6 | Sav.com | 111 | 1,055 | **+850%** | 美国 |
| #7 | NameSilo | 555 | 1,034 | +86% | 加拿大 |
| #8 | Spaceship, Inc. | 347 | 862 | +148% | 美国 |
| #9 | Hostinger | 257 | 715 | +178% | 立陶宛 |
| #10 | Gname | 384 | 600 | +56% | 新加坡 |
| #11 | Wanshangyunji (Chengdu) Technology | — | 559 | 新进入 | 中国 |
| **#12** | **REGRU** | 3,883 | **369** | **-90%** | **俄罗斯** |
| #13 | Global Domain Group LLC | — | 296 | 新进入 | 美国 |
| #14 | Tucows | 238 | 239 | 0% | 加拿大 |
| #15 | WebNic.cc | 223 | 235 | +5% | 新加坡 |
| #16 | Cloudflare, Inc. | 136 | 231 | +70% | 新加坡 |
| #17 | Porkbun | 115 | 220 | +91% | 美国 |
| #18 | Realtime Register B.V. | — | 211 | 新进入 | 荷兰 |
| #19 | Hosting Concepts B.V. | — | 200 | 新进入 | 荷兰 |
| #20 | Name SRS | 116 | 198 | +71% | 瑞典 |

要点：

- **PDR（印度）+901%**：滥用注册量从 320 飙升至 3,204，报告建议与 Spamhaus 联系关注
- **REGRU（俄罗斯）-90%**：与 .ru 域名下降同步，俄罗斯注册渠道整体收缩
- **美国注册商占比升至 52.57%**（2025 下半年 39.91%），俄罗斯从 32.15% 降至 1.88%
- 印度占比从 2.65% 升至 16.33%，成为仅次于美国的第二大滥用注册来源国
- 中国注册商 Nicenic（+105%）与新进入的 Wanshangyunji 均在列

## 五、托管网络（Botnet C&C 宿主）

### 新观察到 C&C 最多的网络

| 排名 | 网络 | 2025 下半年 | 2026 上半年 | 变化率 | 国家 |
|------|------|------------|------------|--------|------|
| #1 | DigitalOcean | 1,428 | 1,017 | -29% | 美国 |
| #2 | Stark Industries Solutions | — | 931 | 新进入 | 英国 |
| #3 | Colocrossing | 729 | 589 | -19% | 美国 |
| #4 | Alibaba-inc | 1,502 | 588 | **-61%** | 中国 |
| #5 | Virtualine | 511 | 382 | -25% | 英国 |
| #6 | Contabo | 346 | 374 | +8% | 德国 |
| #7 | Amazon | 543 | 335 | -38% | 美国 |
| #8 | Tencent | 879 | 302 | **-66%** | 中国 |
| #9 | Cloudzy | — | 291 | 新进入 | 美国 |
| #10 | AS210558 | 362 | 273 | -25% | 德国 |

要点：

- **Stark Industries Solutions 以 931 个 C&C 直接进入第 2 位**：报告评估其为新型 bulletproof hosting 提供商，与俄罗斯关联 APT 组织相关
- **中国云厂商显著改善**：Alibaba-inc -61%、Tencent -66%（活跃 C&C 分别 -53%、-64%）
- **Cloudzy** 被评估为「knowingly or recklessly hosts malicious infrastructure」（知情或鲁莽地托管恶意基础设施）

## 六、地理分布（Top 20 国家）

| 排名 | 国家 | 2025 下半年 | 2026 上半年 | 变化率 |
|------|------|------------|------------|--------|
| #1 | 美国 | 5,040 | 4,244 | -16% |
| #2 | 荷兰 | 2,104 | 1,595 | -24% |
| #3 | 中国 | 3,371 | 1,409 | **-58%** |
| #4 | 德国 | 1,528 | 1,170 | -23% |
| #5 | 新加坡 | 1,191 | 645 | -46% |
| #6 | 英国 | 667 | 539 | -19% |
| #7 | 法国 | 533 | 525 | -2% |
| #8 | 俄罗斯 | 722 | 471 | -35% |
| #9 | 塞浦路斯 | — | 286 | 新进入 |
| #10 | 瑞典 | 437 | 264 | -40% |
| #11 | 芬兰 | 197 | 254 | **+29%（唯一大幅增长）** |
| #12 | 摩尔多瓦 | — | 231 | 新进入 |
| #13 | 加拿大 | 206 | 219 | +6% |
| #14 | 塞舌尔 | 647 | 209 | **-68%** |
| #15 | 拉脱维亚 | — | 188 | 新进入 |
| #16 | 土耳其 | 271 | 187 | -31% |
| #17 | 日本 | 269 | 175 | -35% |
| #18 | 越南 | 321 | 174 | -46% |
| #18 | 瑞士 | — | 174 | 新进入 |
| #20 | 阿联酋 | — | 143 | 新进入 |

要点：

- 美国连续 6 期保持第 1，但数量下降 16%
- 中国从第 2 降至第 3（-58%），与阿里云/腾讯云改善数据一致
- 芬兰 +29% 是前 20 中唯一大幅增长的国家
- 塞舌尔 -68%（历史上依赖宽松注册政策的离岸枢纽收缩）

## 七、对邮件安全运营的启示（数据应用层）

以下为基于报告数据的运维应用梳理（数据本身均引自报告原文）：

1. **C&C 基础设施与垃圾邮件/钓鱼的关联**：Tofsee（Spambot）新进入 Top 20（183 个 C&C）——垃圾邮件僵尸网络仍在活跃运营；邮件网关应将 C&C 域名/IP 信誉源（如 Spamhaus ZEN、DBL）作为过滤信号之一
2. **.cn 域名 +771% 的监控价值**：对入境邮件中 .cn 新注册域名的 SPF/DKIM 认证失败率与发信行为应重点监控（域名滥用高发区的投递特征）
3. **注册商维度**：PDR（印度）+901%、Sav.com +850% 等注册商是新注册域名信誉评估的重要参考维度；网关可结合域名年龄与注册商信誉做风险打分
4. **Sliver 取代 Cobalt Strike 的趋势**：C2 框架的检测特征发生变化，邮件网关与沙箱的 IOC 库应同步更新 Sliver/AsyncRAT/Remcos 相关特征
5. **云端托管变化**：DigitalOcean 仍居新发现 C&C 首位，但其数量也在下降（-29%）；中国云（阿里云/腾讯云）C&C 显著减少，可作为境内云邮件服务的正面信号

## 八、参考来源

1. Spamhaus《Botnet Threat Update January to June 2026》（2026-07-10，The Spamhaus Team）：https://www.spamhaus.org/resource-hub/botnet-c-c/botnet-threat-update-january-to-june-2026/
2. 报告 PDF 原文：https://content.spamhaus.org/d32359a1-1665-4dd8-8cf4-a75d2f66fc1d.pdf
3. Spamhaus Botnet C&C 资源中心：https://www.spamhaus.org/resource-hub/botnet-c-c/
4. Spamhaus《Botnet Spotlight: Pressure rises on botnets — but the fight is far from over》（2026-01-27，Jonas Arnold）：https://www.spamhaus.org/resource-hub/botnet-c-c/botnet-spotlight-pressure-rises-on-botnets-but-the-fight-is-far-from-over/
5. Spamhaus《Botnet Threat Update July to December 2025》（2026-01-12）：https://www.spamhaus.org/resource-hub/botnet-c-c/botnet-threat-update-july-to-december-2025/

### 相关文章

* [Spamhaus DBL 域名黑名单数据源深度解读 — RFC 5782 DNSBL 架构与 dbl.spamhaus.org 查询实践](/kb/spamhaus-dbl-datasource.html)
* [DNS 黑名单机制与应对策略 — DNSBL/RBL/URIBL 原理、查询方法与自建方案](/kb/dnsbl-blacklist-guide.html)
* [邮件合规与发件人信誉：收件箱不会忘记 — Spamhaus 权威解读](/kb/email-compliance-reputation-spamhaus.html)
