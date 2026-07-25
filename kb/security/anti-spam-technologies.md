---
title: "邮件反垃圾技术全景分析 — Bayesian 统计过滤、DNSBL 实时黑名单、Greylisting 与深度学习演进"
source: "https://ztpop.net/kb/anti-spam-technologies.html"
license: CC-BY 4.0
---

# 邮件反垃圾技术全景分析 — Bayesian 统计过滤、DNSBL 实时黑名单、Greylisting 与深度学习演进

一封来路不明的邮件从进入 SMTP 会话到最终投递至用户收件箱，其间要穿越至少四道独立的检测环节。这四道防线从连接建立那一刻就开始运作，各自覆盖不同的攻击面，任何单一技术都不足以独立承担反垃圾任务。本文以技术演进为主线，逐一拆解每道防线的核心原理、关键参数和工程实践中需要留意的细节。

## 一、反垃圾邮件的四道防线

将反垃圾技术按介入时点和检测依据分层，可以得到一张清晰的纵深防御视图：

一、反垃圾邮件的四道防线

| 防线 | 介入阶段 | 判断依据 | 代表技术 |
| --- | --- | --- | --- |
| 连接层 | TCP 握手 → SMTP HELO | 发件 IP 信誉 | DNSBL、Greylisting、速率限制 |
| 协议认证层 | SMTP MAIL FROM → DATA | 发件身份真实性 | SPF、DKIM、DMARC、ARC |
| 内容层 | 邮件 DATA 接收后 | 正文/头部/附件特征 | Bayesian 分类、规则引擎、指纹哈希 |
| 行为层 | 投递后 / 离线分析 | 发件行为模式 | 声誉评分、异常检测、机器学习 |

这四层不是串行接力——连接层和协议认证层在 SMTP 事务早期就能拦截大部分批量垃圾邮件（据 Spamhaus 统计，仅 DNSBL 即可在连接阶段过滤约 35%~60% 的垃圾流量），大幅减少后端内容分析的压力。内容层承担细粒度判断，行为层则负责捕捉那些穿透前三层的攻击。

## 二、Bayesian 贝叶斯统计分类

### 2.1 Paul Graham 的原始方案

2002 年，Paul Graham 在文章
*A Plan for Spam*
中提出了将朴素贝叶斯分类器应用于垃圾邮件检测的方案。其核心思路简洁：将邮件拆解为 token 序列，为每个 token 计算其"垃圾倾向概率"，然后用组合概率判定整封邮件的类别。

计算过程分三步。第一步，从训练语料中统计每个 token
*w*
在 spam 和 ham 中出现的频率：

```
P(w|spam) = (bad(w) / total_bad)
P(w|ham)  = (good(w) / total_good)
```

第二步，计算 token 的独立垃圾概率（Graham 最初取双倍 ham 权重以压低误报）：

```
p(w) = P(w|spam) / (2 × P(w|ham) + P(w|spam))
```

第三步，选取概率最极端的 15 个 token（即 |p(w) − 0.5| 最大的 15 个），用它们计算联合概率：

```
P(spam) = (p1 × p2 × ... × p15) / (p1 × p2 × ... × p15 + (1−p1) × (1−p2) × ... × (1−p15))
```

Graham 声称该方案在自己收到的邮件上达到了 99.5% 的准确率。不过原始方案存在两个已知缺陷：一是极端概率（p(w) 趋近 0 或 1 的 token）会压倒整体判断；二是未对邮件头部/正文区域做区分加权。

### 2.2 Robinson 的几何均值变体

Gary Robinson 在 2003 年提出了关键改进，被 SpamAssassin 等主流实现采纳。Robinson 方案的核心变化有三点：

**（1）引入先验信念，平滑小样本偏差。**
不再直接用频率相除，而是用贝叶斯推断中的先验概率做加权：

```
f(w) = (s × x + n × p(w)) / (s + n)
```

其中
*s*
为先验强度（典型值 1.0），
*x*
为先验假设概率（典型值 0.5），
*n*
为该 token 出现的总次数。这意味着一个只出现过两三次的 token 不会产生极端倾向。

