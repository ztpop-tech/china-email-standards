---
title: "邮件系统灰名单 Greylisting 原理与部署"
source: "https://ztpop.net/kb/greylisting-guide.html"
license: CC-BY 4.0
---

# 邮件系统灰名单 Greylisting 原理与部署

摘要：电子邮件灰名单（Greylisting）是一种基于 SMTP 协议的轻量级反垃圾邮件技术，通过暂时拒收（SMTP 451）首次出现的"发送方IP+信封发件人+信封收件人"三元组，利用合法邮件传输代理（MTA）的自动重试机制（RFC 5321 §4.5.4）区分合法邮件与垃圾邮件。灰名单无需内容分析、不需签名库更新，部署成本极低而拦截率可达 90% 以上。本文基于 RFC 6647 灰名单适用性声明和 NIST SP 800-45 邮件安全指南，完整讲解灰名单的工作原理、Postfix postgrey 和 SQLgrey 的部署方案、自动白名单机制以及常见的延迟交付问题处理。

**一、灰名单工作原理：三元组与 SMTP 451**

灰名单的核心依据是一个简单事实：符合 RFC 5321 规范的合法 MTA 在遇到临时性故障（SMTP 4xx 返回码）时会自动重试发送，而大多数垃圾邮件发送程序（尤其是僵尸网络的垃圾邮件脚本）不会重试——它们采用"投递即忘"（fire-and-forget）模式遍历邮件地址列表，遇到失败直接跳过。灰名单利用这一行为差异，对首次出现的三元组（发送方IP地址、SMTP MAIL FROM 信封发件人、SMTP RCPT TO 信封收件人）返回临时拒收码 451（"Requested action aborted: local error in processing" 或 "Temporary failure, please try again later"），并将该三元组记录到数据库中。

RFC 5321 §4.5.4 明确规定：发送方 MTA 在遇到临时失败时必须至少重试，建议初始重试间隔至少 30 分钟，发送方必须持续重试至少 4-5 天才能放弃投递并返回永久失败（5xx）给原始发件人。具体来说，典型的重试策略是：第一次重试在 15-30 分钟后，然后指数退避（每次间隔翻倍），直到达到最大重试间隔（通常为 2-4 小时），然后以该间隔持续重试直到超时（通常 4-5 天）。当同一三元组在规定的最小重试间隔后再次出现时，灰名单服务将其视为合法重试，允许该邮件通过，并将该三元组加入"白名单"（自动白名单），后续来自同一三元组的邮件直接放行，不再拦截。

RFC 6647（"Email Greylisting: An Applicability Statement for SMTP"）由 IETF 在 2012 年发布，是灰名单技术的正式适用性声明。该 RFC 澄清了灰名单与 SMTP 标准合规性之间的关系：灰名单返回的 SMTP 451 是标准允许的临时拒收码，合法 MTA 的重试行为符合 RFC 5321，因此灰名单不会被标准合规的 MTA 理解为永久拒收。RFC 6647 同时提醒管理员注意灰名单可能带来的副作用——延迟交付、对多 IP 轮流发送的邮件服务提供商的影响，以及需要维护的白名单策略。

**二、Postfix + postgrey 灰名单部署**

postgrey 是 Postfix 生态中最成熟的灰名单策略守护进程，使用 Berkeley DB 存储三元组数据，通过 Postfix 的 policy delegation 协议与 Postfix 集成。部署步骤如下：

安装 postgrey：

```
apt install postgrey
```

默认配置下 postgrey 监听 127.0.0.1:10023。关键配置参数位于 /etc/default/postgrey：

```
POSTGREY_OPTS="--inet=127.0.0.1:10023 --delay=300 --max-age=35
  --retry-window=5 --auto-whitelist-clients=5"
```

参数说明：--delay=300 表示初次拒收后须等待 300 秒才开始接受重试；--max-age=35 表示白名单条目 35 天后过期；--retry-window=5 表示在初次拒收后 5 小时内重试的邮件都会被接受；--auto-whitelist-clients=5 表示同一客户端 IP 成功投递 5 次后自动加入白名单。

Postfix 集成配置（/etc/postfix/main.cf）：

```
smtpd_recipient_restrictions =
    permit_mynetworks
    permit_sasl_authenticated
    reject_unauth_destination
    check_policy_service inet:127.0.0.1:10023
```

