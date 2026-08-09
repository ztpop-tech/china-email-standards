---
title: "云邮件网关与本地网关混合部署时，连接器和邮件路由该怎么设计？"
source: "https://ztpop.net/kb/cloud-hybrid-connector-mailflow.html"
license: CC-BY 4.0
---

# 云邮件网关与本地网关混合部署时，连接器和邮件路由该怎么设计？

**先画清四条邮件路径**

混合部署里最容易出错的是**没把路径穷举清楚**。至少存在四条：

1. 外部 → 云邮箱
2. 外部 → 本地邮箱
3. 云邮箱 → 外部
4. 本地邮箱 → 外部

此外还有内部互通（云 ↔ 本地）。**每条路径分别回答：第一跳是谁、在哪一点做安全过滤、出口 IP 是什么。**把这张表填完，连接器怎么配基本就确定了。

**连接器的方向是相对于云端定义的**

* **入站连接器：**接收**发往云端**的邮件，用于标识来源（本地组织或第三方网关）并建立信任关系。
* **出站连接器：**把**从云端发出**的邮件投向指定目标（本地组织、第三方网关或特定域）。

方向搞反是新手最常见的错误，表现为邮件在两端之间来回投递直至超时。

**集中式传输与直投的取舍**

**集中式传输**把云邮箱的所有外发邮件先回送到本地或第三方网关，由其统一出口。

* **选它的理由：**合规要求全部外发邮件经过统一的留痕、加密或数据防泄漏检查；对外必须呈现固定的出口 IP。
* **代价：**邮件路径变长、延迟增加，本地网关成为**单点故障**——它一停，云邮箱也发不出信。

**判据：**没有明确的合规或固定出口 IP 要求，就不要开集中式传输。为了「统一管理」这种模糊理由而引入单点，不划算。

**TLS 必须强制并校验证书**

组织内部两个网关之间的连接器，是少数**可以且应当强制加密**的场景——两端都由你控制，不存在对方不支持的兼容性顾虑。

**配置要点：**连接器上启用强制 TLS，并校验对端证书的颁发者与主题名称，而不是只要求「尽力而为的加密」。仅开启机会性加密时，中间人可以通过剥离能力协商让连接降级为明文。

对外部通信，则通过 MTA-STS 一类机制声明本域的传输安全策略，让发信方能够拒绝被降级的连接。

**MX 指向与环路排查**

环路的典型成因：MX 指向网关 A，A 按规则把邮件转给云端，而云端的接受域类型或出站连接器又把该域的邮件送回 A。

**排查顺序：**

1. 查邮件头中的接收链，数一数在两端之间往返了几次——环路一眼可见。
2. 核对云端**接受域的类型**：域是被视为「本组织权威」还是「内部中继」，这个设置直接决定了收件人不存在时是拒绝还是继续转发。这是环路最高频的根因。
3. 核对出站连接器的作用域，确认没有把本组织自己的域包含进去。

**收敛内部中继权限**

混合环境中通常需要允许打印机、业务系统等设备中继邮件。这类配置极易演变成事实上的开放中继。

* 中继连接器**必须**按源 IP 精确限定，且列表要定期核对。
* 优先限制为只能发往内部收件人；确需外发的单独评估。
* 为设备使用专用子域发信，便于在认证与日志中单独识别和限速。
* 定期检查这些通道的外发量——**异常放大往往是设备被利用的第一个信号**。

参考：[Microsoft Learn：Configure mail flow using connectors](https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/use-connectors-to-configure-mail-flow/use-connectors-to-configure-mail-flow)、[Microsoft Learn：Transport routing in Exchange hybrid deployments](https://learn.microsoft.com/en-us/exchange/transport-routing)、[RFC 5321：Simple Mail Transfer Protocol](https://www.rfc-editor.org/rfc/rfc5321.html)、[RFC 8461：SMTP MTA Strict Transport Security (MTA-STS)](https://www.rfc-editor.org/rfc/rfc8461.html)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cloud-hybrid-connector-mailflow.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
