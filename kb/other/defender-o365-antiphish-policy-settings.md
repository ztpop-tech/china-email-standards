---
title: "Microsoft Defender for Office 365 反钓鱼策略有哪些必调设置项？"
source: "https://ztpop.net/kb/defender-o365-antiphish-policy-settings.html"
license: CC-BY 4.0
---

# Microsoft Defender for Office 365 反钓鱼策略有哪些必调设置项？

1
Microsoft Defender for Office 365 反钓鱼策略有哪些必调设置项？
▼

**先分清哪些设置人人都有、哪些要 Defender**

官方文档把反钓鱼策略的设置划成两层。**所有云邮箱可用**的是欺骗设置（spoof settings）、未认证发件人标识、首次联系安全提示、以及策略适用范围等通用设置。**仅 Defender for Office 365 可用**的是仿冒防护（impersonation protection，含用户仿冒、域仿冒、邮箱智能仿冒）、仿冒安全提示、受信任发件人与域清单、以及钓鱼判定阈值。这条分界线很重要：仅有内置基础防护的租户，即便照着配置清单逐条找，也找不到仿冒防护相关选项。默认反钓鱼策略不能改名、不能指定收件人范围，自定义策略则至少要配一项收件人条件。

**欺骗设置与 DMARC 联动**

`Enable spoof intelligence` 在默认策略与新建自定义策略中**默认开启**，用于识别来自外部与内部域的被检出仿冒发件人。对被阻断仿冒发件人的处置动作有两个选项：移入垃圾邮件文件夹（默认）或隔离（可绑定隔离策略）。真正需要重点关注的是 `Honor DMARC record policy when the message is detected as spoof`——开启后会展开两个子项，分别指定当邮件被判定为仿冒且发件方 DMARC 策略为 `p=quarantine` 时的动作（隔离或移入垃圾箱），以及 `p=reject` 时的动作（隔离或拒收）。这意味着「是否尊重对方发布的 DMARC 严格策略」在云邮箱侧是可配置的，而非自动执行；对合规要求高的组织，这一开关及其两个子项应当明确设定并留档，而不是沿用默认。

**仿冒防护：对抗认证挡不住的那一类攻击**

仿冒防护解决的是 SPF/DKIM/DMARC 从原理上挡不住的问题——攻击者不伪造你的域名，而是用近似域名或仅改显示名。`Enable users to protect` 添加受保护的发件人地址，官方限额为**每策略最多 350 个**；`Enable domains to protect` 添加受保护发件域，自定义域**每策略最多 50 个**。两者被检出后的动作均有六选项：不采取任何动作（默认）、重定向到其他地址、移入垃圾箱、隔离、投递并加 Bcc、投递前删除。邮箱智能方面，`Enable mailbox intelligence`（基于收件人历史通信图谱建模）**默认开启**，但把它用于仿冒判定的 `Enable intelligence for impersonation protection` **默认关闭**——这是最常被忽略的一项。`Trusted senders and domains` 作为仿冒防护的例外清单，上限 1024 条，且**受信任项不自动继承子域**。

**安全提示与判定阈值**

提示类设置包括：显示用户仿冒安全提示、显示域仿冒安全提示、显示用户仿冒异常字符安全提示（三者分别依赖对应的保护开关已启用），以及不依赖任何前置条件的首次联系安全提示（`Show first contact safety tip`）。后者对收件人极少或从未与之通信的发件人给出提示，对识别新注册的一次性钓鱼域名很有价值。判定灵敏度由 `Phishing email thresholds` 控制，四档分别为 `1 - Standard`（默认）、`2 - Aggressive`、`3 - More aggressive`、`4 - Most aggressive`，官方直言档位越高误报越多。

**配置顺序建议**

从文档结构可读出一条务实的推进顺序：**第一步**确认欺骗智能已开启，并按组织的风险偏好明确设定「遵从发件方 DMARC 策略」及其 quarantine/reject 两个子动作；**第二步**打开首次联系安全提示，这是零成本、零误伤的收益项；**第三步**把高管、财务、HR、法务等高价值账号加入用户仿冒保护，把本域与常被冒充的核心合作方域加入域仿冒保护，并把动作从默认的「不采取任何动作」改为实际生效的处置；**第四步**开启邮箱智能用于仿冒防护的子开关；**第五步**先用默认阈值观察一段时间的误报与漏报比例，再决定是否上调档位。全过程配合受信任发件人清单收敛误伤，并留意该清单不覆盖子域这一细节。

参考：Microsoft Learn 官方文档《Anti-phishing policies in Microsoft 365》，https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-policies-about

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/defender-o365-antiphish-policy-settings.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
