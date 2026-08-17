---
title: "DMARCbis 落地实践：DMARC 记录配置示例与 RFC 9989 新标签使用指南"
source: "https://ztpop.net/kb/dmarcbis-config-examples.html"
license: CC-BY 4.0
---

# DMARCbis 落地实践：DMARC 记录配置示例与 RFC 9989 新标签使用指南

# DMARCbis 落地实践：DMARC 记录配置示例与 RFC 9989 新标签使用指南

⁣​‌​‌‌​‌​​‌​‌​‌​​​‌​‌​​​​​‌​​‌‌‌‌​‌​‌​​​​​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​​​​‌‌‌​​​​‌‌‌‌‌​​​‌‌‌​‌‌​​​‌‌​​​‌​‌‌‌‌‌​​​‌​​​‌‌​​‌​​​‌​‌​‌​​​‌​​​‌​​​‌​‌⁤

RFC 9989 / RFC 9990 / RFC 9991 / 2026 年 5 月发布

2026-08-03 · ztpop.net 邮件技术知识库

## 一、配置层面发生了什么变化

2026 年 5 月发布的 RFC 9989（DMARC 主规范，替代 RFC 7489）、RFC 9990（聚合报告，替代 RFC 7489 报告章节）与 RFC 9991（失败报告，替代 RFC 7489 报告章节并更新 RFC 6591）共同构成 DMARCbis。对配置实践者而言，**记录语法（tag=value 形式）与 DNS 部署位置（\_dmarc 子域 TXT 记录）没有变化**，但可用标签集合与语义发生了实质性调整：新增 3 个标签（np、psd、t）、移除 3 个标签（pct、rf、ri）。

RFC 9989 Section 4.7 规定：DMARC Policy Record 沿用 DKIM 的 DNS 记录 tag=value 语法（RFC 6376），仅处理 IANA「DMARC Tags Registry」中登记的标签，未知标签必须忽略（MUST be ignored）。这意味着老接收方遇到新标签会安全跳过，新接收方遇到已移除标签（如残留的 pct=）也会按未知标签忽略——**迁移期双向兼容**。

## 二、RFC 9989 完整标签清单

| 标签 | 状态 | 取值 | 默认 | 说明（依据 RFC 9989 §4.7） |
| --- | --- | --- | --- | --- |
| **v** | 必需 | DMARC1 | — | 版本标识，必须出现在记录首位 |
| **p** | 推荐 | none / quarantine / reject | 缺失视为 none | 域所有者评估策略；适用于该域及其子域（除非 sp/np 另行声明） |
| **sp** | 可选 | none / quarantine / reject | 同 p | 仅适用于**存在的**子域；在子域上发布的记录中 sp 被忽略 |
| **np** | 新增 | none / quarantine / reject | 回退 sp → p | 仅适用于**不存在的**子域（NXDOMAIN，定义同 RFC 8020） |
| **t** | 新增 | y / n | n | 测试模式：请求不实际应用 p/sp/np 声明的策略，而是降一级执行（reject→quarantine，quarantine→none）；不影响报告生成；对 p=none 无效果 |
| **psd** | 新增 | y / n / u | u | 发布者是否为公共后缀域（PSD）；y 用于 PSO 发布的记录 |
| **rua** | 可选 | URI 列表（逗号分隔） | — | 聚合报告目标；未提供则接收方不得生成聚合报告（RFC 9990） |
| **ruf** | 可选 | URI 列表（逗号分隔） | — | 失败报告目标；未提供则接收方不得生成失败报告（RFC 9991） |
| **fo** | 可选 | 0 / 1 / d / s（冒号分隔） | 0 | 失败报告触发条件；0 与 1 互斥；无 ruf 时本标签被忽略 |
| **adkim** | 可选 | r / s | r | DKIM 标识符对齐模式（宽松/严格） |
| **aspf** | 可选 | r / s | r | SPF 标识符对齐模式（宽松/严格） |
| **pct** | **已移除** | — | — | RFC 9989 Appendix A.6：运营经验表明中间值从未被准确执行；功能由 t 标签承接 |
| **rf** | **已移除** | — | — | 报告格式只有一种（AFRF/XML），定义多余 |
| **ri** | **已移除** | — | — | 接收方很少遵循指定间隔，改由接收方自行决定 |

此外 RFC 9989 移除了报告 URI 中「最大报告大小」参数（RFC 9990 附录 C），报告发现机制（PSL 依赖）被 **DNS Tree Walk** 取代（RFC 9989 §4.10）。

## 三、场景化 DNS 记录配置示例

