---
title: "Rspamd评分引擎架构深入：从规则集到机器学习管道"
source: "https://ztpop.net/kb/rspamd-architecture-scoring-engine.html"
license: CC-BY 4.0
---

# Rspamd评分引擎架构深入：从规则集到机器学习管道

## 1. 引言

Rspamd采用事件驱动的多阶段处理架构，将邮件的反垃圾邮件检测分解为符号(Symbols)评分、规则匹配、统计分类和机器学习四个层次。与传统反垃圾邮件引擎不同，Rspamd通过C语言编写的高性能事件处理内核与Lua语言编写的可扩展插件层，实现了毫秒级的处理延迟。

Rspamd的架构设计源于对SpamAssassin在生产环境中暴露出的性能瓶颈的反思。SpamAssassin采用单次遍历的规则集模型，每封邮件需要串行执行数十到数百条正则表达式规则，DNS查询也是逐个发起，在高并发场景下延迟急剧上升。Rspamd则采用异步事件循环(基于libevent)将所有网络查询批量并行发起，DNSBL、SURBL、DKIM验证和Bayes分类在同一事件循环中完成，处理延迟通常控制在10毫秒以内。

本文从Symbols符号体系出发，逐步拆解复合规则(Composite)、统计分类器管道、模糊哈希和实时学习机制，最后讨论Rspamd与SpamAssassin的迁移策略及Web界面运维。

## 2. Symbols评分体系

### 2.1 Symbol与Metric的映射关系

在Rspamd中，Symbol是一个具名的检测结果单元，每个Symbol通过Lua插件或C模块产生。Metric是Symbol的加权聚合容器：每个Metric定义了一组Symbol及其对应权重(weight)，最终计算出一个浮点数评分。系统默认提供`default`指标，管理员可根据场景在`local.d/metrics.conf`中自定义多个Metric，例如分别为入站、出站和内网邮件配置独立的评分阈值。

```
# /etc/rspamd/local.d/metrics.conf
symbol "BAYES_HAM" {
  weight = -2.0;
  description = "Message classified as ham by Bayes";
}
symbol "RBL_SPAMHAUS" {
  weight = 3.5;
  description = "Sender IP listed in Spamhaus Zen";
}
actions {
  reject = 15;
  "add header" = 6;
  "rewrite subject" = 4;
  greylist = 2;
}
```

当多个Symbol同时触发时，评分累加。若某Symbol的`one_shot`属性为true，则该Symbol在单个Metric中仅触发一次，即使多个规则产生相同符号。这一机制在防止重复计分的同时保持了规则的表达能力。

### 2.2 内置Symbol类型

2.2 内置Symbol类型

| 类型 | 产生方式 | 示例 |
| --- | --- | --- |
| 预过滤 | pre-filters插件 | `GREYLIST`, `MIME_BAD_EXTENSION` |
| 网络查询 | DNSBL/SURBL模块 | `RBL_SPAMHAUS`, `URIBL_MULTI` |
| 认证结果 | DKIM/SPF/DMARC模块 | `R_DKIM_ALLOW`, `DMARC_POLICY_REJECT` |
| 统计推断 | Bayes/Fann/神经网络 | `BAYES_SPAM`, `NEURAL_SPAM` |
| 内容特征 | Regexp/Multimap模块 | `SUBJ_ALL_CAPS`, `FROM_EXCESS_BASE64` |

### 2.3 Lua插件开发模型

Rspamd的插件系统基于LuaJIT，提供完整的API用于访问邮件的各个属性层。一个典型的自定义插件在初始化阶段注册symbol和回调函数，在处理阶段通过task对象获取邮件信息，最终向控制器返回symbol结果。

