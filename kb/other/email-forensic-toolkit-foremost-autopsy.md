---
title: "邮件取证常用工具（Foremost/Autopsy 等）有哪些实用方法？"
source: "https://ztpop.net/kb/email-forensic-toolkit-foremost-autopsy.html"
license: CC-BY 4.0
---

# 邮件取证常用工具（Foremost/Autopsy 等）有哪些实用方法？

1
邮件取证常用工具（Foremost/Autopsy 等）有哪些实用方法？
▼

**磁盘级恢复（carving）**

当邮件已被删除或存储损坏时，用文件雕刻从原始镜像中提取残留数据：

* **Foremost**：基于文件头/尾特征（如 EML 的 `Received:`、`From:` 起始）恢复零散邮件片段；
* **The Sleuth Kit (TSK)** 与 **Autopsy**：图形化取证平台，可做时间线分析、关键字搜索、已删文件恢复，并导出证据包。

**邮箱格式解析**

不同客户端的存储格式不同，需专用解析：

* **PST/OST**（Outlook）：用 `libpff`/readpst 提取邮件、附件与目录；
* **mbox**（Unix/Thunderbird）：逐封以 `From`  分隔，可直接文本解析；
* **EML**：单封 RFC 822 明文，便于用脚本批量抽取 Received/Authentication-Results 做溯源。

**取证工作流**

标准流程：①对磁盘/镜像做哈希保全（md5/sha1）保证证据不可辩驳；②用 Autopsy 建立时间线与关键字命中；③对 Outlook 数据用 readpst 转 EML；④用脚本提取 Received/ARC/Authentication-Results 信头还原传输链；⑤交叉比对 DNSBL 与 SPF/DKIM 结论形成报告。注意遵守取证合规与授权边界。

参考：The Sleuth Kit / Autopsy 文档、Foremost 使用说明、libpff/readpst（PST 解析）、RFC 822/5322 邮件格式。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-forensic-toolkit-foremost-autopsy.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