以下示例均为可直接复制的 `_dmarc.example.com` TXT 记录（域名所有者视角）。所有示例假设 SPF（RFC 7208）与 DKIM（RFC 6376）已先行配置完毕——DMARC 本身不提供认证，只对 SPF/DKIM 结果做对齐判定。

### 3.1 基线：监控模式（p=none）

RFC 9989 域名所有者行动指南（§5.1）推荐所有新部署从监控模式起步，收集至少一个报告周期的基线数据：

```
v=DMARC1; p=none; rua=mailto:dmarc-rua@example.com
```

该记录请求接收方对未通过 DMARC 的邮件不采取动作，仅发送聚合报告。RFC 9990 §3.5.2 要求报告邮件流本身必须通过 DMARC 对齐验证（aligned pass），以降低伪造报告风险——因此 `rua` 邮箱所在域也应具备有效的 SPF/DKIM 配置。

### 3.2 子域差异化：sp 与 np

RFC 9989 将子域策略拆分为两级，这是与 RFC 7489 最实质的配置能力差异：

```
v=DMARC1; p=reject; sp=quarantine; np=none; rua=mailto:dmarc-rua@example.com
```

语义分解：

* `p=reject`：主域（example.com）不通过 DMARC 的邮件一律拒绝
* `sp=quarantine`：**存在的**子域（如 mail.example.com、news.example.com）不通过时隔离
* `np=none`：**不存在的**子域（DNS 返回 NXDOMAIN，如 typo.example.com）不通过时仅监控

`np` 标签解决了一个长期痛点：攻击者利用未注册子域（如 `invoice.example.com` 并不存在）伪造发信时，若该子域恰好落入接收方的树遍历路径，主域 p=reject 策略可能被继承到不存在的子域。RFC 9989 通过 np 让域所有者对 NXDOMAIN 域单独声明宽松策略，避免域名拼写错误与临时 DNS 故障导致的误拒。

### 3.3 强制执行前测试：t=y

替代 pct= 的测试模式。RFC 9989 Appendix A.6 指出，pct= 在实操中只有 0 与 100 被准确执行，中间值实现差异巨大；t 标签将「测试/非测试」二元语义显式化：

```
v=DMARC1; p=reject; t=y; rua=mailto:dmarc-rua@example.com
```

当 t=y 时，接收方被请求将声明策略降一级执行：p=reject 实际按 quarantine 处理，p=quarantine 实际按 none 处理。报告照常生成，因此域所有者可以在不承担误拒风险的前提下观察：若大量合法邮件本会被 reject，聚合报告中 `disposition` 字段将显示实际执行的降级策略，而 `policy_published` 中记录声明的原始策略（RFC 9990 §3.1.1.5 新增 `testing` 元素，值 y/n）。

注意 RFC 9989 §3.2.11 与 Appendix A.6 同时提醒：t=y 对 p=none 无效果，且此标签只表达请求，接收方是否采纳由其实施决定。

### 3.4 完整强制执行（含失败报告）

```
v=DMARC1; p=reject; sp=reject; np=none; adkim=s; aspf=s; fo=1; rua=mailto:dmarc-rua@example.com; ruf=mailto:dmarc-ruf@example.com
```

要点：

* `adkim=s; aspf=s`：严格对齐。RFC 9989 §C.3 明确：严格对齐 + 在所有实际使用的 Author Domain 上显式发布记录，可完全规避 Tree Walk 与 PSL 实现的互操作差异
* `fo=1`：任一认证机制未产生对齐 pass 即生成失败报告（RFC 9991 格式，基于 RFC 6591 ARF）。`fo=0`（默认）要求全部机制失败才触发
* `ruf` 与 `fo` 成对使用：无 ruf 时 fo 被忽略（RFC 9989 §4.7）

### 3.5 严格模式仅用于 DKIM 签名域

RFC 9989 §7.4 强调：SPF 在间接邮件流（转发、邮件列表）中几乎必然失败，因此仅依赖 SPF 实现 DMARC pass 的域若发布 p=reject 必须同时部署有效的 DKIM 签名。推荐配置：

```
v=DMARC1; p=quarantine; adkim=s; aspf=r; rua=mailto:dmarc-rua@example.com
```

DKIM 采用严格对齐（签名域 d= 必须与 From 域完全一致），SPF 保持宽松对齐（允许子域），兼顾转发场景兼容性。

### 3.6 多报告目标与外部报告接收方

```
v=DMARC1; p=none; rua=mailto:dmarc@example.com,mailto:rua@thirdparty.example; ruf=mailto:forensic@thirdparty.example; fo=1
```