```
-- /etc/rspamd/lua/custom/check_subject_length.lua
local rspamd_logger = require "rspamd_logger"
local rspamd_regexp = require "rspamd_regexp"

local symbol_name = "SUBJ_TOO_LONG"
local symbol_weight = 0.5

local function callback(task)
  local subject = task:get_header("Subject")
  if not subject then return end

  -- 检查主题长度和编码特征
  local raw_len = #subject
  local decoded = task:get_header_decoded("Subject")

  if raw_len > 200 then
    task:insert_result(symbol_name, symbol_weight,
      string.format("subject length %d chars", raw_len))
    rspamd_logger.infox(task, "long subject detected: %d", raw_len)
  end
end

local id = rspamd_config:register_symbol(
  symbol_name, 1.0, callback
)
rspamd_config:set_metric_symbol("default", symbol_name, symbol_weight)
rspamd_config:set_symbol_group(symbol_name, "content")
rspamd_config:set_symbol_type(id, "postfilter")
```

## 3. Composite复合规则引擎

Composite是Rspamd特有的一种元规则机制，允许将多个底层Symbol的触发结果组合为单一高阶判断。这与SpamAssassin中的meta规则功能类似，但语法更为灵活，表达能力等价于完整的布尔逻辑表达式。Composite采用“策略表达式”(policy expression)语法定义触发条件。

```
# /etc/rspamd/local.d/composites.conf
composite "COMPOSITE_FREEMAIL_FORGERY" {
  expression = "(-g+:policies) & (FROM_HAS_DN & !IS_LOCAL_DOMAIN)";
  policy = "remove_weight";
  score = 4.0;
  description = "Freemail sender claims non-freemail domain";
  group = "forgery";
}
```

上述规则的含义：如果发件人域名通过了策略检查(`-g+:policies`)且Having `From`头但并非本地域，则施加4.0的额外权重并从原符号中移除基础权重。Composite支持的策略操作包括三种模式：`remove_weight`在命中时替换所有子符号的基础权重为Composite定义的权重值，避免重复计分；`leave`保留子符号的原有权重在此基础上叠加Composite的评分；`default`仅当没有任何子符号触发时才使用Composite定义的权重。

策略表达式的语法支持逻辑与(`&`)、逻辑或(`||`)、逻辑非(`!`)以及组引用(`g:group_name`)，前缀加号(+)表示要求某symbol必须触发，减号(-)表示要求某symbol不触发。

## 4. 统计分类器管道

### 4.1 朴素贝叶斯分类器

Rspamd的贝叶斯实现基于双词元(token)的最小哈希(minhash)算法，词元存储于Redis或SQLite后端。与SpamAssassin的CSV风格词元存储不同，Rspamd使用OSB(Optimized Statistically Based)词元化算法，通过n-gram分解将邮件正文和头域转化为固定长度的统计特征向量，有效降低了维度灾难的影响。

```
# /etc/rspamd/local.d/classifier-bayes.conf
classify_headers = [
  "Subject", "From", "To", "List-Id", "Message-ID"
];
min_tokens = 11;
min_learns = 200;
backend = "redis";
tokenizer {
  name = "osb";
  max_tokens = 400000;
  min_ngram = 1;
  max_ngram = 2;
}
```

学习命令通过`rspamc`完成，学习过程为增量式，无需重启服务。生产环境中通常结合自动学习(Autolearn)阈值实现无人值守的持续训练：当邮件评分低于-1.0时自动学习为正常邮件(ham)，高于10.0时自动学习为垃圾邮件(spam)，中间的邮件不参与学习以避免污染训练集。

```
$ rspamc -h 127.0.0.1:11334 -P password learn_spam /path/to/spam.eml
Results for file: /path/to/spam.eml
  success = true;
  scan_time = 0.042;
  score = 12.34;
  action = "reject";
$ rspamc -h 127.0.0.1:11334 -P password learn_ham /path/to/ham.eml
```

### 4.2 神经网络(FANN)分类器

Rspamd还集成了基于FANN(Fast Artificial Neural Network)库的前馈神经网络作为贝叶斯分类器的补充分类器。其输入向量从邮件的多模态特征中生成：头域结构特征被编码为浮点向量，主题编码检测(如Base64多重编码)、MIME结构复杂度、正文token统计特征等共同构成输入层。网络的隐藏层通过反向传播训练，输出层给出垃圾邮件的概率估计。