check\_policy\_service 位置必须放在 permit\_mynetworks 和 permit\_sasl\_authenticated 之后、reject\_unauth\_destination 之后。这样本地网络和已认证用户不受灰名单影响。注意：如果将 check\_policy\_service 放在 reject\_unauth\_destination 之前，攻击者可能利用灰名单进行 SMTP 背向散射攻击（探测收件人是否存在）。正确的位置确保只有通过收件人合法性检查的邮件才进入灰名单流程。

配置完成后重启服务：

```
systemctl restart postgrey postfix
```

验证灰名单是否生效：查看 Postfix 日志中的 greylisted 条目：

```
grep "greylist" /var/log/mail.log
```

预期日志输出类似：

```
postgrey[12345]: action=greylist, reason=new,
  client_address=203.0.113.42, sender=user@example.com,
  recipient=alice@ztpop.net
```

**三、SQLgrey：基于 MySQL 后端的灰名单方案**

SQLgrey 是 postgrey 的替代品，使用 MySQL 或 PostgreSQL 作为后端存储，适合需要多服务器共享灰名单数据库的分布式邮件集群场景。与 postgrey (Berkeley DB) 相比，SQLgrey 的优势在于：多台邮件服务器可通过共享 MySQL 实例实现灰名单状态同步（例如同一域名的多台 MX 服务器共用一套灰名单数据库，避免用户因每次连接到不同 MX 而被反复拒收）；SQL 后端便于查询分析统计和手动管理白名单。

安装 SQLgrey：

```
apt install sqlgrey
```

创建 MySQL 数据库和用户：

```
CREATE DATABASE sqlgrey CHARACTER SET utf8mb4;
CREATE USER 'sqlgrey'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON sqlgrey.* TO 'sqlgrey'@'localhost';
FLUSH PRIVILEGES;
```

SQLgrey 配置文件 /etc/sqlgrey/sqlgrey.conf 中配置数据库连接：

```
db_type = mysql
db_name = sqlgrey
db_host = localhost
db_user = sqlgrey
db_pass = your_password
db_cleandelay = 86400
connect_delay = 300
max_age = 35
```

多服务器共享场景中，只需将各服务器的 db\_host 指向同一 MySQL 实例即可实现灰名单同步。SQLgrey 的 Postfix policy service 集成方式与 postgrey 相同，Postfix 配置中 check\_policy\_service inet:127.0.0.1:2501（SQLgrey 默认监听端口）。

**四、自动白名单与豁免策略**

灰名单的自动白名单机制（Auto-Whitelisting）是保证用户体验的关键。自动白名单的触发条件包括：

（1）SPF Pass 豁免：如果发件域的 SPF 验证结果为 Pass，说明发送 IP 是域所有者授权的，灰名单可跳过该邮件。这利用了 SPF 作为前置筛选，减少了灰名单的拦截量和延迟。在 postgrey 中可以通过 --whitelist-clients 配置文件和 SPF 验证的前置 Postfix 策略实现。（2）域名白名单：对已知的大型邮件服务提供商（如 Gmail、Outlook、QQ邮箱等）提前加入白名单，避免因这些服务商的多 IP 轮流发送（multi-IP rotation）导致的重复灰名单拦截。postgrey 默认安装时已包含一份包含 300+ 常用域名的白名单文件 /etc/postgrey/whitelist\_clients。（3）成功计数自动白名单：postgrey 的 --auto-whitelist-clients=N 参数指定当一个 IP 地址成功投递 N 封邮件后，将该 IP 自动加入白名单。默认值通常设为 5。（4）DKIM 签名验证豁免：如果邮件带有有效的 DKIM 签名，表明发件域对该邮件负责，可作为灰名单豁免的依据。可通过 Postfix 的 dkim-filter/milter 与 postgrey 配合实现。

手动白名单配置（/etc/postgrey/whitelist\_clients）：

```
# 域名白名单（匹配 MAIL FROM 域）
mailchimp.com
sendgrid.net

# IP 白名单（CIDR）
66.231.80.0/20   # Constant Contact

# 正则表达式匹配
/^postmaster@/
```

**五、常见问题与排查**

问题一：邮件延迟过长。灰名单的本质决定了初次投递必定有延迟。延迟大小取决于发送方 MTA 的重试间隔配置。大多数大型邮件服务提供商的重试间隔为 15-30 分钟，因此用户感知延迟通常在 15-30 分钟以内。部分小型邮件服务器可能配置了较长的重试间隔（如 1 小时），导致延迟感知明显。解决方案：（a）降低灰名单 delay 参数（如 --delay=180 秒），但不建议低于 120 秒——过短的 delay 可能导致部分发送缓慢的垃圾邮件程序也能通过；（b）扩充自动白名单和 SPF/DKIM 豁免范围。

