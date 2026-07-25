---
title: "IMAP IDLE 实时推送深度解析 — RFC 2177：从轮询到服务端推送的邮件到达通知"
source: "https://ztpop.net/kb/imap-idle-push-rfc2177.html"
license: CC-BY 4.0
---

# IMAP IDLE 实时推送深度解析 — RFC 2177：从轮询到服务端推送的邮件到达通知

邮件服务器要让客户端「新邮件即时可见」，最朴素的方法是客户端定时轮询 `SELECT` 邮箱查 `EXISTS`。但轮询要么延迟高（间隔长），要么空耗连接与电量（间隔短）。RFC 2177 定义的 IMAP IDLE 扩展让客户端在邮箱上下文中挂起一条命令，由服务端在邮件到达时主动推送通知，是邮件系统实现「准实时收信」的标准路径[1]。

## 轮询的代价

每 60 秒轮询一次、10 万在线用户，意味着每天约 1.44 亿次无意义查询。RFC 2177 引言明确指出，频繁轮询浪费服务器资源与网络带宽，而 IDLE 让服务端在状态变化时才通知客户端[1]。对于移动端，轮询还会持续唤醒radio，显著缩短续航。

## RFC 2177 IDLE 命令

客户端在已 `SELECT`/`EXAMINE` 的邮箱下发送 `IDLE`，服务端回 `+` 进入待命；此后无需客户端请求，服务端直接推送未标记响应（如新邮件 `EXISTS`、`RECENT`）[1]。

```
C: A001 SELECT INBOX
S: A001 OK [READ-WRITE] Selected.
C: A002 IDLE
S: + idling
   * 15 EXISTS        <- 新邮件到达，服务端主动推送
   * 2 RECENT
DONE                  <- 客户端发送终止行退出 IDLE
S: A002 OK IDLE terminated
```

客户端读取推送后，再发 `FETCH` 拉取新邮件头/正文。整个过程中只有一次真正的数据拉取，中间等待零流量。

## 续期超时机制

IDLE 不能无限挂起。RFC 2177 §3 建议服务端在约 30 分钟（1800 秒）后主动终止 IDLE 并回 `OK`，客户端必须重新进入 IDLE 以维持推送[1]。移动网络（NAT/运营商）通常比 30 分钟更早回收空闲连接，因此健壮客户端会以 10–25 分钟为周期主动 `DONE` 并重建 IDLE。

```
# 客户端心跳策略（伪代码）
while connected:
    send "IDLE"; wait_for_push_or_timeout(20min)
    send "DONE"; reconnect_and_idle()
```

## 与移动推送的协同

纯 IDLE 在 App 退到后台时会被系统挂起。生产方案通常是「IDLE + 平台推送」双层：App 前台用 IDLE 直连；后台由邮件系统向厂商推送服务（如 APNs/FCM）发静默通知，唤醒 App 重建 IDLE 或拉取[2]。这样兼顾实时性与电量。

## Dovecot 部署要点

Dovecot 原生支持 IMAP IDLE，无需额外配置；要点在连接与超时参数：

```
# dovecot.conf
mail_max_userip_connections = 50   # IDLE 长连接会占用连接数，需预留
# 防火墙/代理必须允许 30min 级空闲连接透传，避免提前断链
```

若前置了反向代理或负载均衡，必须将其空闲超时设为大于 IDLE 续期周期（建议 ≥ 35 分钟），否则推送通道会在服务端推送前被中间层切断。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/imap-idle-push-rfc2177.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
