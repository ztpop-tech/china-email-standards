---
title: "邮件系统迁移策略：IMAP 迁移、混合共存与分阶段切流"
source: "https://ztpop.net/kb/exchange-online-migration-strategy.html"
license: CC-BY 4.0
---

# 邮件系统迁移策略：IMAP 迁移、混合共存与分阶段切流

## 概述

邮件系统迁移是 IT 基础设施中最复杂的操作——涉及大量历史数据、不停机要求和严格的数据一致性保障。迁移到基于 Postfix/Dovecot 的开源邮件系统需考虑三个关键环节：历史邮件数据的完整迁移（通过 IMAP 协议逐用户拷贝）、SMTP 流量在迁移期间的路由共存，以及 DNS 切换的分阶段执行策略。每封邮件的 UID、标记状态和文件夹结构需完整保留，用户不应感知切换过程。

## IMAP 数据迁移

IMAP 迁移通过源服务器和目标服务器之间的 IMAP 连接逐封拷贝邮件。imapsync 是最成熟的 IMAP 迁移工具，支持增量同步（跳过已迁移邮件）、文件夹映射和邮件标记保留。迁移流程通常分三次执行：初次全量迁移（T-30天）、增量同步（T-3天）和最终增量 + 锁定源邮箱（T-0天）以最小化切换窗口中的数据差异。

```
# imapsync 单用户迁移
imapsync \
  --host1 exchange.example.com --user1 user@example.com \
  --password1 src_pass --ssl1 \
  --host2 new-mail.example.com --user2 user@example.com \
  --password2 dst_pass --ssl2 \
  --syncinternaldates --useheader Message-ID \
  --delete2duplicates --maxage 3650

# 批量迁移（从用户列表文件）
while IFS=: read -r user pass_src pass_dst; do
  imapsync --host1 exchange.example.com --user1 "$user" \
    --password1 "$pass_src" --ssl1 \
    --host2 new-mail.example.com --user2 "$user" \
    --password2 "$pass_dst" --ssl2 \
    --syncinternaldates --useheader Message-ID &
done < users.txt

# 统计迁移进度
grep "successfully" /var/log/imapsync/*.log | wc -l
```

## SMTP 混合共存与 DNS 切换

迁移期间新旧系统需要同时接收邮件。新系统配置中继域（relay\_domains）接收目标域邮件，对于尚未迁移的用户通过 transport\_maps 将邮件中继回 Exchange。随着用户分批迁移，transport\_maps 中的转发条目逐批删除。DNS MX 记录在全部用户迁移完成后切换，切换前通过修改 TTL 至 300 秒加速 DNS 传播。

```
# Postfix 共存配置：未迁移用户邮件中继回 Exchange
# /etc/postfix/main.cf
relay_domains = example.com
transport_maps = hash:/etc/postfix/transport
relay_recipient_maps = hash:/etc/postfix/relay_recipients

# /etc/postfix/transport
# user1@example.com    lmtp:unix:private/dovecot-lmtp   # 已迁移
# user2@example.com    smtp:[exchange.example.com]      # 未迁移

# DNS 切换前降低 TTL
# example.com.  IN  MX  10  exchange.example.com.   ; TTL 300

# 监控切换后流量
tail -f /var/log/mail.log | grep -E "relay=exchange|delivered via lmtp"
```

## 踩坑与排错

IMAP 迁移中邮件过大（>50MB附件）可能导致 imapsync 超时——需设置 --maxsize 参数跳过大邮件并在切换后通过其他方式迁移。迁移时间窗口内用户在旧系统发送的邮件可能不会自动同步到新系统，需要在 IMAP 迁移之外通过 SMTP 转发收件箱归档。切换后立即检查 DNS 缓存中仍指向旧 MX 的外部发件方——至少维护一周的旧 MX 转发。

本站技术文章采用 CC-BY 4.0 许可，可自由引用，仅需标注来源 [ztpop.net](https://www.ztpop.net)。

### 相关主题

* [邮件迁移完全指南](/email-migration.html)：从评估到上线的邮件迁移全流程
* [Exchange 邮件迁移规划框架](/kb/exchange-migration-planning-framework.html)

class="article-footer">

本文由 ztpop.net 知识库编辑发布。了解更多邮件技术实践，请访问知识库或扫码联系我们。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/exchange-online-migration-strategy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