**（2）用几何均值替代 Graham 的朴素联合概率。**
不再仅取最极端的 15 个 token，而是对所有有效 token 计算：

```
P = 1 − ( (1−f1) × (1−f2) × ... × (1−fn) )^(1/n)
Q = 1 − ( f1 × f2 × ... × fn )^(1/n)
S = (1 + (P − Q) / (P + Q)) / 2
```

这一组公式依次计算了"非垃圾倾向"的几何均值 P、"垃圾倾向"的几何均值 Q，最后用费舍尔合并方法将两者压缩为一个 0~1 的最终得分。SpamAssassin 内部将 S 映射为 -1~+1 的规则加分，默认阈值 5.0 分为 spam。

**（3）按邮件区域分别对待。**
Subject 中的 token 权重高于正文（默认 ×1.5），而 HTML 标签中的 token 权重降低。这一设计使得"viagra 出现在标题"比"viagra 埋在一堆 HTML 垃圾里"产生更大的判定信号。

### 2.3 多语种分词与 Token 归一化

英文反垃圾的 tokenization 主要依赖空格分词和词干提取（Porter Stemmer），中、日、韩（CJK）语言的解析则需要额外的工程处理。常见做法包括：

* **N-gram 切分**
  ：对 CJK 文本按 bigram 或 trigram 滑动窗口生成伪 token，无需词典依赖。例如 "免费送货上门" → ["免费", "费送", "送货", "货上", "上门"]。
* **MIME 解码归一**
  ：将 Base64、Quoted-Printable 编码的正文还原为 UTF-8 后再分词，防止攻击者用编码混淆逃避匹配。
* **HTML 标签剥离**
  ：在 token 化之前先提取纯文本，且对隐藏在 display:none 中的文本做特殊标记（垃圾邮件常见手法：正文是正常文字，隐藏区域塞满色情关键词）。

sa-learn 工具负责训练贝叶斯分类器。管理员需要持续供给标注邮件来维持分类器的时效性：

```
# 训练 spam
sa-learn --spam /var/spool/training/spam/

# 训练 ham
sa-learn --ham /var/spool/training/ham/

# 查看分类器状态
sa-learn --dump magic
```

关键的运维参数是
`bayes_min_ham_num`
和
`bayes_min_spam_num`
（默认各 200 封），分类器在积累到这个数量之前不激活，避免小样本噪声。此外，spamd 的
`bayes_auto_expire`
配置可自动淘汰过期的旧 token，防止长期概念漂移。

## 三、DNSBL — DNS 实时黑名单

### 3.1 协议原理与查询机制

DNSBL（DNS-based Blackhole List）的本质是把 IP 信誉数据库包装成一个 DNS 区域。查询时，MTA 构造一个反向的 DNS A 记录查询，如果查询返回结果，说明该 IP 在列表中；如果返回 NXDOMAIN，说明不在。RFC 5782 对这一机制的结构和操作做了正式描述。

查询流程：

```
目标 IP: 203.0.113.45
正向查询: dig A 45.113.0.203.zen.spamhaus.org

# 不在列表（NXDOMAIN）：
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN

# 在列表（返回 127.0.0.x）：
45.113.0.203.zen.spamhaus.org. 900 IN A 127.0.0.4
```

DNSBL 的语义编码在返回的 A 记录的最后一个字节中。各知名列表的返回码含义：

3.1 协议原理与查询机制

| 返回码 | Spamhaus ZEN | SpamCop | Barracuda |
| --- | --- | --- | --- |
| 127.0.0.2 | SBL — 已知垃圾源 | — | — |
| 127.0.0.3 | CSS — 雪鞋/批量 | — | — |
| 127.0.0.4 | XBL — 僵尸/代理 | — | — |
| 127.0.0.5 | — | — | — |
| 127.0.0.9 | — | — | — |
| 127.0.0.10 | PBL — 策略不应直发 | — | — |
| 127.0.0.11 | PBL — 动态/拨号 | — | — |
| 127.0.0.2 | — | 已确认垃圾源 | — |
| 127.0.0.2 | — | — | 已确认垃圾源 |

