---
title: "邮件系统灰度发布与回滚方案：从DNS TTL到rsync恢复"
source: "https://ztpop.net/kb/email-canary-rollback.html"
license: CC-BY 4.0
---

# 邮件系统灰度发布与回滚方案：从DNS TTL到rsync恢复

#### 📑 目录

1. [灰度发布策略概览](#s1)
2. [多MX优先级分级发布（Graded Rollout）](#s2)
3. [DNS TTL 逐步降低与恢复](#s3)
4. [smtp\_generic\_maps 测试流量分流](#s4)
5. [rsync 回滚流程](#s5)
6. [变更清单与检查点](#s6)

## 一、灰度发布策略概览

邮件系统作为关键业务基础设施，任何变更（Postfix 版本升级、配置参数修改、过滤规则更新、存储节点变更）都带来停产风险。灰度发布（Canary Release / Staged Rollout）通过控制变更的影响范围和进度，将风险限制在可管控的子集内。

邮件系统独特的挑战来自其 **store-and-forward** 架构（RFC 5321 Section 2.1）和 **异步性**：发件 MTA 的重试机制可能在一封邮件上持续 4~48 小时，这意味着变更的影响窗口远长于变更操作本身。

### 1.1 灰度发布分层框架

表 1：分层灰度发布框架

| 层级 | 流量比例 | 监控周期 | 决策点 |
| --- | --- | --- | --- |
| L1 — 测试 | < 5% (单个低优先 MX) | 30 min | 服务存活、关键错误 |
| L2 — 金丝雀 | 10–20% (MX prio 次高) | 2 h | 投递成功率、延迟 P95 |
| L3 — 扩展 | 30–50% (MX prio 主/次) | 4 h | 全指标基线内 |
| L4 — 全量 | 100% | 24 h | 无新增告警 |

## 二、多MX优先级分级发布（Graded Rollout）

### 2.1 原理

DNS MX 优先级是邮件系统最天然、最安全的流量分割机制。通过控制不同优先级 MX 记录的更新顺序，可以实现流量的分阶段切换。RFC 5321 Section 5.1 规定：发件 MTA **必须**优先尝试最低优先级（最高优先级）的 MX，失败后再尝试次低优先级。控制 MX 的优先级值即可控制哪台 MX 获得多少流量。

### 2.2 实施步骤

```
# 场景: 部署新版本 Postfix 配置到全网
# 环境: 3 台 MX: mx1.example.com (prio 5), mx2.example.com (prio 10), mx3.example.com (prio 20)

# Phase 1: 仅在 mx3 (最低优先级，备用 MX) 上部署新版本
ssh mx3.example.com "apt-get update && apt-get install postfix-3.9"
# 此时 mx3 优先级 20，在 mx1/mx2 正常时只有极少量流量

# Phase 2: 降低 mx3 优先级 → L2 (金山雀)
# 调整 MX 记录: 将 mx3 优先级从 20 提升到 10
example.com.  IN  MX  5   mx1.example.com.
example.com.  IN  MX  10  mx2.example.com.
example.com.  IN  MX  10  mx3.example.com.
# 约 50% 流量进入 mx3（与 mx2 均分优先级 10 的流量）

# Phase 3: 全量发布 — 降低 mx1/mx2 并全部升级
ssh mx2.example.com "apt-get update && apt-get install postfix-3.9"
ssh mx1.example.com "apt-get update && apt-get install postfix-3.9"

# Phase 4: 回归标准优先级配置
example.com.  IN  MX  5   mx1.example.com.
example.com.  IN  MX  5   mx2.example.com.
example.com.  IN  MX  10  mx3.example.com.
```

### 2.3 注意事项

* MX 优先级降低后，DNS 缓存生效前，旧优先级记录仍被使用（TTL 依赖性）
* 部分发件 MTA 实现不遵循优先级轮询，始终选择同一 IP
* 回滚时只需将 MX 优先级恢复到发布前的值，等待 TTL 过期
* 建议在 MX 变更前后各收集 24 小时的投递统计做基线对比

## 三、DNS TTL 逐步降低与恢复

### 3.1 TTL 调整策略

DNS TTL 控制 MX、A 等记录在解析器中的缓存时长。正常运行时 TTL 可设为 300–3600 秒以减少 DNS 查询负载；变更操作前应将 TTL **临时降低**，以便变更后能快速生效。

```
# Step 1: 降低 TTL（发布前 2× 原 TTL 时间）
# 原 TTL: 3600 (1 小时)
example.com.  300   IN  MX  5   mx1.example.com.
example.com.  300   IN  MX  10  mx2.example.com.
_mta-sts.example.com.  300  IN  TXT  "v=STSv1; id=20260724001"

# 等待至少 2× 原 TTL（7200 秒）让旧缓存过期
sleep 7200

# Step 2: 执行 MX 变更
example.com.  300   IN  MX  5   mx1-new.example.com.
example.com.  300   IN  MX  10  mx2-new.example.com.

# Step 3: 确认所有 DNS 服务器更新完毕
dig @ns1.example.com example.com MX +short
dig @ns2.example.com example.com MX +short

# Step 4: 恢复 TTL（确认稳定后）
example.com.  3600  IN  MX  5   mx1-new.example.com.
example.com.  3600  IN  MX  10  mx2-new.example.com.
```

### 3.2 验证缓存过期

```
# 检查各地 DNS 解析结果
for ns in 8.8.8.8 1.1.1.1 208.67.222.222; do
  echo "--- $ns ---"
  dig @$ns example.com MX +short
done

# 检查权威 NS 的 SOA 序列号（确认 slave 已同步）
dig soa example.com +short
# 序列号应已递增

# 监控 Postfix 日志确认发件 MTA 开始使用新 MX
tail -f /var/log/mail.log | grep "to=" | head -20
```

## 四、smtp\_generic\_maps 测试流量分流

### 4.1 原理

`smtp_generic_maps` 是 Postfix 的出站地址重写机制（RFC 5321 的 address masquerading）。通过将测试发件人的地址重写为特定的发件域名，可以实现出站流量的按发件人路由。

在灰度发布场景中，可以将特定测试用户或测试组的出站邮件路由到新版本 MX，实现精准的流量分流。

### 4.2 配置示例

```
# /etc/postfix/main.cf
# Generic maps 做出站信封地址重写
smtp_generic_maps = hash:/etc/postfix/generic

# 定义出站中继分流
# /etc/postfix/transport — 按发件人路由
# transport_maps = hash:/etc/postfix/transport

# /etc/postfix/transport:
user1@example.com    smtp:mx-canary.example.com:25
user2@example.com    smtp:mx-canary.example.com:25
# 其他用户正常投递
example.com          smtp:

postmap /etc/postfix/transport
postfix reload
```

### 4.3 基于发件域的分流

对于更精细的分流需求，可以创建一个专用的测试发件域：

```
# /etc/postfix/main.cf
smtp_generic_maps = hash:/etc/postfix/generic

# /etc/postfix/generic:
user1@example.com     user1.test@test.example.com
user2@example.com     user2.test@test.example.com

# 或更复杂的场景：基于邮件头路由
# /etc/postfix/header_checks
/^Subject:.*TEST/     FILTER smtp:mx-canary.example.com:25

# 构建并加载
postmap /etc/postfix/generic
postmap /etc/postfix/transport
postfix reload
```

### 4.4 回滚时的 generic maps 清理

```
# 回滚时只需注释掉或删除 generic/transport 中的测试条目
# 或:
postmap -d user1@example.com /etc/postfix/transport
postmap -d user2@example.com /etc/postfix/transport
# 恢复后验证
postmap -q user1@example.com /etc/postfix/transport
# 应返回空
```

## 五、rsync 回滚流程

### 5.1 回滚前的快照

任何配置变更前，应创建回滚点：

```
#!/bin/bash
# 回滚快照脚本 — 在变更操作执行前运行
DATE=$(date +%Y%m%d_%H%M%S)
ROLLBACK_DIR="/opt/rollback/$DATE"

mkdir -p "$ROLLBACK_DIR"/{postfix,dovecot,rspamd,clamav,nginx}

# 配置快照
cp -a /etc/postfix/main.cf      "$ROLLBACK_DIR/postfix/"
cp -a /etc/postfix/master.cf    "$ROLLBACK_DIR/postfix/"
cp -a /etc/postfix/*.db         "$ROLLBACK_DIR/postfix/"
cp -a /etc/dovecot              "$ROLLBACK_DIR/dovecot/"
cp -a /etc/rspamd               "$ROLLBACK_DIR/rspamd/"
cp -a /etc/clamav               "$ROLLBACK_DIR/clamav/"
cp -a /etc/nginx                "$ROLLBACK_DIR/nginx/"
cp -a /etc/aliases              "$ROLLBACK_DIR/"

# 软件包版本记录
dpkg -l | grep -E 'postfix|dovecot|clamav|rspamd|nginx' \
  > "$ROLLBACK_DIR/pkg-versions.txt"

# 回滚说明生成
cat > "$ROLLBACK_DIR/README.txt" << EOF
回滚点时间: $(date)
变更描述: [填写]
回滚命令:
  cp -a $ROLLBACK_DIR/postfix/main.cf /etc/postfix/main.cf
  cp -a $ROLLBACK_DIR/postfix/master.cf /etc/postfix/master.cf
  postfix reload
  systemctl restart dovecot rspamd clamav-daemon nginx
EOF

# 持久化备份到远程存储
rsync -az "$ROLLBACK_DIR" backup-server:/var/backups/mta-rollback/
```

### 5.2 配置回滚流程

```
#!/bin/bash
# rollback.sh — 回滚到指定快照点
if [ -z "$1" ]; then
  echo "用法: $0 <回滚点目录>"
  ls -1 /opt/rollback/
  exit 1
fi

RB="$1"
echo "[$(date)] 开始回滚到 $RB ..."

# 1. 恢复 Postfix 配置
echo "→ 恢复 Postfix 配置"
cp -a "$RB/postfix/main.cf" /etc/postfix/mainf.cf.bak
cp "$RB/postfix/main.cf" /etc/postfix/main.cf
cp "$RB/postfix/master.cf" /etc/postfix/master.cf
# 恢复 *.db 文件（避免 postmap 重建）
cp -a "$RB/postfix"/*.db /etc/postfix/ 2>/dev/null

# 2. 恢复 Dovecot
echo "→ 恢复 Dovecot 配置"
cp -a /etc/dovecot /etc/dovecot.bak.$(date +%s)
cp -a "$RB/dovecot"/* /etc/dovecot/

# 3. 恢复 Rspamd / ClamAV
echo "→ 恢复安全组件配置"
cp -a "$RB/rspamd"/* /etc/rspamd/
cp -a "$RB/clamav"/* /etc/clamav/

# 4. 恢复 Nginx
echo "→ 恢复 Nginx 配置"
cp -a "$RB/nginx"/* /etc/nginx/

# 5. 重启服务（按依赖顺序）
echo "→ 重启服务"
systemctl restart clamav-daemon
sleep 2
systemctl restart rspamd
sleep 2
systemctl restart dovecot
postfix reload
systemctl reload nginx

# 6. 验证服务状态
echo "→ 验证状态"
systemctl status clamav-daemon --no-pager -l | head -3
systemctl status rspamd --no-pager -l | head -3
systemctl status dovecot --no-pager -l | head -3
postfix status

echo "[$(date)] 回滚完成。请检查 /var/log/mail.log 确认无异常。"
```

### 5.3 软件包级回滚

仅恢复配置文件可能不足以回滚软件包版本变更：

```
# 查看变更前的软件包版本
cat /opt/rollback/20260724_100000/pkg-versions.txt

# 使用 apt history 回滚到指定版本
apt-get install postfix=3.8.6-1~deb12u1

# 或使用 snapshots.debian.org 下载特定版本
cd /tmp
wget "https://snapshot.debian.org/archive/debian/20260701T000000Z/pool/main/p/postfix/postfix_3.8.6-1~deb12u1_amd64.deb"
dpkg -i postfix_3.8.6-1~deb12u1_amd64.deb

# 阻止自动升级（确保不会在下次 apt upgrade 时被升级）
apt-mark hold postfix
```

### 5.4 rsync 完整恢复（灾难级回滚）

当变更涉及存储层（例如 Dovecot 索引格式变更）且发生灾难性故障时，需要从远程备份全量恢复：

```
# 从备份服务器 rsync 恢复
# 假设备份策略: 每小时增量快照，每日全量

# 方案: 停止服务 → rsync 恢复 → 启动
systemctl stop postfix dovecot

# 恢复配置
rsync -az --delete backup-server:/var/backups/mta-rollback/20260724_100000/ /etc/

# 恢复邮件存储（如必要）
rsync -az --delete backup-server:/mailstore-incremental/ /var/vmail/

# 恢复邮件队列（如必要）
rsync -az --delete backup-server:/var/spool/postfix-backup/ /var/spool/postfix/

# 启动服务
systemctl start dovecot
systemctl start postfix
postqueue -p | wc -l     # 确认队列恢复

# 监控投递
tail -f /var/log/mail.log | grep "status=sent"
```

## 六、变更清单与检查点

### 6.1 发布前检查清单

```
[ ] 创建回滚快照: /opt/rollback/$(date +%Y%m%d)
[ ] 记录当前软件包版本
[ ] 降低 DNS TTL 至 300 秒（提前 2× 原 TTL）
[ ] 确认所有权威 NS 已更新
[ ] 制定回滚触发条件（P95 延迟 > 3× 基线）
[ ] 通知运维值班人员
[ ] 确认监控告警通道正常
[ ] 准备回滚脚本
[ ] 确认 rsync 备份连通性
```

### 6.2 发布中监控指标

```
#!/bin/bash
# 发布期间持续监控脚本
while true; do
  echo "=== $(date) ==="

  # 1. Postfix 队列深度
  QDEPTH=$(mailq | grep -c "^[0-9A-F]")
  echo "队列深度: $QDEPTH"

  # 2. 最近 5 分钟投递延迟
  LATENCY=$(tail -10000 /var/log/mail.log | grep "status=sent" \
    | grep -oP "delay=\K[0-9.]+" | awk '{sum+=$1; n++} END {if(n>0) print sum/n; else print "N/A"}')
  echo "平均投递延迟(5min): ${LATENCY}s"

  # 3. 错误比例
  DEFERRED=$(grep "status=deferred" /var/log/mail.log | wc -l)
  SENT=$(grep "status=sent" /var/log/mail.log | wc -l)
  if [ "$SENT" -gt 0 ]; then
    RATIO=$(echo "scale=2; $DEFERRED / ($SENT + $DEFERRED) * 100" | bc)
    echo "deferred 比例: ${RATIO}%"
  fi

  # 4. 服务健康检查
  systemctl is-active postfix dovecot rspamd clamav-daemon nginx \
    | tr '\n' ' '
  echo

  sleep 60
done
```

### 6.3 回滚触发条件

表 2：回滚触发条件

| 指标 | 触发值 | 说明 |
| --- | --- | --- |
| 队列深度基线比 | > 200% | 邮件大量堆积 |
| 投递延迟 P95 | > 3× 基线 | 性能退化 |
| deferred 比例 | > 10% | 异常投递失败 |
| 服务异常 | 任一 rsyslog 服务崩溃 | 立即回滚 |
| 告警频次 | > 5 条/5min | 异常告警风暴 |

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-canary-rollback.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