```
# /etc/rspamd/local.d/neural.conf
rules {
  "NEURAL_SPAM_LONG" {
    train {
      max_training_cycles = 100;
      desired_error = 0.001;
    }
    symbols {
      "NEURAL_SPAM" {
        threshold = 0.85;
        symbol = "NEURAL_SPAM";
      }
    }
  }
}
```

神经网络分类器的优点在于它可以捕捉特征之间的非线性关系，例如“发件人域名为免费邮箱 + 正文包含大量URL”这个组合特征的垃圾邮件概率远大于两个特征独立概率的线性组合。但代价是训练需要更多的样本量和计算资源，且模型的可解释性不如贝叶斯分类器。

### 4.3 Fuzzy Hashing模糊哈希

Rspamd的Fuzzy Check模块通过`fuzzy_storage` Worker接收多个节点的哈希提交。其核心原理是将邮件MIME结构拆分为多个“节”(part)，对每节计算多个哈希值(包含shingle哈希以便容忍小幅修改)，通过UDP协议以二进制协议同步到中心存储。

```
# /etc/rspamd/local.d/worker-fuzzy.inc
bind_socket = "*:11335";
hash_file = "${DBDIR}/fuzzy.db";
expires = 90d;
sync = true;
count = 3;
min_bytes = 400;
allow_update = ["192.168.1.0/24"];
```

模糊哈希在对抗“多态垃圾邮件”(polymorphic spam)时效果显著：垃圾邮件发送者通过随机化正文段落、修改空格和标点符号来逃避传统哈希检测，但模糊哈希的shingle算法可以识别出两封邮件在本质结构上的相似性，即使表面内容有30%以上的差异。

## 5. DNSBL/SURBL与认证模块联动

Rspamd的DNSBL查询通过异步事件循环批量发起，这是其相对于SpamAssassin最大的性能优势之一。在配置文件`rbl.conf`中可定义多级DNSBL规则，每个返回码可映射到不同的分值：

```
# /etc/rspamd/local.d/rbl.conf
rbls {
  spamhaus {
    rbl = "zen.spamhaus.org";
    return_codes {
      "127.0.0.2" = 6.0;  # SBL
      "127.0.0.3" = 3.5;  # CSS
      "127.0.0.4" = 6.0;  # XBL
      "127.0.0.10" = 2.5; # PBL
    }
  }
  surbl {
    rbl = "multi.surbl.org";
    symbol = "URIBL_MULTI";
    resolve_ip = true;
  }
}
```

