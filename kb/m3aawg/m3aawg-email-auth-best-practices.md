---
title: "M3AAWG《邮件认证推荐最佳实践》：SPF/DKIM/DMARC/ARC 落地清单"
source: "https://ztpop.net/kb/m3aawg-email-auth-best-practices.html"
license: CC-BY 4.0
---

# M3AAWG《邮件认证推荐最佳实践》：SPF/DKIM/DMARC/ARC 落地清单

## 概述

M3AAWG（Messaging, Malware and Mobile Anti-Abuse Working Group）是全球最大的反在线滥用行业组织，其成员涵盖 Gmail、Yahoo、Microsoft 等大型邮箱提供方与大量发件组织。该 BCP 文档给出基于 SPF、DKIM、DMARC 与 ARC 的邮件认证最佳实践。M3AAWG 的核心论断是：**认证是二元的——要么做对，要么没做**，不像内容打分那样存在概率空间。行业的最终目标是「No Auth, No Entry（无认证不进入）」：无法确定来源身份的邮件将不再被投递。

## SPF 建议

* 为 `MAIL FROM` 与 `EHLO` 域都发布 SPF 记录。
* SPF 记录应以 `~all`（软失败）收尾；对**从不发信的域**应发布 `-all`（硬失败）。
* 不要授权超出必要的 IP；避免过度 `include` 触发 DNS 10 次查询上限。
* SPF 验证的是 Return-Path，应使其与信头 `From` 域**对齐**。

## DKIM 建议

* 对全部外发邮件用**与 From 域对齐**的域进行签名。
* 遵循密钥管理最佳实践：定期轮换密钥、维持行业标准最小密钥长度、安全存储私钥。
* 使用多个选择器支持并行轮换，避免轮换期认证中断。

## DMARC 建议

* 策略声明应**尽可能用 `p=reject`**，否则用 `p=quarantine`。
* `p=none`、`sp=none` 与 `pct<100` 只应视为过渡态，目标是尽快移除。
* DMARC 策略记录应**包含报告标签 `rua`**，以持续收集聚合报告。

## ARC：转发链认证恢复

该 BCP 还涵盖 ARC（Authenticated Received Chain）。当邮件经合法转发、原有 SPF/DKIM 因路径改变而失效时，ARC 由转发服务对已有的认证结果进行"链式"背书，使下游仍能信任原始认证状态，缓解转发导致的误判。

## 反 SPF 升级攻击：用 DKIM 对齐

M3AAWG 特别指出：当一个域的 SPF 记录过于宽松时，攻击者可利用「SPF 升级攻击」在某些条件下成功伪造该域。优先让 DKIM 签名域与 From 域对齐，是缓解该风险的关键手段——这也与 NIST SP 800-177r1 的"DKIM 比 SPF 更稳健"判断一致。

## 落地清单小结

| 协议 | 关键动作 |
| --- | --- |
| SPF | ~all 收尾；不出信域 -all；控制 include 深度；对齐 Return-Path |
| DKIM | 全量签名且对齐 From；定期轮换；≥2048 位；私钥安全存储 |
| DMARC | 目标 p=reject；含 rua 报告；p=none 仅过渡 |
| ARC | 转发场景背书原始认证链 |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/m3aawg-email-auth-best-practices.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