实际部署中，不同返回码对应不同的处置策略：SBL（127.0.0.2）直接拒绝连接；PBL（127.0.0.10~11）仅加分不拒绝，因为该列表包含大量合法家用 IP，拒绝会误伤个人邮件。

### 3.2 URI DNSBL 与域名黑名单

除 IP 黑名单外，还有一类 URI DNSBL（如 SURBL），它不查发件 IP，而是提取邮件正文中所有链接的域名，查询这些域名是否在黑名单中。这能捕获那些从干净 IP 发出但引导收件人访问恶意网站的攻击。

查询 SURBL 域名黑名单：

```
# 邮件正文中有 http://phish-example.com
dig A phish-example.com.multi.surbl.org
# 返回 127.0.0.64 → 该域名在钓鱼列表中
```

### 3.3 Postfix 集成 DNSBL

在 Postfix 的 main.cf 中配置 DNSBL 只需几行：

```
# /etc/postfix/main.cf
smtpd_recipient_restrictions =
    reject_invalid_hostname,
    reject_non_fqdn_sender,
    reject_unknown_sender_domain,
    reject_rbl_client zen.spamhaus.org,
    reject_rbl_client bl.spamcop.net,
    reject_rhsbl_sender dbl.spamhaus.org,
    permit_mynetworks,
    permit_sasl_authenticated,
    permit

# 对 DNSBL 返回码做精确控制
# 仅当 Spamhaus 返回 127.0.0.2/3/4/9 时拒绝
smtpd_recipient_restrictions =
    reject_rbl_client zen.spamhaus.org=127.0.0.2,
    reject_rbl_client zen.spamhaus.org=127.0.0.3,
    reject_rbl_client zen.spamhaus.org=127.0.0.4,
    reject_rbl_client zen.spamhaus.org=127.0.0.9,
    ...
```

注意
`permit_mynetworks`
和
`permit_sasl_authenticated`
必须在 DNSBL 检查之后——Postfix 按顺序评估 restriction，先通过白名单的不会被后续规则拦截。

## 四、Greylisting — 灰名单

### 4.1 三重元组与 451 临时拒绝

Greylisting 的设计前提来自一个观察：垃圾邮件发送软件（尤其是僵尸网络节点）通常不做完整的 SMTP 重试——它们发送一次后若收到临时失败码（4xx），就会丢弃该收件人并继续轰炸下一个。而合规 MTA（Postfix、Exchange、Sendmail）会严格遵守 RFC 5321，在收到 4xx 临时拒绝后按退避策略重试。

RFC 6647 将 Greylisting 正式描述为一种 "temporarily degraded service to unknown email clients"。其核心数据结构是记录以下三元组（triplet）：

```
triplet = (sender_ip, sender_envelope_domain, recipient_address)
```

首次见到一个三元组时，MTA 返回 SMTP 451（或 450 临时拒绝），同时记录时间戳。合规发件服务器会在数分钟到数十分钟后重试，此时三元组已通过窗口期（典型配置 5~15 分钟），MTA 接受该连接并将三元组加入白名单，后续同一三元组的投递不再延迟。

典型的 greylisting 状态机：

4.1 三重元组与 451 临时拒绝

| 状态 | 条件 | 动作 |
| --- | --- | --- |
| 未知 | 三元组首次出现 | 返回 451，记录时间戳 |
| 等待中 | 距首次记录 < greylist\_delay | 继续返回 451 |
| 通过 | 距首次记录 ≥ greylist\_delay | 接受并白名单（TTL 30~60 天） |
| 白名单 | 三元组在已确认列表中 | 直接放行 |

### 4.2 邮件列表与多 IP 集群的兼容处理

Greylisting 最棘手的工程问题是邮件列表（mailing list）服务。大型邮件列表（如 Google Groups、Mailman）会从多个不同的 IP 地址重试，每次重试使用的发件服务器可能不同，这意味着 second-try 的 IP 与 first-try 不同，传统 triplet 匹配会失败。

常见的兼容策略：

* **域级放宽**
  ：在检测到 SPF 记录中声明了多 IP 网段后，将 triplet 从
  `(ip, domain, rcpt)`
  降级为
  `(/24_cidr, domain, rcpt)`
  。
