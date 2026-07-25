---
title: "邮件反垃圾得分系统深度解读：SpamAssassin vs Rspamd 评分、阈值决策与误报调优"
source: "https://ztpop.net/kb/anti-spam-scoring-system-deep-dive.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# 邮件反垃圾得分系统深度解读：SpamAssassin vs Rspamd 评分、阈值决策与误报调优

## 1. 引言

反垃圾邮件系统的核心是「评分引擎」——通过对邮件多方面特征的加权计算，得出一个量化分值，用于判断邮件是否为垃圾。SpamAssassin 自 2002 年以来一直是开源邮件安全领域的事实标准，其规则集超过 3,000 条，采用 Perl 正则加元数据的「规则树」模型[1]。Rspamd 是 2013 年后兴起的新一代评分引擎，采用 C 核 + Lua 扩展的事件驱动架构，在吞吐量和扩展性上做出了重大突破。

然而，无论是哪套引擎，「得分阈值」的设置、自定义规则的编写、以及误报（false positive）的调优，始终是运维中最大痛点。5.0、6.0、8.0、15.0 这些数字代表什么意义？如何根据自身业务选择？如何在不降低检出率的前提下减少误报？本文将从评分系统的本质出发，给出系统化的方法论。

## 2. SpamAssassin 评分规则体系

### 2.1 架构概要

SpamAssassin 的评分体系是「规则集 + 贝叶斯 + DNSBL」的三层模型，其中规则集分为以下六类：

| 规则类 | 命名前缀 | 示例规则 | 默认评分 |
| --- | --- | --- | --- |
| 头部规则 | HEAD\_ | HEAD\_FROM\_DIFFERENT\_DOMAINS | 0.5~2.0 |
| 正文规则 | BODY\_ | BODY\_LINKS\_IN\_BL | 0.5~3.0 |
| 元数据规则 | META\_ | META\_CLICKBAIT | 0.5~4.0 |
| URI 规则 | URI\_ | URI\_OBFU\_WEBMAIL | 0.5~1.5 |
| 原始体规则 | RAW\_ | RAW\_BASE64\_ENC\_ATTACH | 0.5~2.0 |
| 插件规则 | 插件自定义 | DKIM\_VALID（使用 DKIM 插件） | −0.1（负分表示降低垃圾评分） |

默认配置下，超过 5.0 分的邮件被标记为垃圾（Spam），超过 15.0 分被直接拒绝（block）[1]。但这些阈值在不同环境下差别很大——对一家电子商务公司而言，5.0 可能意味着频繁误杀营销邮件。

### 2.2 SpamAssassin 关键评分文件

```
# /etc/mail/spamassassin/local.cf
# 基础评分阈值
required_score           5.0       # 默认，标记为垃圾邮件的边界线
rewrite_header Subject   [SPAM]

# 贝叶斯启用
use_bayes               1
bayes_auto_learn        1
bayes_auto_learn_threshold_spam     12.0  # 得分>12自动学习为垃圾
bayes_auto_learn_threshold_nonspam  0.1   # 得分<0.1自动学习为非垃圾

# DNSBL 集成
use_dnsbl               1
dns_available           yes

# 自定义评分覆盖（以降低误报为例）
score HEAD_FROM_DIFFERENT_DOMAINS  0.001   # 大幅降低此规则得分
score SUBJ_ILLEGAL_CHARS           0.001   # 许多合法邮件含特殊字符

# 白名单
whitelist_from   *@partner-company.com
whitelist_from   *@trusted-mailing-list.org

# 黑名单覆盖
blacklist_from   *@known-bad-sender.org
```

### 2.3 SpamAssassin 的评分计算公式

`总评分 = 规则集累计评分 + 贝叶斯评分 + DNSBL 评分 + URIBL 评分 + 网络测试评分`

各组件在默认配置下权重并不是线性的。贝叶斯评分（`BAYES_99` 到 `BAYES_00`）是一个系统性修正，最高可达 +3.5 分（BAYES\_99），最低 −3.5 分（BAYES\_00）。这意味着即便所有规则均未触发，纯贝叶斯模型也能决定一封邮件的生死[1]。

## 3. Rspamd 评分引擎架构

### 3.1 与 SpamAssassin 的架构差异

