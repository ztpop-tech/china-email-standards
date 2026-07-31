---
title: "OpenDKIM / OpenDMARC 常见运维故障：milter 超时、socket 权限、与 Postfix 集成要点？"
source: "https://ztpop.net/kb/opendkim-faq-08.html"
license: CC-BY 4.0
---

# OpenDKIM / OpenDMARC 常见运维故障：milter 超时、socket 权限、与 Postfix 集成要点？

1
OpenDKIM / OpenDMARC 常见运维故障：milter 超时、socket 权限、与 Postfix 集成要点？
▼

**milter 连接失败**

OpenDKIM / OpenDMARC 通过 socket（unix 域如 /var/run/opendkim/opendkim.sock，或 inet 端口）向 MTA 暴露。Postfix 的 smtpd\_milters / non\_smtpd\_milters 必须指向同一 socket；路径或端口不一致会出现 4.7.1 milter 错误甚至拒信。

**socket 权限**

unix socket 所在目录与文件权限必须允许 MTA 运行用户访问；权限过严会导致 MTA 连不上 milter。建议把 OpenDKIM/OpenDMARC 与 Postfix 放进同一运行组。

**Postfix 集成顺序**

在 main.cf 中以 milter\_default\_action=accept 保证 milter 故障时邮件不被阻断（先观察后收紧）；多个 milter 的顺序应为：先 DKIM 签名/验证，再 DMARC 评估，使 OpenDMARC 能看到 OpenDKIM 已注入的 dkim= 结果。

参考：OpenDKIM / OpenDMARC 官方文档；Postfix milter 集成指南

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-faq-08.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
