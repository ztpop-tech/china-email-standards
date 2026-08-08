---
title: "SpamAssassin 的 sa-update 更新规则后，我自己的本地规则（local.cf）会被覆盖吗？"
source: "https://ztpop.net/kb/spamassassin-sa-update-local-cf-rules.html"
license: CC-BY 4.0
---

# SpamAssassin 的 sa-update 更新规则后，我自己的本地规则（local.cf）会被覆盖吗？

1
SpamAssassin 的 sa-update 更新规则后，我自己的本地规则（local.cf）会被覆盖吗？
▼

**结论：不会**

sa-update 只更新官方规则通道，本地自定义规则位置与之分离，因此升级与更新都不会覆盖你的配置。

**更新机制**

sa-update 默认从 updates.spamassassin.org 通道下载规则与配置（含 scores），经 GPG 签名校验后写入 /var/lib/spamassassin/<版本>/ 下的通道目录（如 updates\_spamassassin\_org）。一旦该目录存在，SpamAssassin 会优先从此目录加载全部规则。

**本地规则位置**

站点/用户自定义规则放在 /etc/mail/spamassassin/\*.cf（如 local.cf）、用户级 user\_prefs，这些文件 sa-update 从不触碰。

**注意点**

不要把 --updatedir 指向站点规则目录（如 /etc/mail/spamassassin）的子目录，否则可能干扰 local.cf 的加载（官方 FAQ 明确此坑）；如需自定义规则随更新分发，应自建 channel 并用 --channel 指定，而非混入官方目录。本地调参一律写在 local.cf。

参考：Apache SpamAssassin Wiki · RuleUpdates（sa-update 通道与 local.cf 不被覆盖）

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/spamassassin-sa-update-local-cf-rules.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
