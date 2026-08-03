---
title: "如何防御邮箱数据外泄（内部威胁）？"
source: "https://ztpop.net/kb/mailbox-data-exfiltration-defense.html"
license: CC-BY 4.0
---

# 如何防御邮箱数据外泄（内部威胁）？

1
如何防御邮箱数据外泄（内部威胁）？
▼

**检测指标**

关注异常行为：突然配置永久自动转发（收件箱规则含 redirect/forward 到外部域）、非工作时间大批量 POP/IMAP 拉取或 EWS/Graph API 导出、单账号短时间下载上千封邮件、收件箱规则隐藏痕迹（标记已读或移动到不可见文件夹）。可通过邮件网关与 SIEM 关联登录地、客户端类型、数据量阈值告警。

**防御措施**

* 禁用或审批制管理自动转发到外部域，默认阻断转发到非受信任域。
* 部署 DLP 对含敏感标记的附件与正文做外发拦截与水印。
* 对邮箱协议（POP/IMAP/EWS/ActiveSync）按角色最小开放，关键账号仅留 Web 与受管客户端。
* 开启异地登录 MFA，并对特权账号做会话录制与双人复核。

**真实攻击手法**

内部人员常先用手边 Outlook 规则把高管往来自动转发到个人邮箱；离职前通过导出 PST 或脚本调用 Microsoft Graph 批量抓取通讯录与历史邮件；也有借被攻陷的 OA 服务账号以 EWS 订阅推送方式外传。攻击者偏好「合法功能」而非恶意工具，传统防病毒难以发现。

**基准控制项**

对照 CIS Controls v8：控制项 3（数据保护配置）、6（访问控制）、13（网络监控与日志）要求对邮件数据分级、限制外发通道并留存审计。NIST SP 800-53 的 AC-4（信息流强制）、AU-12（审计生成）、SC-7（边界保护）共同构成可审计的最小权限基线。

参考：MITRE ATT&CK T1114（Email Collection）/ T1567（Exfiltration Over Web Service）、CIS Controls v8 控制项 3/6/13、NIST SP 800-53 AC/ AU

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/mailbox-data-exfiltration-defense.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
