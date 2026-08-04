---
title: "Trend Micro 报告的 TONResolver 钓鱼攻击如何投递与规避封禁？"
source: "https://ztpop.net/kb/trendmicro-tonresolver-phishing-2026.html"
license: CC-BY 4.0
---

# Trend Micro 报告的 TONResolver 钓鱼攻击如何投递与规避封禁？

1
Trend Micro 报告的 TONResolver 钓鱼攻击如何投递与规避封禁？
▼

**攻击背景**

Trend Micro 研究团队于 2026 年 5 月下旬起观测到一批投向日本 Booking.com 合作住宿企业的可疑邮件，遥测显示 2026 年 5 月 17 日至 6 月 8 日期间来自日本地区的访问最为集中。报告将该恶意载荷命名为 TONResolver，检测名为 `TrojanSpy.JS.TONRESOLVER.A`，其定位为初始访问与命令执行立足点，后续活动指向凭据窃取与进一步渗透。

**邮件投递手法**

报告记录了两类投递路径。一类是批量钓鱼：邮件伪装成客人投诉或住宿评价请求（日文主题如「重要：ゲスト滞在レビュー依頼」），借助某日程工具服务的通知功能发出，从而绕开对发件域的常规认证判断。另一类是通过 Gmail 发起的会话式攻击：先发一封不含任何 URL 的普通咨询邮件，待酒店员工回复建立信任后，再在跟进邮件中投放恶意链接，其耐心程度接近定向攻击手法。

**载荷链路**

受害者点击邮件链接后从可疑站点下载 ZIP 压缩包，包内是一个伪装成照片的 LNK 快捷方式文件。点击 LNK 会触发内嵌的 PowerShell 命令，还原下载域名并拉取脚本，最终加载 Node.js 与恶意 JavaScript。感染后的终端保持 Keepalive 循环等待指令，只要感染存续，凭据被窃与追加投毒的风险就持续存在。

**抗封禁机制与防御**

TONResolver 把 C&C 域名写在 TON 区块链的智能合约数据单元中，恶意 JS 通过公开 API 读取合约方法取回当前 C&C 地址；攻击者可从管理钱包发送内部消息随时替换域名，即便原服务器被封禁或下线也能无缝切换，这使得基于硬编码 IOC 的封堵大幅失效。Trend Micro 给出的缓解建议包括：在代理网关侧过滤对区块链 API 端点的访问，无业务需求则预先阻断；限制 `powershell.exe` 的外联；对 Node.js 创建的可疑自启动项建立检测；并复核邮件攻击面，收敛非必要的外部通信通道。

参考：Trend Micro 官方研究报告《TONResolver RAT Abuses TON Blockchain to Target Japan's Hotel Industry》，https://www.trendmicro.com/en\_us/research/26/f/tonresolver.html

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/trendmicro-tonresolver-phishing-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