RFC 9989 §4.6 变更：记录中列出的每个报告 URI 都应收到报告（SHOULD），替代 RFC 7489 的「至少支持两个」表述。若报告目标（如 thirdparty.example）与策略域（example.com）的组织域不同，接收方必须执行外部目标验证（RFC 9990 §4）：在 `example.com._report._dmarc.thirdparty.example` 查询 TXT 记录，确认该记录含 `v=DMARC1` 起始的标签串才向该外部地址发送报告。报告接收方可通过这一机制覆盖 rua 目标（覆盖 URI 必须使用同一目标主机）。

### 3.7 公共后缀运营商（PSO）发布记录

RFC 9989 用 DNS Tree Walk 整合了 PSD 策略发现（废弃 RFC 9091）。PSO 在公共后缀域发布记录时必须声明 psd=y，使遍历在该层停止：

```
v=DMARC1; p=none; psd=y; rua=mailto:psd-dmarc@registry.example
```

普通域所有者（非 PSO）**不应**使用 psd=y。默认值 u 表示「不确定，由 Tree Walk 判定」，大多数记录无需显式写 psd。

## 四、从 RFC 7489 记录迁移对照

对已有 DMARC 部署，迁移只需三步：

1. **删除 pct、rf、ri 标签**：它们已被 RFC 9989 移除。残留的 `pct=100` 会被新实现按未知标签忽略（行为同 pct=100 默认），但 `pct=0` 的「From 头重写信号」语义应由 `t=y` 显式承接（RFC 9989 Appendix A.6）
2. **按需新增 np 标签**：希望区分「存在子域」与「不存在子域」策略时添加；不加则回退 sp → p，与旧行为一致
3. **按需新增 t=y 标签**：在策略升级（quarantine→reject）前作为最终测试手段

| RFC 7489 写法 | RFC 9989 对应写法 | 行为差异 |
| --- | --- | --- |
| `p=reject; pct=50` | 不保留 pct；如需部分放行改用 `p=quarantine` 或 `p=reject; t=y` | pct 中间值从未被准确执行；t=y 提供确定性降级 |
| `p=reject; pct=0` | `p=reject; t=y` | t=y 保留「不实际应用策略」的语义，且语义显式 |
| `rf=afrf` | 删除 | 报告格式唯一，无需声明 |
| `ri=86400` | 删除 | 报告间隔由接收方决定 |
| 仅 p/sp 管理子域 | p/sp/np 三级 | np 覆盖 NXDOMAIN 子域（RFC 8020） |

## 五、发布前校验清单

1. **v=DMARC1 必须出现在记录首位**，后续标签顺序不限；未知标签被忽略，但语法错误（如未闭合引号、非法值）可能导致整条记录被判无效
2. **仅使用 IANA DMARC Tags Registry 登记的标签**；不再使用 pct/rf/ri
3. **rua 目标邮箱域需有完整认证配置**（报告邮件本身需通过 DMARC 对齐验证，RFC 9990 §3.5.2）
4. **外部报告目标需提前发布 `<策略域>._report._dmarc.<目标主机>` TXT 记录**（RFC 9990 §4），否则接收方不会发送报告
5. **严格对齐（adkim=s/aspf=s）前确认所有合法发信路径均已覆盖**，否则将产生大量 fail 记录
6. **升级 p=reject 前评估邮件列表与转发场景**：RFC 9989 §7.4 明确通用邮件域 SHOULD NOT 部署 p=reject，且接收方不应仅凭 p=reject 拒绝邮件
7. **用 DNS 查询工具验证 TXT 记录生效**（dig TXT \_dmarc.example.com），并检查接收方解析是否受 CNAME 链影响

## 六、报告格式变化对配置的影响

RFC 9990 定义的聚合报告 XML 命名空间更新为 `urn:ietf:params:xml:ns:dmarc-2.0`（示例见 RFC 9990 Appendix B），`policy_published` 新增 `testing`（对应 t 标签）与 `discovery_method`（treewalk / psl）元素；DKIM 结果中 `selector` 变为必填。聚合报告文件命名格式为 `receiver!policy-domain!begin!end[!unique-id].xml[.gz]`（RFC 9990 §3.5.2）。对配置者的实际影响：

* t=y 测试期间，报告中的 `policy_published/p` 显示声明策略，`row/policy_evaluated/disposition` 显示实际执行的降级策略——解读报告时需区分两者
* 解析旧版（dmarc-1.0 命名空间）报告的本地工具需同步升级，否则新报告可能解析失败

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarcbis-config-examples.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
