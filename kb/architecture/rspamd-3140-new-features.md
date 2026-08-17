---
title: "Rspamd 3.14.0 新特性详解：HTML 模糊哈希与 LLM 增强"
source: "https://ztpop.net/kb/rspamd-3140-new-features.html"
license: CC-BY 4.0
---

# Rspamd 3.14.0 新特性详解：HTML 模糊哈希与 LLM 增强

发布于 2026-08-17

## 版本概览

Rspamd 3.14.0 于 2025 年 11 月 10 日正式发布（Major Release），是继 3.13 之后的又一个重要版本。本次更新围绕四个方向：**HTML 内容结构化检测**、**LLM 插件的上下文增强**、**Fuzzy 存储协议的 TCP 化**，以及**URL 处理与 CTA（Call-To-Action）检测 API**。对生产部署者而言，3.14.0 同时带来若干配置层面的兼容性变化，升级前需阅读官方迁移指南。

本文基于 Rspamd 官方发布说明（rspamd.com changelog / SourceForge 官方镜像发布信息）与官方文档（docs.rspamd.com）整理，所有功能描述均可回溯到官方原始来源。

## 1. HTML 模糊哈希：结构化相似度检测

3.14.0 引入**HTML Fuzzy Hashing**（PR #5661、#5720），为模糊哈希（Fuzzy Hash）体系增加了对 HTML 邮件正文的结构化相似度检测能力。传统模糊哈希以文本内容为单位计算相似度，而 HTML 模糊哈希针对 HTML 文档的**结构特征**（标签层级、属性模式、样式结构）生成哈希，用于识别「换了文案但结构相同」的钓鱼模板。

这一能力的典型应用场景：攻击者批量发送同一钓鱼模板的变体，正文文字、链接域名不断更换，但 HTML 结构骨架保持一致。基于内容的模糊哈希（如传统 fuzzy\_check 的 shingles 哈希）难以跨变体命中，而结构哈希可以稳定识别。

配套新增**per-rule `text_hashes` 开关**（#5720）：规则可配置仅对 HTML 内容启用文本哈希匹配，避免对纯文本邮件产生不必要的计算与误报。

```
# local.d/fuzzy_check.conf 示例（示意，具体参数以官方文档为准）
fuzzy_check {
  rule "html_phish" {
    algorithm = "shingles";
    text_hashes = true;   # 3.14 新增：HTML-only 匹配开关
    match_action = "rewrite subject";
    flag = 1;
  }
}
```

## 2. TCP Fuzzy 存储协议：UDP 自动切换

3.14.0 为 Fuzzy 存储（fuzzy\_storage）提供完整的 **TCP 协议支持**（PR #5669），连接管理与帧封装达到生产级水平。客户端可在配置中声明 TCP 端点，并在 UDP 不可用时**自动切换**到 TCP，显著提升大流量场景下模糊查询的可靠性（UDP 在跨网段、高丢包环境下存在丢包风险）。

官方配置方式（示意）：

```
fuzzy_check {
  rule "local" {
    servers = "tcp://127.0.0.1:11335";  # TCP 端点
    ...
  }
}
```

对部署者而言，这一变化意味着：跨机房、跨云环境下的分布式 Fuzzy 集群可以摆脱 UDP 的 MTU 与丢包限制；大型集群建议优先评估 TCP 端点，并在升级窗口内完成协议切换验证。

## 3. LLM 插件增强：Web 搜索上下文与 Redis 记忆

3.14.0 对 GPT/LLM 插件（docs.rspamd.com/modules/gpt，自 3.9 引入）新增两项上下文能力：

* **Web 搜索上下文（search\_context）**（PR #5732）：插件自动提取邮件 URL 中的域名，将相关 Web 搜索结果注入 LLM 提示词，使模型在评估钓鱼/欺诈邮件时获得域名信誉、品牌背景等外部证据，显著提升对「伪装知名品牌域名」类攻击的判别能力。
* **Redis 记忆（context 块）**：启用后，插件按用户/域名维度在 Redis 中保存对话上下文摘要，使同一收件人（或同一发件域）的多封邮件形成连续评估，可识别跨邮件的社会工程攻击序列。