* **自动白名单大型域名**
  ：对 gmail.com、outlook.com、yahoo.com 等大型 ESP 直接跳过 greylisting（维护一个硬编码的 ESP 豁免列表，约 200~500 个域）。
* **重试窗口内的 SPF 验证补充**
  ：在 451 等待期间，通过 SPF 检查来预先验证后续重试 IP 的合法性，减少误判。
* **带外 List-Unsubscribe 头检测**
  ：合规群发服务会在邮件头中包含 List-Unsubscribe 字段，可据此豁免 greylisting。

## 五、SpamAssassin 规则引擎体系

### 5.1 规则分类与评分叠加

SpamAssassin 的架构可以理解为一个规则评分累加器。每封邮件经过数百条规则的逐一检测，每条规则命中后累加一个权重分。总分超过 threshold（默认 5.0）即判定为 spam。规则按检测目标分为四类：

5.1 规则分类与评分叠加

| 规则类别 | 检测对象 | 典型规则示例 |
| --- | --- | --- |
| Header 规则 | 邮件头字段 | MISSING\_DATE（无 Date 头）、FORGED\_MUA\_OUTLOOK（伪造 Outlook 头）、RCVD\_IN\_DNSWL\_NONE（不在白名单） |
| Body 规则 | 邮件正文 | HTML\_MESSAGE（含 HTML）、DRUGS\_ERECTILE（伟哥关键词）、BODY\_8BITS（8bit 编码异常） |
| URI 规则 | 链接域名/IP | URIBL\_BLOCKED（SURBL 命中）、URIBL\_ABUSE\_SURBL、HTTP\_IN\_BODY（正文出现原始 IP URL） |
| Meta 规则 | 多条规则组合 | 组合命中 A AND B 再触发 C，避免单条规则的噪声 |

SpamAssassin 配置文件中规则的定义格式：

```
# /etc/spamassassin/local.cf

# 标准规则示例
header   SUBJ_ALL_CAPS     Subject =~ /^[A-Z\s]{20,}$/
describe SUBJ_ALL_CAPS     Subject is all capitals
score    SUBJ_ALL_CAPS     1.5

body     VIAGRA_OBFU       /v[i1]@[g9]r[a4]/i
describe VIAGRA_OBFU       Obfuscated viagra reference
score    VIAGRA_OBFU       2.5

# Meta 规则（组合触发）
meta     PHISHY_COMBO      (HTML_FORM_FRAUD && URIBL_PH_SURBL)
describe PHISHY_COMBO      Phishy HTML form + phishing domain
score    PHISHY_COMBO      3.0
```

### 5.2 分布式指纹：Pyzor / Razor / DCC

SpamAssassin 集成了三个独立的分布式指纹网络，它们共享同一设计思路：对邮件正文计算模糊哈希（fuzzy hash），将哈希值上传至中心服务器，若同一哈希已被其他用户标记为垃圾，则直接判定。三者各有侧重：

5.2 分布式指纹：Pyzor / Razor / DCC

| 系统 | 哈希算法 | 特点 | SpamAssassin 集成方式 |
| --- | --- | --- | --- |
| Pyzor | Nilsimsa 模糊哈希 | 抗小幅修改，Python 实现 | pyzor 客户端通过 stdin/stdout 通信 |
| Razor | SHA + 模糊摘要 | Vipul's Razor，最早的分发式方案 | razor2 客户端，需注册 |
| DCC | 模糊校验和（fuzzy checksum） | 注重计数统计（bulkness），非二元分类 | dccproc 客户端，侧重识别群发行为 |

DCC（Distributed Checksum Clearinghouse）与其他两者不同：它的目标不是标记"垃圾"，而是标记"群发"——一封邮件如果在 DCC 网络中命中高计数值（≥ 20 个 receipient 报告了相同校验和），即便内容是合法新闻推送也会报出，最终是否拦截由 SpamAssassin 的评分权重决定。

在 local.cf 中启用 Pyzor 和 Razor：

```
# /etc/spamassassin/local.cf
use_pyzor 1
pyzor_path /usr/bin/pyzor

use_razor2 1
razor_config /etc/razor/razor-agent.conf

use_dcc 1
dcc_home /var/lib/dcc
dcc_timeout 8
```