| 维度 | SpamAssassin | Rspamd |
| --- | --- | --- |
| 核心语言 | Perl | C (核心) + Lua (扩展) |
| 规则模型 | 线性规则集，串行匹配 | 符号(Symbols) + 复合指标(Composites) + 统计分类器 |
| 网络查询 | 串行，单次 DNSBL 阻塞 | 异步并行，所有查询在事件循环中同时发起 |
| 贝叶斯 | 使用 BAYES 规则，基于 Graham-Click 算法 | 集成贝叶斯分类器 + 互信息特征提取 |
| 神经网络 | 不支持原生 | 支持基于模糊哈希的神经网络分类器 |
| 评分系统 | 加减分制（默认 required\_score 5.0） | 复合符号评估，最终得分归一化到 0~1 或自定义范围 |
| 多事件 | 每封邮件单次遍历 | 管道式多阶段处理（pre-filter → filter → post-filter） |
| 配置热加载 | 需重载 spamd | 支持 umlogged 模式下自动检测更改 |

### 3.2 Rspamd 得分计算逻辑

Rspamd 的评分不直接是加法求和，而是使用「符号权重 + 复合条件」的混合模式：

* 每个符号（Symbol）有自己的权重（可为负），匹配时向最终得分贡献该权值
* 复合指标（Composite）允许将多个符号组合为「且/或/非」逻辑，赋予更高权重
* 统计分类器（Bayes / Neural）的输出值会与符号评分融合，进行 Sigmoid 归一化

```
# Rspamd 符号权重配置示例 (/etc/rspamd/rspamd.conf 或 local.d/ 目录)
# 默认符号定义（metrics 区块）
symbols {
    "R_DKIM_ALLOW" {
        weight = -0.1;        # DKIM 验证通过，降低垃圾评分
        description = "DKIM verified";
    }
    "R_DKIM_REJECT" {
        weight = 3.0;         # DKIM 验证失败，显著增加垃圾评分
        description = "DKIM rejected";
    }
    "MIME_GOOD" {
        weight = -0.25;       # 良好的 MIME 结构加分
    }
    "RBL_SPAMHAUS_BLOCK" {
        weight = 5.0;         # 出现在 Spamhaus 区块列表中，高权重
        groups = ["rbl"];
    }
}

# 复合指标定义（composites 区块）
composites {
    "COMPOSITE_DMARC_FAIL" {
        expression = "R_DMARC_DNSFAIL && R_DKIM_REJECT && R_SPF_FAIL";
        weight = 8.0;
        description = "DMARC + DKIM + SPF 全失败";
    }
}

# 动作阈值定义
actions {
    reject = 15.0;            # 直接拒绝
    add_header = 8.0;         # 添加垃圾标记头
    greylist = 5.0;           # 灰名单
    subject = 6.0;            # 修改主题前缀
    rewrite_subject = 6.0;    # 重写主题
}
```

## 4. 得分阈值决策模型

得分阈值的选择需要在「召回率（检出率）」和「精确率（误报率）」之间寻找平衡。以下对 5.0、6.0、8.0、15.0 四个常见阈值进行分析：

### 4.1 阈值 5.0（宽松默认）

SpamAssassin 的出厂默认阈值。在此配置下，一封仅包含几个弱匹配规则的邮件（如一封来自中国 IP 的英文促销邮件）就容易被标记。适合对误报容忍度极低、且用户自主分类能力强的环境。

* 误报率（FP Rate）：约 1~3%（取决于业务类型，营销邮件越多误报越高）
* 检出率（Recall）：约 85~92%
* 适合场景：个人邮箱、小型企业（日邮件量 < 5000）

### 4.2 阈值 6.0（折中推荐）

略微收紧下限但不至于过度杀伤。在此阈值下，单一 DNSBL 命中 + 无 DKIM 的邮件可能不达标（5+0=5 < 6），需要更综合的证据。这是大多数中型企业的推荐起点。

* 误报率：约 0.5~1.5%
* 检出率：约 80~88%
* 适合场景：中型企业、日流量 5000~100000 封

### 4.3 阈值 8.0（高门槛）

要求多维度负面证据累积才能判定为垃圾。适用于垃圾邮件比例高、且用户对少量误报可接受的环境。

* 误报率：约 0.1~0.5%
* 检出率：约 70~80%
* 适合场景：大型企业、邮件安全服务商、日流量 > 100000

### 4.4 阈值 15.0（极严格）

该阈值意味着邮件必须有明确的、多维度的高确信度负面证据才被拒绝。通常对应 Rspamd 的 `reject` 动作阈值。适用于需要极低误报率的场景。

* 误报率：< 0.05%
* 检出率：约 50~65%
* 适合场景：医疗、金融、政府等合规严苛场景，配合后续人工审核

**重要原则**：阈值永远是业务语境相关的。一家以邮件下单为主的电商不能使用 5.0 阈值——客户下单确认邮件会被误杀。一个业务邮件极少的教育机构可以将阈值降到 3.0 以提高检出率。

