---
title: "AI 驱动的垃圾邮件检测：从贝叶斯到深度学习的演进"
source: "https://ztpop.net/kb/ai-powered-email-security.html"
license: CC-BY 4.0
---

# AI 驱动的垃圾邮件检测：从贝叶斯到深度学习的演进

## 概述

垃圾邮件检测从基于规则的静态匹配演进到多阶段 AI 流水线。第一层（统计层）使用朴素贝叶斯和逻辑回归对邮件文本中的词频特征做快速分类，每秒可处理数千封邮件。第二层（语义层）使用 Transformer 模型理解邮件的语义意图，识别社会工程学和鱼叉式钓鱼中精心构造的欺骗性文本。第三层（判白层）使用大语言模型作为误报裁判——对于被前两层标记为高风险但用户历史通信中存在的发件方，大模型分析邮件语义并判断是否属于误判。三层流水线在延迟和检测精度之间取得平衡。

## 贝叶斯分类器：统计基线

朴素贝叶斯分类器利用贝叶斯定理计算邮件属于垃圾邮件的概率。Rspamd 内置的 Bayesian 模块将邮件拆分为 Token（词元），统计各 Token 在 spam 和 ham 训练集中的出现频次，通过 Paul Graham 提出的组合概率公式得出邮件整体的垃圾概率。贝叶斯方法的优势在于计算极轻量（每封邮件毫秒级）、可解释性强（可回溯每个 Token 的贡献度），且支持增量在线学习——每天通过用户反馈自动更新词元概率表。

```
# Rspamd Bayesian 分类器管理
rspamc stat | grep -A10 "Statistic"

# 手动训练
rspamc learn_spam /path/to/spam.eml
rspamc learn_ham  /path/to/ham.eml

# 批量训练（从 Maildir 文件夹）
for eml in /var/vmail/example.com/user/.Junk/cur/*; do
  rspamc learn_spam "$eml"
done

# Bayesian 分类器 Redis 数据
redis-cli HLEN BAYES_SPAM
redis-cli HLEN BAYES_HAM
redis-cli HGET BAYES_SPAM "token_count"

# 查看特定 Token 的垃圾概率
redis-cli HGET BAYES_SPAM "viagra"
redis-cli HGET BAYES_HAM "viagra"
```

## 神经网络与 Transformer 语义检测

贝叶斯分类器对词袋模型的依赖使其无法检测词汇替换攻击——垃圾邮件发送者使用近义词、Unicode 同形字符或嵌入图片避开关键词匹配。CNN 和 RNN 模型可从邮件文本序列中提取局部和全局语义特征，对同义改写有较强鲁棒性。BERT 等 Transformer 模型通过注意力机制（Attention）理解单词在不同上下文中的含义，可有效检测伪装成商业沟通的社会工程学钓鱼邮件。Rspamd 的神经网络插件支持加载 ONNX 格式的预训练模型进行在线推理。

```
# Rspamd 神经网络插件配置
# /etc/rspamd/local.d/neural.conf
# enabled = true
# rules { NEURAL_SPAM { symbol = "NEURAL_SPAM"; min_score = 0.5; } }

# AI 过滤流水线架构（概念）
# L1: 贝叶斯 + 规则引擎（<1ms）→ score<4 → 放行
# L2: 神经网络模型（<5ms）  → score<6 → 放行
# L3: LLM 判白（<500ms，仅5%邮件触发）

# 监控各层过滤效果
rspamc stat | grep -E "Messages|Spam|Ham|Action"
```

## 大模型判白与误报抑制

垃圾邮件过滤面临的最大用户投诉不是漏报而是误报——将正常邮件标记为垃圾。大语言模型（LLM）在自然语言理解任务上表现出色，适合作误报判别的“第二意见”。当邮件被传统规则和模型评为高 spam 分但发件方在收件人历史通讯录中时，LLM 可对邮件全文内容做语义分析并给出“正常/垃圾”分类。实际部署中仅对“高不确定性”邮件触发 LLM 判白，以控制推理延迟和成本。

```
# Rspamd 多层评分配置
# /etc/rspamd/local.d/actions.conf
actions {
  reject = 15
  "add header" = 6
  "rewrite subject" = 4
  greylist = 3
}

# 计算精确率和召回率
echo "tp=$(grep -c 'spam.*correct' /tmp/validation.log)" > /tmp/precision.sh
echo "fp=$(grep -c 'spam.*wrong' /tmp/validation.log)" >> /tmp/precision.sh
echo "fn=$(grep -c 'ham.*spam' /tmp/validation.log)" >> /tmp/precision.sh
bash /tmp/precision.sh
python3 -c "
tp=$tp; fp=$fp; fn=$fn
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
print(f'Precision={precision:.4f} Recall={recall:.4f} F1={f1:.4f}')
"
```

## 踩坑与排错

贝叶斯分类器存在“中毒”风险：攻击者发送大量 ham 训练样本稀释特定 Token 的垃圾概率。应限制 learn\_spam/learn\_ham 的 API 访问并设置每日训练配额。神经网络模型的推理延迟在高吞吐场景下可能成为瓶颈——建议使用 ONNX Runtime 的 GPU 推理或将模型量化（INT8）减小体积。大模型判白可能引入幻觉——LLM 生成的分类理由可能看似合理但实际错误，建议使用结构化输出（JSON Schema）限制分类结果为二值标记。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/ai-powered-email-security.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
