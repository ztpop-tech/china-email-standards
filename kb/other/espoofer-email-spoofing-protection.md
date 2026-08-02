---
title: "邮件伪造攻击与防护：espoofer 测试与 SPF/DKIM/DMARC 组合加固"
source: "https://ztpop.net/kb/espoofer-email-spoofing-protection.html"
license: CC-BY 4.0
---

# 邮件伪造攻击与防护：espoofer 测试与 SPF/DKIM/DMARC 组合加固

**一、espoofer 是什么**

espoofer 是安全研究员 Chen Ji（陈吉）于 2020 年发布的开源邮件伪造检测工具（GitHub: chenjj/espoofer，Python 实现）。它的定位是「邮件伪造攻击测试框架」：自动探测目标域名的 SPF、DKIM、DMARC 配置状态，判断该域名是否存在可被利用的伪造漏洞，并实际构造攻击邮件演示漏洞利用路径。工具核心价值在于帮助安全团队和企业邮件管理员在攻击者利用之前，发现自己的域名是否可以被冒充。

espoofer 的攻击面分为三类：**显示名欺骗**（Display Name Spoofing，在 From 头中伪造显示名，RFC 5322 允许显示名与邮箱地址分离）、**伪造 DKIM 签名**（当域名存在 DKIM 但选择器选择器可枚举或密钥配置不当）、**绕过 RFC 5322.From 校验**（利用接收方仅校验 RFC 5322.From 而忽略 RFC 5321.MailFrom 或反之的解析差异）。这三类漏洞在 2020 年前后广泛存在于主流邮箱服务商的解析逻辑中，espoofer 因此被 Google、Microsoft 等厂商的安全团队用于评估自身与第三方邮件基础设施。

**二、espoofer 判定的域名可伪造性矩阵**

espoofer 的核心判定逻辑与同类工具（如 Spoofy）一致：组合分析域名 SPF 与 DMARC 记录，得出「是否可伪造」结论。该矩阵也是 ztpop.net 邮件伪造风险评估器（在线工具）的判定依据：

· 无 SPF 且无 DMARC → **完全可伪造**（攻击者可任意冒充发件人，接收方无任何认证依据）；  
· SPF 为 ?all 或 +all 且 DMARC p=none → 完全可伪造（SPF 软失败无约束力，DMARC 仅报告不拒收）；  
· SPF 为 ~all（软失败）且无 DMARC 或 p=none → **高可伪造**（SPF 校验大概率失败，但 DMARC 不拒收）；  
· SPF 为 -all（硬失败）且 DMARC p=quarantine → 中可伪造（有防护但未达最严）；  
· SPF 为 -all 且 DMARC p=reject → **不可伪造**（DMARC 强制接收方拒收未认证邮件，RFC 7489 最佳实践）。

注意：DMARC 采用「SPF 或 DKIM 任一通过即可」的宽松判定（RFC 7489 §6.6.3），因此即使 SPF 配置完善，若 DKIM 选择器密钥泄露或选择器可被枚举，仍存在伪造窗口。完整链路防护需要 SPF、DKIM、DMARC 三者同时到位。

**三、使用 espoofer 进行自查**

espoofer 是 Python 3 命令行工具，典型用法：`python3 espoofer.py -d victim.com --spoof`（探测并尝试攻击 victim.com）或 `python3 espoofer.py -d victim.com --analyze`（仅分析不攻击）。它支持 SMTP 直连发送、SMTPS、以及通过自定义 SMTP 中继发送攻击邮件。使用前请确认已获得目标域名所有者的书面授权——未经授权对他人域名实施伪造攻击测试可能违反当地法律（如《中华人民共和国网络安全法》关于未经授权测试的规定），仅建议用于自查自有域名。

自查流程建议：① 使用 ztpop.net 邮件伪造风险评估器或 espoofer --analyze 分析自有域名当前风险等级；② 使用 espoofer --spoof 向自己的邮箱发送测试邮件，确认客户端与网关的展示逻辑；③ 依据判定结果按第四节加固；④ 加固后重新检测，确认风险等级降至「不可伪造」。重复此闭环直至达标。

**四、SPF/DKIM/DMARC 组合加固清单**

根据 RFC 7208（SPF）、RFC 6376（DKIM）、RFC 7489（DMARC）及 M3AAWG 最佳实践，组合加固的完整检查项如下：

1. **SPF**：记录以 `-all` 结尾（禁止 `+all`、慎用 `~all`）；SPF 中不要使用 `ptr` 机制（RFC 7208 §5.5 明确弃用，性能与安全性均差）；DNS 查询次数（含 include 展开）不超过 10 次上限（RFC 7208 §4.6.4）；SPF 记录长度不超过 255 字符，避免 DNS 截断（RFC 1035）。  
2. **DKIM**：密钥长度 ≥2048 位 RSA（RFC 6376 建议，1024 位已可被暴力破解尝试）；定期轮换密钥（建议 6 个月，M3AAWG 建议）；确保 `s=` 选择器值不可被攻击者枚举（避免使用 `default` 等常见值作为唯一选择器时配合弱密钥）；DNS 公钥记录 `p=` 值完整无截断。  
3. **DMARC**：策略逐步从 p=none → p=quarantine → p=reject 演进（每个阶段至少观察 2-4 周 RUA 报告）；`pct=100` 全覆盖；配置 `rua` 聚合报告接收地址并持续监控；`sp=` 子域策略与主域一致；`adkim/aspf` 建议设为 `s`（严格模式）降低宽松匹配被利用风险。  
4. **其他**：DKIM 与 DMARC 对齐域名使用同一主域（避免第三方代发域造成 SPF/DKIM 不对齐）；启用 MTA-STS（RFC 8461）与 TLS-RPT（RFC 8460）防传输层降级；对自有域名定期用伪造风险评估器复测。

**五、与 ztpop.net 工具联动**

本文配套的在线工具：[邮件伪造风险评估器](/tools/spoof-risk-checker.html)（DoH 读取 SPF/DMARC 记录，按本节矩阵自动判定风险等级并给出加固建议，纯浏览器端运行）；[SPF 深度诊断工具](/tools/spf-deep-diagnose.html)（逐机制解析、lookup 计数、void lookup 检测）；[域名健康评分](/tools/domain-health-score.html)（SPF/DKIM/DMARC/MTA-STS/TLS-RPT/BIMI/MX/黑名单八项百分制评分）。建议三工具组合使用完成自检闭环。

### 相关主题

* [DMARC 策略渐进式部署：从 p=none 到 p=reject](/kb/dmarc-policy-gradual.html)
* [DMARC p=reject 部署后的常见问题排查](/kb/dmarc-reject-troubleshooting.html)
* [DKIM 密钥轮换管理实践](/kb/dkim-key-rotation-management.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/espoofer-email-spoofing-protection.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
