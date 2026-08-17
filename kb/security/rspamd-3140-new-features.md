---
title: "Rspamd 3.14.0 新特性详解：HTML 模糊哈希与 LLM 增强"
source: "https://ztpop.net/kb/rspamd-3140-new-features.html"
license: CC-BY 4.0
---

# Rspamd 3.14.0 新特性详解：HTML 模糊哈希与 LLM 增强

Rspamd 3.14.0 于 2025 年 11 月 10 日正式发布（Major Release），围绕四个方向更新：HTML 内容结构化检测、LLM 插件的上下文增强、Fuzzy 存储协议的 TCP 化，以及 URL 处理与 CTA 检测 API。本文基于 Rspamd 官方发布公告与文档整理。

## 1. HTML 模糊哈希：结构化相似度检测

3.14.0 引入 HTML Fuzzy Hashing（PR #5661、#5720），为模糊哈希体系增加了对 HTML 邮件正文的结构化相似度检测能力。传统模糊哈希以文本内容为单位计算相似度，而 HTML 模糊哈希针对 HTML 文档的结构特征（标签层级、属性模式、样式结构）生成哈希，用于识别「换了文案但结构相同」的钓鱼模板。

配套新增 per-rule `text_hashes` 开关（#5720），规则可配置仅对 HTML 内容启用文本哈希匹配，避免对纯文本邮件产生不必要的计算与误报。

```
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

3.14.0 为 Fuzzy 存储（fuzzy_storage）提供完整的 TCP 协议支持（PR #5669），连接管理与帧封装达到生产级水平。客户端可在配置中声明 TCP 端点，并在 UDP 不可用时自动切换到 TCP，显著提升大流量场景下模糊查询的可靠性。

```
fuzzy_check {
  rule "local" {
    servers = "tcp://127.0.0.1:11335";  # TCP 端点
  }
}
```

## 3. LLM 插件增强：Web 搜索上下文与 Redis 记忆

3.14.0 对 GPT/LLM 插件（自 3.9 引入）新增两项上下文能力：

- **Web 搜索上下文（search_context）**（PR #5732）：插件自动提取邮件 URL 中的域名，将相关 Web 搜索结果注入 LLM 提示词，使模型在评估钓鱼/欺诈邮件时获得域名信誉、品牌背景等外部证据。
- **Redis 记忆（context 块）**：启用后，插件按用户/域名维度在 Redis 中保存对话上下文摘要，使同一收件人（或同一发件域）的多封邮件形成连续评估，可识别跨邮件的社会工程攻击序列。

两项能力均默认关闭，需在配置中显式启用，同时依赖 Redis 可用性与 LLM API 配额。

```
gpt {
  enabled = true;
  type = "ollama";
  search_context {
    enabled = true;           # Web 搜索上下文（默认关闭）
  }
  context {
    enabled = true;           # Redis 用户/域名记忆（默认关闭）
  }
}
```

## 4. 高级 URL 处理：get_cta_urls() 与 URL 重写

3.14.0 在 Lua API 中新增 `task:get_cta_urls()`（PR #5732），用于检测邮件中的 CTA（Call-To-Action）链接——即正文中视觉突出、诱导点击的「立即领取」「验证账户」「重置密码」类按钮/链接。配套的 URL 重写基础设施（PR #5676）为 HTML 邮件中的 URL 提供统一改写管道，并内置基于哈希的去重保护（50,000 URL 上限），防止大型 HTML 邮件触发资源耗尽。

```
local function check_cta(task)
  local urls = task:get_cta_urls()
  if urls and #urls == 1 then
    -- 结合 URL 信誉查询做进一步判定
  end
end
```

## 5. 其他值得关注的变更

- 高级别名（aliases）与环路检测（#5655）
- WebUI 深色模式（#5725）
- Milter/集成类改进
- 升级注意：3.14 起部分默认行为调整可能影响既有部署，升级前务必阅读官方 Upgrading 文档并在实验集群先行验证

## 6. 升级建议

1. 在实验集群部署 3.14.0，使用 rspamd_proxy 镜像生产流量观察评分分布
2. 逐项核对官方迁移指南中的破坏性变更（include_content_urls 默认开启、proxy 负载均衡默认 token bucket、SSL worker 配置写法）
3. 启用 HTML 模糊哈希前用历史钓鱼样本回放验证误报率
4. 监控新增符号在生产流量中的出现频率，按需调权

## 权威参考来源

- Rspamd 官方 Changelog（rspamd.com）
- Rspamd 3.14.0 官方发布包与发布说明（SourceForge 官方镜像）
- Rspamd GPT Plugin 官方文档（docs.rspamd.com）
- Rspamd Upgrading 迁移指南（docs.rspamd.com）
- Rspamd Fuzzy Storage 使用教程（docs.rspamd.com）
- Rspamd 官方 GitHub 仓库（PR #5661/#5720/#5669/#5732/#5676/#5655/#5725）
