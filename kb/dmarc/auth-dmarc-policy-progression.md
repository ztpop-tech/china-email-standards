---
title: "DMARC 从 p=none 收敛到 p=reject，中间怎么走才不会误杀正常邮件？"
source: "https://ztpop.net/kb/auth-dmarc-policy-progression.html"
license: CC-BY 4.0
---

# DMARC 从 p=none 收敛到 p=reject，中间怎么走才不会误杀正常邮件？

1
DMARC 从 p=none 收敛到 p=reject，中间怎么走才不会误杀正常邮件？
▼

**三档策略的语义：请求而非强制**

RFC 7489 第 6.3 节定义 `p` 的三个取值，它们表达的是域名所有者**希望接收方如何处置**未通过 DMARC 的邮件：

* `none`：不因 DMARC 失败而特殊处置，仅按常规流程处理（本质是「只观察」）。
* `quarantine`：请求接收方将失败邮件视为可疑，通常投入垃圾箱一类的隔离区。
* `reject`：请求接收方拒收失败邮件。

**务必理解：**这是「请求」，最终处置权在接收方。所以策略收敛的目的不是「命令别人拦截」，而是**让自己的域具备可被信任的判定依据**。

**阶段一：p=none，把发送源看全**

起步必须是 `p=none` 且配置 `rua`，先收聚合报告：

```
_dmarc.example.com  TXT  "v=DMARC1; p=none; rua=mailto:dmarc-rua@example.com"
```

**这一阶段唯一的任务是「发现」**：报告会暴露出你自己都不知道的发送源——业务系统、监控告警、第三方通知、历史遗留脚本。

**退出条件：**连续多个报告周期内，所有出现的合法发送源都已识别并纳管，且其 DMARC 通过率稳定在高位；剩余失败流量能被明确归类为「非本方发送」。**只要还存在「不认识但看起来像自己人」的源，就不能进入下一阶段。**

**阶段二：quarantine 灰度，用 pct 控制暴露面**

RFC 7489 第 6.3 节定义 `pct` 为「请求对多大比例的失败邮件施加策略」，默认 100。灰度示例：

```
"v=DMARC1; p=quarantine; pct=25; rua=mailto:dmarc-rua@example.com"
```

可按 `pct` 递增推进：25 → 50 → 100，每一档观察若干报告周期。

**两个必须知道的细节：**

* `pct` 作用于**失败邮件**的处置比例，而非全部邮件；未被抽中的失败邮件按低一档策略处理。
* **不要长期停留在 pct<100。**它是过渡手段，不是终态；长期部分执行意味着攻击者仍有稳定的穿透概率。

**阶段三：reject 收口**

进入 `p=reject` 的前置条件应当同时满足：

1. 合法发送源**全部**具备对齐的 DKIM 签名（不要只依赖 SPF，见转发场景）。
2. `p=quarantine; pct=100` 已稳定运行足够长时间，聚合报告中无新增的合法失败源。
3. 子域侧已用 `sp` 或独立记录明确安排。
4. 报告接收与巡检已常态化，具备快速发现异常的能力。

NIST SP 800-177 Rev. 1《Trustworthy Email》同样把 SPF、DKIM、DMARC 作为可信邮件的基础机制加以推荐，可作为内部推动策略收敛的依据文档。

**回滚触发线：先定好再上线**

收紧动作必须配一条明确的回滚线，否则出事时只能凭感觉操作。建议在变更前书面固定：

* **触发条件**：出现明确的合法业务邮件被拒/被隔离，且短时间内无法通过补签名解决。
* **回滚动作**：降一档（reject→quarantine，或调低 pct），而非直接退回 none——保留已获得的防护收益。
* **责任人与时限**：谁有权改 DNS、多久内完成、如何验证生效。

**经验：**绝大多数「上 reject 出事」的案例，根因都是阶段一没做透——存在未被发现的合法发送源。补的是观察功课，不是策略本身。

参考：[RFC 7489 Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489.txt)、[NIST SP 800-177 Rev. 1 Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/auth-dmarc-policy-progression.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