DKIM签名验证([RFC 6376](https://datatracker.ietf.org/doc/html/rfc6376))和DMARC策略评估([RFC 7489](https://datatracker.ietf.org/doc/html/rfc7489))作为独立的C模块内嵌在Rspamd的事件循环中，无需外部进程。SPF验证使用内置的DNS解析器和SPF记录解释器，同样在进程内完成，避免了SpamAssassin通过外部命令调用spfquery带来的fork开销。

一次完整的认证链日志清晰地展示了各模块的返回结果及其对总评分的贡献：

```
2026-07-15 01:45:23 #1(rdns) <a4f3b2> lua_dkim_tool: DKIM check: d=example.com
  result: pass; selector: 20240715; algorithm: rsa-sha256
2026-07-15 01:45:23 #1(rdns) <a4f3b2> lua_spf: SPF check:
  result: pass (-all); ip: 203.0.113.25; domain: example.com
2026-07-15 01:45:23 #1(rdns) <a4f3b2> lua_dmarc: DMARC:
  domain: example.com; policy: reject; result: pass
2026-07-15 01:45:23 #1(rdns) <a4f3b2> rspamd_task_write_log:
  id: <a4f3b2@example.com>; score: -0.82/15.00 [5/5];
  symbols: [R_DKIM_ALLOW(-0.2), R_SPF_ALLOW(-0.2),
  DMARC_POLICY_ALLOW(-0.1), RCVD_COUNT_THREE(0.0),
  MIME_TRACE(0.0), FROM_HAS_DN(0.0)]; action: no action
```

## 6. Redis缓存层与Maps分发机制

Rspamd对Redis有较强的运行时依赖，用作贝叶斯词元存储、模糊哈希共享存储、速率限制计数器、动态Maps分发以及配置数据的集中管理等。在生产环境中推荐使用多实例部署，将不同用途的Redis数据库隔离：

```
# /etc/rspamd/local.d/redis.conf
servers = "127.0.0.1:6379";
write_servers = "127.0.0.1:6379";
password = "rspamd_redis_pass";
db = "0";
timeout = 2.0;

map_cache_expire = 86400;
map_cache_max_size = 20000;
```

Maps是Rspamd中一种灵活的键值映射机制，支持静态文件(在磁盘上按行读取)、HTTP远程(定时拉取更新)和Redis(实时查询)三种后端。这一机制在安全策略的分发场景中具有实用价值，典型的使用案例包括白名单域、黑名单IP和发件人信誉列表。HTTP模式允许管理员通过集中管理平台下发策略，所有Rspamd实例定期拉取更新，无需逐个节点部署文件：

```
# /etc/rspamd/local.d/multimap.conf
WHITELIST_DOMAIN {
  type = "from";
  map = "https://cdn.internal/maps/whitelist-domains.map";
  score = -10.0;
  description = "Internal whitelisted sender domains";
}
BLACKLIST_IP {
  type = "ip";
  map = "redis://127.0.0.1:6379/blacklist-ips";
  score = 20.0;
  prefilter = true;
}
```

## 7. SpamAssassin规则兼容与迁移

Rspamd通过内置的`spamassassin`模块提供了对SpamAssassin规则语法的部分兼容，使现有的大量SA规则集可以逐步迁移重用。迁移路径通常分为三个阶段。

第一阶段将SA规则转换为Rspamd的Lua插件，最彻底的迁移方式，性能最优但开发投入最大。第二阶段利用Rspamd的regexp模块直接加载SA规则文件，可以快速迁移绝大部分正则规则，但需注意SA和Rspamd在正则引擎行为上的细微差异。第三阶段使用`external_services`模块在过渡期调用外部SA进程，作为临时方案，逐步将规则迁移到原生实现。

```
# /etc/rspamd/local.d/spamassassin.conf
spamassassin {
  ruleset = "SURBL";
  symbol = "SA_SCORE";
}

# /etc/rspamd/local.d/regexp.conf
config {
  "RE_SA_LEGACY" = "/etc/rspamd/sa-rules/re_sa_legacy.lua";
}
```

## 8. Web界面运维

Rspamd内置Web Worker提供基于AJAX的管理界面和RESTful API，默认监听127.0.0.1:11334，需通过反向代理(Nginx)对外暴露。Web界面支持实时扫描测试、历史查询、图表统计和配置热加载等运维功能。管理员可以直接在网页上粘贴邮件源码进行即时扫描，查看所有触发的symbol及对应分值，这在排查误报时极为便捷。

```
# /etc/rspamd/local.d/worker-controller.inc
bind_socket = "127.0.0.1:11334";
password = "$2$encrypted_hash_from_rspamadm";
secure_ip = "192.168.1.0/24;10.0.0.0/8";
enable_password = "admin_password";
static_dir = "${WWWDIR}";
```

常用的命令行管理工具在日常运维中比Web界面更高效。以下是几个高频使用的命令：

```
# 查看当前统计
$ rspamc stat
Results: scanned: 1245823; learned: 45231; actions: {
  "no action": 1203891,
  "add header": 18534,
  "rewrite subject": 9234,
  "reject": 14164
}

# 重置统计
$ rspamadm control reset_stat

# 配置重载（不丢数据）
$ rspamadm control reload
```

对于需要导出统计数据进行分析的场景，Rspamd的API提供了JSON格式的统计数据端点，可以集成到Grafana等监控平台中实现可视化的垃圾邮件拦截趋势图。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rspamd-architecture-scoring-engine.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
