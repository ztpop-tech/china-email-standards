---
title: "Fortinet 分析的 PureLogs 钓鱼活动攻击链是怎样的？"
source: "https://ztpop.net/kb/fortinet-purelogs-phishing-chain-2026.html"
license: CC-BY 4.0
---

# Fortinet 分析的 PureLogs 钓鱼活动攻击链是怎样的？

1
Fortinet 分析的 PureLogs 钓鱼活动攻击链是怎样的？
▼

**邮件与附件特征**

FortiGuard Labs 于 2026 年 5 月 26 日发布的分析显示，该活动以「采购订单」为主题投递钓鱼邮件，诱导收件人打开附带的 RAR 压缩包查看所谓订单。RAR 内并非文档，而是一个高度混淆的 JavaScript 文件。报告特别注明：样本邮件在主题中已被标记为病毒检出，即已被 FortiMail 服务拦截而不会投递到收件箱——这也说明网关侧的附件解包与脚本识别是链条最前端的阻断点。

**执行链路**

攻击链分四段推进：一是 JS 阶段，脚本执行后解密出 PowerShell 代码并落地到临时目录下的随机名 `.ps1` 文件，再由 `wscript.exe` 调起 `powershell.exe` 以绕过执行策略、隐藏窗口的参数运行；二是 PowerShell 阶段，脚本内含 Base64 编码且经异或与位旋转加密的数据，解密后以 `Invoke-Expression` 执行无文件脚本；三是内存注入，脚本用进程镂空技术把 .NET 模块注入到合法的 `MsBuild.exe` 进程；四是插件下载，被注入模块从资源节取出数据解密还原下载器，再从 C2 拉取无文件窃密插件并在内存中加载。

**窃取目标**

最终载荷 PureLogs 变种驻留内存并加密回传，采集范围覆盖：系统与用户信息（截图、杀软清单、系统版本、处理器、分辨率、剪贴板等）；主流浏览器保存的登录凭据、历史、自动填充、Cookie 与会话令牌；邮件客户端与常用应用中保存的凭据（研究点名了 Thunderbird、Outlook、Foxmail、FileZilla、OpenVPN 等）；即时通讯令牌；以及数十款加密货币钱包的文件与密钥。对邮件系统运维而言最需要警惕的是：邮件客户端保存的账号口令属于首要采集目标，一旦被窃即可能演化为账号接管与内部发信。

**检测与防御**

Fortinet 给出的防护路径分三层：邮件层强制附件过滤与沙箱化，尤其对压缩包内的脚本类文件；终端层禁用非必要的脚本宿主执行权限，并监控 `wscript.exe` 派生 `powershell.exe`、以及向 `MsBuild.exe` 等合法进程写入内存的镂空行为；人员层做反钓鱼意识培训与模拟演练。由于载荷全程无文件落地，基于哈希的静态检测收效有限，跨版本稳定的行为特征（进程派生关系、内存写入 API 序列、异常外联端口）才是更可靠的检测锚点。

参考：FortiGuard Labs 官方威胁研究《Phishing Campaign Deploys JavaScript-Driven PureLogs Variant to Steal Sensitive Data》（Xiaopeng Zhang，2026-05-26），https://www.fortinet.com/blog/threat-research/

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/fortinet-purelogs-phishing-chain-2026.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