sa-learn 支持将人工标注后的邮件回传至 Pyzor/Razor 网络（报告模式），这意味着每个管理员不仅是消费者，也在为整个网络贡献情报。

## 六、SPF / DKIM / DMARC 作为反向信号

SPF、DKIM、DMARC 三项认证协议的设计初衷是防钓鱼和防伪造——它们回答"这封邮件是否真的来自它所声称的域"。但在反垃圾体系中，认证结果本身就是一个强信号：

* **认证通过不代表不是垃圾**
  （合法域也可以被攻陷用作垃圾转发）。
* **认证失败却是一个清晰的异常信号**
  ，可以直接加权。

SpamAssassin 中与认证相关的规则及默认分值：

六、SPF / DKIM / DMARC 作为反向信号

| 规则名 | 触发条件 | 默认分值 | 含义 |
| --- | --- | --- | --- |
| SPF\_FAIL | SPF 检查失败 | +0.5 | 发件 IP 不在 SPF 记录声明的范围内 |
| SPF\_HELO\_FAIL | HELO 域的 SPF 失败 | +0.5 | HELO 声称的域与发件 IP 不匹配 |
| SPF\_SOFTFAIL | SPF ~all 软失败 | +0.1 | 仅作为弱信号叠加 |
| DKIM\_SIGNED | 存在 DKIM 签名 | +0.1 | 仅表示签名存在 |
| DKIM\_VALID | DKIM 验证通过 | -0.1 | 弱正信号 |
| DKIM\_VALID\_AU | DKIM 签名域与 From 一致 | -0.1 | 更强的正信号 |
| DKIM\_INVALID | DKIM 签名损坏 | +0.5 | 签名验证失败 |
| DMARC\_FAIL | DMARC 策略 reject | +2.0 | 强负信号，接近直接拒绝 |

> **关键认知：**
> DMARC 失败的邮件几乎不可能是合法邮件。如果某个域的 DMARC 策略设为 p=reject，那么所有声称来自该域但无法通过 SPF 或 DKIM 认证的邮件都应该被拒绝——不需要内容分析。这是反垃圾体系中判决置信度最高的信号之一。

M3AAWG（Messaging, Malware and Mobile Anti-Abuse Working Group）在其 Sender Best Common Practices 中建议，所有发件域应至少配置 p=quarantine 的 DMARC 策略，而收件方应将 DMARC 结果直接注入内容过滤评分引擎而非隔离处理。

## 七、机器学习演进：从 TF-IDF 到 BERT

### 7.1 三阶段技术对比

反垃圾领域的机器学习实践经历了三个清晰的阶段，每个阶段都对应着特征表示能力的代际跃迁：

7.1 三阶段技术对比

| 阶段 | 特征表示 | 模型 | 时间 | 局限 |
| --- | --- | --- | --- | --- |
| 统计 ML | TF-IDF + 词袋 | 朴素贝叶斯、SVM、Logistic Regression | 2002~2015 | 忽略词序和上下文，易被分词混淆绕过 |
| 梯度提升 | 手工工程特征 + 嵌入向量 | LightGBM、XGBoost | 2015~2020 | 依赖人工特征设计，对新型攻击泛化有限 |
| 深度学习 | 预训练语言模型表示 | BERT、RoBERTa、DistilBERT | 2019~至今 | 推理延迟高（每封 50~200ms），部署成本大 |

### 7.2 TF-IDF + 朴素贝叶斯（统计阶段）

TF-IDF 向量 + 线性分类器是工业界最早成规模上线的一批反垃圾 ML 方案。TF-IDF 的计算分为两项：

```
TF(t, d)  = 词 t 在文档 d 中的出现次数 / 文档 d 的总词数
IDF(t)    = log(语料总文档数 / 包含词 t 的文档数)
TF-IDF(t) = TF(t, d) × IDF(t)
```

这一表示的优势在于计算量极低（O(n) 特征维度），可在大规模流量下以极小成本完成推理。但其致命缺陷是无法区分词序，因此 "buy now" 和 "now buy" 在 TF-IDF 向量中完全等价——而攻击者正是利用这种不敏感性，通过词序打乱、同义替换来逃避检测。