问题二：密码重置邮件或验证邮件丢失。许多 Web 服务的密码重置和账户验证邮件通过第三方邮件投递服务发送（如 SendGrid、Mailgun），这些服务不会重试，因为它们生成的邮件是一次性的（如验证链接包含一次性令牌）。一旦被灰名单拦截，用户将无法收到验证邮件。解决方案：将常见的邮件投递服务商域名和 IP 段加入白名单。

问题三：多 MX 服务器轮转导致的重复灰名单。发送方 MTA 可能在不同重试中连接到不同的 MX 服务器（如 mx1.example.com 和 mx2.example.com），而每台 MX 服务器的灰名单数据库不共享。postgrey 单机部署时，发送方每次连接到不同 MX 都会被当作新三元组触发灰名单拦截。解决方案：使用 SQLgrey 的共享 MySQL 后端，或在 postgrey 单机场景下确保负载均衡配置为基于发送方 IP 的会话保持（session persistence）。

问题四：邮件服务商的多 IP 发送池。Gmail、Outlook 等大型邮件服务商使用多个出站 IP 地址，同一邮件可能从不同 IP 重试，导致每次都被视为新三元组。postgrey 的 --lookup-by-subnet 参数可基于 /24 子网进行 IP 匹配，而非精确 IP 匹配，缓解此问题。或使用域名白名单替代 IP 白名单。配置方式：修改 postgrey 启动参数 --lookup-by-subnet=/24 后，来自同一 /24 子网的 IP 将被视为同一客户端。

**六、灰名单在多层反垃圾体系中的定位**

根据 NIST SP 800-45 Version 2（"Guidelines on Electronic Mail Security"），电子邮件安全应采取纵深防御策略，在邮件传输路径的不同阶段设置多道防线。灰名单属于 SMTP 会话层面的防御，适合部署在最外层——在收件人地址是否存在的检查（reject\_unauth\_destination）之后、DNS 黑名单查询（DNSBL）之前。多层防御体系的典型顺序为：连接控制（速率限制、IP 信誉）→ 协议合规检查 → 收件人合法性检查 → 灰名单 → DNS 黑名单查询 → SPF/DKIM/DMARC 认证 → 内容过滤（Bayesian/规则）→ 病毒扫描。

灰名单在这一顺序中的优势是成本极低——不需要内容分析、不需要维护签名库、不需要复杂的规则引擎。一个三元组查询通常只需几微秒，而内容过滤（如 SpamAssassin）可能需要数百毫秒到数秒。将灰名单放在内容过滤之前，可以为系统节省大量计算资源——统计显示，灰名单可拦截 50%-90% 的垃圾邮件，这意味着这些邮件根本不需要进入后续的资源密集型处理环节。

昆仑邮件系统的反垃圾邮件模块内置了灰名单引擎，管理员可在管理后台一键开启，自动与系统中的 SPF 验证、DKIM 验证、DNSBL 查询模块协同工作。系统后端采用类 postgrey 的三元组匹配逻辑，并内置了针对国内主流邮件服务商（QQ邮箱、163/126、阿里邮箱等）的预配置白名单，部署后即可生效，无需手动配置域名列表。

**七、参考文献**

[1] RFC 6647 - Email Greylisting: An Applicability Statement for SMTP. IETF, June 2012. https://datatracker.ietf.org/doc/rfc6647/

[2] RFC 5321 - Simple Mail Transfer Protocol, Section 4.5.4 (Retry Strategies). IETF, October 2008. https://datatracker.ietf.org/doc/rfc5321/

[3] NIST SP 800-45 Version 2 - Guidelines on Electronic Mail Security. NIST, February 2007. https://csrc.nist.gov/publications/detail/sp/800-45/version-2/final

[4] RFC 2821 - Simple Mail Transfer Protocol (Obsoleted by RFC 5321). IETF, April 2001.

[5] GB/T 37002-2023 - 信息安全技术 电子邮件系统安全技术要求. 国家标准化管理委员会, 2023.

[6] postgrey 项目文档. https://postgrey.schweikert.ch/

了解更多邮件技术实践，请访问知识库或联系

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/greylisting-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
