---
title: "为什么 Yahoo 要求发送 IP 具备有效的正向与反向 DNS（PTR）记录？"
source: "https://ztpop.net/kb/yahoo-faq-06.html"
license: CC-BY 4.0
---

# 为什么 Yahoo 要求发送 IP 具备有效的正向与反向 DNS（PTR）记录？

1
为什么 Yahoo 要求发送 IP 具备有效的正向与反向 DNS（PTR）记录？
▼

**双 DNS 是强制要求**

无论所有发送方还是批量发送方，Yahoo 都要求发送 IP 具备有效的正向与反向 DNS 记录。反向 DNS（PTR）应能反映你的域名，且不应看起来像动态分配的 IP，而应是静态邮件服务器的名称。

**作用**

完整的正向/反向 DNS 是可追溯、可信发送基础设施的基础，有助于接收方验证来源、建立稳定信誉，也是 Yahoo 2024 强制标准之一。

参考：Yahoo《Sender Best Practices》— Have a valid forward and reverse DNS record

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/yahoo-faq-06.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