### 7.3 LightGBM + 多模态特征（梯度提升阶段）

梯度提升树的优势在于能自动学习特征之间的非线性交互。在反垃圾场景中，典型的输入特征空间包含数百个维度：

* **文本特征**
  ：TF-IDF 降维后的词向量（前 500 维）、Unicode 混淆度（Cyrillic 字符占比）、大小写混合度。
* **元数据特征**
  ：From 域年龄、IP 自治系统号（ASN）、时区偏移一致性。
* **行为特征**
  ：该 IP 过去 1h/24h 的发送量、收件人域分布熵值。
* **认证特征**
  ：SPF/DKIM/DMARC 结果编码为 one-hot 向量。

LightGBM 在 2017 年前后成为反垃圾系统的主流分类器，单封邮件推理延迟约 1~3ms，配合直方图算法，内存占用和训练速度都优于 XGBoost。局限在于特征工程仍然是人工驱动的——新攻击手法出现后，需要先从邮件样本中识别异常模式，再编码为特征，响应周期可能需要数天。

### 7.4 BERT + 迁移学习（深度学习阶段）

BERT 及其变体将反垃圾从特征工程推向了表示学习的范式。预训练模型无需手动设计特征即可捕获上下文语义，对混淆文本（Leet speak、同音替换、零宽字符插入）有天然的抗性。

典型部署架构：

```
SMTP 入站 → 轻量级过滤（DNSBL + Greylisting）→ 内容提取（剥离 MIME）
→ 文本截断至 512 token → 蒸馏 BERT 推理 → softmax(ham, spam)
→ 分值注入 SpamAssassin 评分管道
```

当前的主要工程障碍是延迟：即使经过知识蒸馏（DistilBERT），单封邮件的 GPU 推理仍需要 30~80ms，CPU 推理则需要 150~300ms。因此实际部署中通常采用级联架构——BERT 仅处理前三层无法判定且 Bayesian 置信度处于灰色区间（例如 2.5~4.5 分）的邮件，占总流量的 5%~15%。

## 八、BEC 与鱼叉攻击的检测挑战

商业电子邮件诈骗（BEC，Business Email Compromise）和鱼叉式钓鱼（Spear Phishing）是反垃圾体系中难度最高的攻击类型。它们的共同特征是没有传统垃圾的"招牌特征"：

* **无恶意 URL：**
  BEC 邮件通常不包含链接，只是一段精心编写的社交工程文字。
* **无垃圾关键词：**
  正文是正常的商务沟通语言——"请确认这笔款项是否已汇出""有没有时间开个电话会议"。
* **来自合法账号：**
  发件账号本身就是被攻陷的真实企业邮箱，SPF/DKIM/DMARC 全部通过。
* **小批量定向投放：**
  同一内容只发给三五个收件人，不会触发群发频率检测。

这类攻击面前，基于关键词和链接的传统反垃圾手段基本失效。当前工业界的应对思路集中在两条线：

**行为异常检测**
：即使正文内容正常，发件行为本身可能存在异常——凌晨 3 点的 CEO 邮件、来自从未出现过的地理位置的登录、短时间内大量读取旧邮件（攻击者搜集上下文信息以编造可信内容）。这些行为特征独立于邮件内容，可以被 SIEM 或 UEBA 系统捕获。NIST SP 800-45 第 4 节建议将邮件系统的访问日志与认证日志做关联分析。

**多模态检测**
：除文本特征外，引入邮件头时间线异常（该域历史上每天发件 50 封，今天突然 5000 封）、Reply-To 与 From 不一致、display name 伪装（CEO 全名 + 外部免费邮箱地址）等特征。这些信号在内容分析层面不可见，但在元数据层面有清晰的统计差异。

值得注意的是，纯文本 BEC 的检测仍然是一个开放性问题——没有公认的 ML 基准数据集（因为涉及真实企业内部通信，不可公开），各厂商的检测能力高度依赖自有的内部邮件语料。

## 九、误报控制：从负分规则到反馈闭环