### 4.5 动态阈值策略

更先进的方案是根据时间或特征动态切换阈值。例如：

```
# 基于时间段动态切换（需 cron + 重载）
# 工作日 9:00~18:00（业务高峰）使用宽松阈值
# 其余时间使用严格阈值
0 6 * * * sed -i 's/required_score.*/required_score 6.0/' /etc/mail/spamassassin/local.cf
0 10 * * * sed -i 's/required_score.*/required_score 4.0/' /etc/mail/spamassassin/local.cf
```

Rspamd 支持基于 `ratelimit` 和 `reputation` 插件的动态阈值——发件方 IP 若积累了正面声誉（如持续发送合法邮件 30 天以上），其邮件可使用更低阈值。这比 SpamAssassin 的静态阈值更精细[2]。

## 5. 自定义规则编写

### 5.1 SpamAssassin 规则

```
# 自定义头部规则：检测特别长的 Subject 行
# /etc/mail/spamassassin/30_my_custom.cf
header   LONG_SUBJECT    Subject =~ /^.{200,}$/
describe LONG_SUBJECT    Subject line exceeds 200 characters
score    LONG_SUBJECT    0.5

# 自定义正文规则：检测特定垃圾词组
body     PHARMA_PILLS    /(viagra|cialis|levitra|weight\s*loss)/i
describe PHARMA_PILLS    Contains pharmaceutical keywords
score    PHARMA_PILLS    1.5

# 元规则：组合两个条件同时命中才加分
meta     META_SUSPICIOUS (LONG_SUBJECT && PHARMA_PILLS)
score    META_SUSPICIOUS 3.0

# 使用 eval 调用 Perl 函数
eval     SENDER_IN_RU_RBL check_rbl('sender', 'rbl.example.com')
score    SENDER_IN_RU_RBL 2.0
```

自定义规则注意事项：

* 规则文件编号（如 30\_）决定了加载顺序，建议使用 20\_~50\_ 之间的编号
* 正则表达式应加 `i` 标记忽略大小写，但注意在非 ASCII 文本上可能产生误报
* 新规则部署后需要观察至少一周，通过 `sa-learn --dump` 统计触发率
* 避免过于宽泛的正则，如 `/free/i` 会命中无数字免费通知

### 5.2 Rspamd 规则（Lua）

```
-- /etc/rspamd/local.d/custom.lua
-- Rspamd 自定义符号定义

-- 检查发件人域是否包含数字（常见于随机生成的垃圾邮件域）
rspamd_config.SENDER_NUMERIC_DOMAIN = {
    type = 'normal',
    score = 2.0,
    group = 'custom',
    callback = function(task)
        local from = task:get_from()
        if from then
            local domain = from[1].domain or ''
            if domain:match('%d') then
                return true, string.format('domain contains digits: %s', domain)
            end
        end
        return false
    end
}

-- 复合符号：综合判定高欺诈风险邮件
rspamd_config.COMPOSITE_HIGH_FRAUD = {
    type = 'composite',
    score = 8.0,
    group = 'custom',
    expression = "SENDER_NUMERIC_DOMAIN && R_DKIM_REJECT && R_SPF_FAIL"
}

-- 白名单符号：自定义白名单域
rspamd_config.CUSTOM_WHITELIST = {
    type = 'normal',
    score = -5.0,   -- 大负值确保不被标记
    group = 'custom',
    callback = function(task)
        local from = task:get_from()
        if from then
            local domain = from[1].domain or ''
            local whitelist = {'trusted.com', 'safe.org', 'partner.net'}
            for _, wl in ipairs(whitelist) do
                if domain == wl then
                    return true
                end
            end
        end
        return false
    end
}
```

Rspamd 自定义规则使用 Lua 回调，比 SpamAssassin 的正则+元规则更灵活，但学习曲线也更陡。注意所有自定义 Lua 文件必须放置于 `/etc/rspamd/local.d/` 或 `/etc/rspamd/override.d/` 目录，Rspamd 会自动加载。

## 6. 误报分析与调优方法论

### 6.1 误报发现的系统化方法

1. **设置误报报告通道**：为用户提供一键「这不是垃圾」按钮（如 webmail 客户端），并记录原邮件完整头部和评分详情
2. **定期抽样审查**：每天从被标记为垃圾的邮件中随机抽查 100~200 封，计算假阳性比例
3. **评分分解**：对每封误报邮件，列出其得分最高的前 5 条规则——通常是少数几条规则导致了标记