两项能力均默认关闭，需在配置中显式启用；同时依赖 Redis 可用性与 LLM API 配额。官方同时提供了 `context_augment`（自定义异步上下文注入，支持 Redis/HTTP）作为扩展点。

```
# local.d/gpt.conf 示意（3.14 新增块）
gpt {
  enabled = true;
  type = "ollama";            # 或 openai
  search_context {
    enabled = true;           # Web 搜索上下文（默认关闭）
    # 结果数、缓存 TTL 等参数按官方文档配置
  }
  context {
    enabled = true;           # Redis 用户/域名记忆（默认关闭）
  }
}
```

成本控制提示：LLM 类检查只应作为分层防御的末段——先用 RBL、Bayes、Fuzzy 等低成本信号过滤已知威胁，仅对灰色地带邮件触发 LLM 深检（官方插件默认也排除 BAYES\_SPAM 等已明确符号的邮件，见官方文档）。

## 4. 高级 URL 处理：get\_cta\_urls() 与 URL 重写

3.14.0 在 Lua API 中新增 `task:get_cta_urls()`（PR #5732），用于检测邮件中的 **CTA（Call-To-Action）链接**——即正文中视觉突出、诱导点击的「立即领取」「验证账户」「重置密码」类按钮/链接。该 API 使规则作者能够针对「唯一 CTA 链接指向可疑域名」这一典型钓鱼模式编写精确规则。

配套的 **URL 重写基础设施**（PR #5676）为 HTML 邮件中的 URL 提供统一的改写管道（如安全网关重写链接为隔离/审计地址），并内置**基于哈希的去重保护**（50,000 URL 上限），防止大型 HTML 邮件触发资源耗尽（DoS 防护）。

```
-- 自定义规则示例：唯一 CTA 指向低信誉域名
local function check_cta(task)
  local urls = task:get_cta_urls()
  if urls and #urls == 1 then
    -- 结合 URL 信誉查询做进一步判定
  end
end
```

## 5. 其他值得关注的变更

* **高级别名（aliases）与环路检测**（#5655）：别名配置增加循环引用检测，避免别名环路导致的邮件路由死循环。
* **WebUI 深色模式**（#5725）：管理界面支持深色模式与自动检测（跟随系统）。
* **Milte/集成类改进**：与主流 MTA 的 milter 集成持续完善（详见官方 changelog）。
* **升级注意**：3.14 起部分默认行为调整（如 4.0 迁移指南中提到的 `include_content_urls` 默认开启、proxy 负载均衡默认改为 token bucket 等）可能影响既有部署，升级前务必阅读官方 [Upgrading 文档](https://docs.rspamd.com/tutorials/migration/) 并在实验集群先行验证。

## 6. 升级建议

1. 在实验集群部署 3.14.0，使用 rspamd\_proxy 镜像生产流量，观察新增符号命中与评分分布变化。
2. 逐项核对官方迁移指南中的破坏性变更（默认值、已移除选项），重点检查 `include_content_urls`、proxy 负载均衡、SSL worker 配置写法。
3. 启用 HTML 模糊哈希前，先用历史钓鱼样本回放验证误报率；启用 LLM 搜索上下文前，确认 Redis 与 LLM API 的容量预算。
4. 监控新增符号（如 HTML\_FUZZY、CTA 相关符号）在生产流量中的出现频率，按需调权。

### 相关主题

* [Rspamd 评分引擎架构深入：从规则集到机器学习管道](/kb/rspamd-architecture-scoring-engine.html)
* [Rspamd 与 SpamAssassin 评分机制对比与规则调优](/kb/rspamd-spamassassin-score-tuning.html)
* [Rspamd Console 与监控指标](/kb/rspamd-console-and-metrics.html)
* [邮件反垃圾得分系统深度解读](/kb/anti-spam-scoring-system-deep-dive.html)
* [AI 驱动的邮件安全检测](/kb/ai-powered-email-security.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rspamd-3140-new-features.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