垃圾邮件漏过（false negative）的影响是用户需要手动删除，属于可接受的代价。但合法邮件被误拦（false positive）意味着客户可能错过合同、工单或付款通知——这在企业邮件场景中是不可接受的。一个好的反垃圾体系必须把误报率控制在 0.01% 以下。

### 9.1 负分规则（Negative Scoring）

SpamAssassin 的评分体系中，有些规则带有负分值，命中后会抵消其他规则的正向加分：

```
# AWL（自动白名单）：对历史通信过的地址降低 spam 倾向
score AWL -3.0

# DKIM 验证通过的域与 From 一致
score DKIM_VALID_AU -0.1

# 邮件包含标准 List-Unsubscribe 头（合法群发标志）
score RCVD_IN_DNSWL_HI -2.0
```

AWL（Auto-Whitelist）是最关键的误报缓解机制：SpamAssassin 会自动记录每个发件地址在历史上收到的评分统计（均值、标准差），对历史上长期低分（即从该地址来的邮件总被判定为 ham）的发件人自动减分。

### 9.2 用户反馈闭环

用户反馈是误报控制中最基本也是最有效的机制。具体流程：

1. 用户在邮件客户端将误拦邮件移入收件箱，或将漏过的垃圾邮件标记为垃圾。
2. 邮件系统通过 IMAP 移动通知（或定时轮询垃圾箱）捕获用户的分类动作。
3. 被重新分类的邮件自动通过
   `sa-learn`
   注入训练语料。
4. 管理员定期审查训练集中矛盾标记的邮件（同一封同时被标记为 ham 和 spam），人工仲裁以减少标签噪声。

自动化训练的 cron 脚本示例：

```
#!/bin/bash
# 每晚 2:00 从用户反馈目录学习
sa-learn --spam --dir /var/spool/feedback/spam --showdots
sa-learn --ham  --dir /var/spool/feedback/ham  --showdots
sa-learn --sync
# 定期淘汰 120 天未出现的 token
sa-learn --force-expire
```

另一个重要的运维参数是
`bayes_auto_learn`
：当此选项开启时，spamd 会自动将评分极高（≥ 12 分）或极低（≤ 0.1 分）的邮件纳入训练，无需人工标注。这个"自动课程"在分类器早期训练阶段有效，但长期运行后建议关闭以避免反馈循环——分类器可能开始强化自身的错误倾向。

## 十、总结

反垃圾邮件是一场没有终点的博弈。攻击者不断调整策略——从纯文本批量群发到僵尸网络 IP 轮换、从图片垃圾到 BEC 社交工程——而防御方的技术栈也在同步演进。理解每道防线的工作机制和边界条件，比追逐某一种"新技术"更重要。

以下是在实际部署中经过验证的有效组合方案：

1. **连接层**
   ：Postfix 集成 DNSBL（Spamhaus ZEN + SpamCop），配置 Greylisting 延迟窗口 10 分钟，对认证用户和已知邮件列表域豁免。
2. **协议认证层**
   ：DMARC 失败的邮件直接拒绝或标记 +3 分，SPF softfail 仅作为弱信号叠加。
3. **内容层**
   ：SpamAssassin 开启 Bayesian + Pyzor + Razor，持续用 sa-learn 注入用户反馈。Robinson 几何均值分类器的误报率在充足训练后可达 0.01% 以下。
4. **行为层**
   ：对 BEC 类无载荷攻击，依赖发件行为异常检测和元数据特征，而非内容关键词。

**参考来源：**
  
[1] RFC 5782 — DNS Blacklists and Whitelists (J. Levine, IRTF, 2010)
  
[2] RFC 6647 — Email Greylisting: An Applicability Statement for SMTP (M. Kucherawy, D. Crocker, IETF, 2012)
  
[3] NIST SP 800-45 Version 2 — Guidelines on Electronic Mail Security (NIST, 2007)
  
[4] M3AAWG Sender Best Common Practices (M3AAWG, 2024)
  
[5] Apache SpamAssassin Project Documentation — Writing Rules, Bayes Frequently Asked Questions
  
[6] Paul Graham, "A Plan for Spam" (2002)
  
[7] Gary Robinson, "A Statistical Approach to the Spam Problem" (Linux Journal, 2003)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/anti-spam-technologies.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