### 6.2 SpamAssassin 误报调优命令

```
# 查看具体邮件的评分详情
spamassassin -D < /var/mail/false-positive.eml 2>&1 | grep -E '^ *-?[0-9]+\.[0-9]'

# 训练贝叶斯
sa-learn --ham --msg /var/mail/false-positive.eml     # 标记为正常
sa-learn --spam --msg /var/mail/sample-spam.eml        # 标记为垃圾

# 查看贝叶斯数据库状态
sa-learn --dump magic

# 分析邮件的规则匹配
sa-awl --analyze /var/log/mail.log | sort -k2 -rn | head -20
```

### 6.3 白名单/黑名单权重策略

白名单和黑名单的权重选择直接决定了效果：

| 策略 | 权重 | 效果 | 风险 |
| --- | --- | --- | --- |
| 强白名单 | −100 | 绝对通过，不经过任何垃圾检查 | 发件人账号被劫持后，攻击者可使用白名单直接投递垃圾 |
| 弱白名单 | −5.0 | 显著降低垃圾评分，但不完全绕过检查 | 依赖其他规则兜底，安全与便利的平衡 |
| 强黑名单 | +100 | 绝对拒绝，不经过任何检查 | 合法邮件发送方 IP 变化时可能误杀 |
| 弱黑名单 | +5.0 | 显著增加垃圾评分，但允许通过其他规则翻转 | 被攻击者利用放大评分，对其他系统规则造成扰动 |

**推荐**：对已知合作伙伴、订阅邮件列表使用弱白名单（−5.0），对确凿的垃圾发件方使用强黑名单（+100）。定期（每季度）审查白名单列表，移除不再活动的发件域。

### 6.4 基于邮局反馈环的数据闭环

更高级的调优策略是将用户的「标记为垃圾/标记为非垃圾」行为通过 ARF（Abuse Reporting Format）回灌到评分引擎的贝叶斯训练集中[3]：

```
#!/bin/bash
# spam-train-from-fbl.sh — 利用用户报告回灌训练
# 从用户报告数据库中提取已标记邮件
mysql -u root -p maildb -e "
  SELECT email_body FROM fbl_reports
  WHERE action='ham' AND created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
" | while read body; do
  echo "$body" | sa-learn --ham 2>&1
done

mysql -u root -p maildb -e "
  SELECT email_body FROM fbl_reports
  WHERE action='spam' AND created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
" | while read body; do
  echo "$body" | sa-learn --spam 2>&1
done
```

## 7. 引擎选型决策树

```
是否需要同步处理 < 10ms/封？
├─ 是 → Rspamd（事件驱动优势显著）
└─ 否 → 继续评估

现有基础设施是否是 Perl？
├─ 是 → SpamAssassin（生态成熟，运维团队熟悉）
└─ 否 → 继续评估

是否需要深度学习/模糊哈希分类？
├─ 是 → Rspamd（原生神经网络支持）
└─ 否 → 继续评估

规则的定制频率？
├─ 频繁 → Rspamd（Lua 热加载，无需重启）
└─ 低频 → SpamAssassin（vi 改 .cf 文件即可）
```

实际上许多大型部署会同时使用两个引擎：SpamAssassin 担任第一道防线（配置在 MTA 的前置过滤中），Rspamd 担任第二道引擎（在 Milter 层进行深度分析）。两个引擎的评分进行加权融合，取加权均值作为最终决策——这种方法能有效抵消单个引擎的盲区。

## 参考文献

1. SpamAssassin Configuration Manual — The Apache SpamAssassin Project. Section 3 (Score Configuration), Section 8 (Bayes System), Section 9 (Network Tests). <https://spamassassin.apache.org/full/3.4.x/doc/Mail_SpamAssassin_Conf.html>
2. Rspamd Documentation — Rspamd Project. Metrics and Symbols Configuration, Composites, Actions Thresholds. <https://rspamd.com/doc/configuration/metrics.html>
3. RFC 5965 — An Extensible Format for Email Feedback Reports. IETF, August 2010. Section 2 (Feedback Report Format), Section 3 (Required Fields).
4. RFC 7208 — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1. IETF, April 2014. Section 3 (SPF Record Format).
5. NIST SP 800-177 Rev.1 — Email Security Guidelines. NIST, February 2021. Section 4 (Email Authentication Standards), Section 5.2 (Spam and Phishing Filtering).
6. Graham-Click B — A Plan for Spam. Paul Graham. 2002. Bayesian Spam Filtering Algorithm Foundation.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/anti-spam-scoring-system-deep-dive.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
