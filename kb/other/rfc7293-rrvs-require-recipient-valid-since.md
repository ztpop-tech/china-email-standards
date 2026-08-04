---
title: "RFC 7293 RRVS：用 Require-Recipient-Valid-Since 拦截僵尸账号投递"
source: "https://ztpop.net/kb/rfc7293-rrvs-require-recipient-valid-since.html"
license: CC-BY 4.0
---

# RFC 7293 RRVS：用 Require-Recipient-Valid-Since 拦截僵尸账号投递

## 概述

邮箱地址会被回收、重用：用户注销后，域名可能把该地址重新分配给他人；休眠账号也可能被攻击者接管。若发件方缓存了旧地址并持续投递敏感邮件（密码重置、账单、验证码），就可能泄露给新持有者。RFC 7293 定义 `Require-Recipient-Valid-Since`（RRVS）头，让发件方声明"我只投递给在这个时间戳之前就存在的收件人"，接收方据此放行或拒收。

## 工作原理

发件方在邮件中带上期望的"有效起始时间"：

```
Require-Recipient-Valid-Since: <alice@example.com>; 2018-01-01T00:00:00Z
```

接收方 MTA 检查 `alice@example.com` 的创建/分配时间：若账号在该时间之后才存在（即被回收重用），则返回 `5.7.21`（收件人晚于要求时间创建）拒绝投递，并建议发件方从地址簿移除该联系人。这等于给"过期地址"上了一道闸门。

## 典型防护场景

* **账号接管阻断**：攻击者拿到旧员工邮箱后，原系统向该地址发的重置邮件被 RRVS 拒绝，避免权限续期。
* **回收邮箱防泄露**：域名重用地址后，历史订阅的账单/通知不再投递给新主。
* **减少后退信**：对已知无效地址提前拒收，降低退信与队列负担。

## 部署要点

RRVS 需要发件方维护"每个联系人首次确认的时间"，并在提交时带上；接收方维护"每个本地账号的创建时间"。它可与 DMARC、ARP（Address Risk Profile）等配合。对政企邮件系统，RRVS 是账号生命周期管理（入职/离职/回收）在邮件层的自然延伸。

## 对信创邮件与账号安全的启示

在信创邮件替换中，账号同步（如 AD/LDAP 同步）应一并导出"账号创建时间"，供 RRVS 判断；同时建议在邮件安全网关对出站敏感邮件默认附加 RRVS，降低离职/回收账号引发的横向风险。这与 MFA、异常发信监测共同构成账号防盗体系。

### 相关主题

* [邮件账号防盗与 SMTP 劫持检测](/kb/email-account-hijacking-defense.html)：凭据窃取后的实时发现
* [信创 AD 账号同步指南](/kb/xinchuang-ad-sync-guide.html)：账号生命周期同步
* [邮件安全威胁全景](/kb/email-security-threats.html)：账号接管与 BEC 分类
* [DMARC 完全指南](/kb/dmarc-guide.html)：域信任基线

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/rfc7293-rrvs-require-recipient-valid-since.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
