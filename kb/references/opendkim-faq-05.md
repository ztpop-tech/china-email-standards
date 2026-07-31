---
title: "如何在 OpenDMARC 中启用拒绝（RejectFailures）与历史记录（HistoryFile）？"
source: "https://ztpop.net/kb/opendkim-faq-05.html"
license: CC-BY 4.0
---

# 如何在 OpenDMARC 中启用拒绝（RejectFailures）与历史记录（HistoryFile）？

1
如何在 OpenDMARC 中启用拒绝（RejectFailures）与历史记录（HistoryFile）？
▼

**RejectFailures**

设为 true 时，凡是 DMARC 评估为失败、且发件域策略为 quarantine 或 reject 的邮件会被直接拒收。注意：当发件域策略为 p=none 时不会拒收（none 本就不要求动作），所以拒绝力度取决于对端公布的策略强度。

**HistoryFile**

把每封邮件的 DMARC 评估结果（含策略、对齐情况、动作）追加写入指定文件，相当于本地的 RUA 报表，便于在不立即拒信的前提下观察通过率与伪造情况。

**推荐节奏**

上线应先以 p=none + 开启 HistoryFile 观察若干周，确认合法流量不被误伤后，再请发件方或本域逐步收紧到 quarantine/reject，并将 RejectFailures 打开。

参考：OpenDMARC 官方文档（RejectFailures / HistoryFile）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/opendkim-faq-05.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
