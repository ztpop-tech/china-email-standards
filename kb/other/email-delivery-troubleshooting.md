---
title: "邮件投递故障排查：认证检查、内容分析、发送行为与诊断工具"
source: "https://ztpop.net/kb/email-delivery-troubleshooting.html"
license: CC-BY 4.0
---

# 邮件投递故障排查：认证检查、内容分析、发送行为与诊断工具

参考 Google/Microsoft/Yahoo 邮件服务商投递指南

邮件投递问题的排查是一个系统工程，涉及发件方基础设施、收件方策略、网络路径、内容质量等多维度。本文提供标准化的邮件投递故障排查流程。

## 投递问题排查三层次

### 第一层：基础认证检查

收到邮件被拒或进入垃圾箱的反馈后，首先检查邮件认证配置：

1. SPF 记录是否包含所有发件 IP？用 dig 验证：`dig txt example.com +short | grep spf`
2. DKIM 签名是否正确？邮箱服务商的 Authentication-Results 头中标示 dkim=pass/fail
3. DMARC 策略是否合理？是否设置了 rua/rf 报告地址？
4. PTR 记录是否指向发送域？`dig -x [IP] +short` 检查结果是否与域匹配

### 第二层：内容质量分析

分析邮件内容是否触发了垃圾规则：

* 检查邮件中图片/文字比例是否超标（建议 <60% 图片）
* 链接数量是否过多（建议 <10 个链接）
* 主题行是否包含垃圾触发词
* 邮件是否附带会被拦截的附件类型（.exe、.scr、.zip 中的脚本文件等）
* 确认发件地址不是常见的垃圾邮件发件模式（如随机生成的本地部分）

### 第三层：发送行为分析

* 发送量是否保持稳定节奏？是否有突增导致限流？
* 发送时间是否在收件人的正常工作时间？
* 是否使用了混合 IP 池（信誉好/差的 IP 混合发送影响整体评分）
* 收件人列表的活跃度如何？大量不活跃用户会拖低域信誉

## 各邮箱服务商投递问题诊断入口

| 邮箱服务商 | 诊断工具 | 投诉循环 (FBL) |
| --- | --- | --- |
| Gmail | [Postmaster Tools](https://postmaster.google.com) | Gmail FBL (ABUSE) |
| Outlook.com | [Sender Support](https://sendersupport.olc.protection.outlook.com/) | JMRP (Junk Mail Reporting Program) |
| Yahoo Mail | [Yahoo Postmaster](https://postmaster.yahoo.com/) | Yahoo FBL |
| QQ/国内主流邮箱服务商 | 无公开 Postmaster Tools | 无公开 FBL |
| 163 邮箱 | 无公开 Postmaster Tools | 无公开 FBL |

## 常用邮件投递测试工具

* **easydmarc.com/tools/email-test**：全面的邮件认证测试（SPF/DKIM/DMARC/BIMI）
* **www.mail-tester.com**：测试单封邮件的垃圾评分，提供改进建议
* **www.litmus.com/email-testing**：邮件在各邮件客户端的渲染和投递测试
* **mailflow.com**：邮箱服务商收件箱放置率测试

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-delivery-troubleshooting.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
