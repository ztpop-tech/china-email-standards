---
title: "怎么用一份基线清单核对邮件系统的安全配置是否达标？"
source: "https://ztpop.net/kb/cfg-trustworthy-email-baseline-check.html"
license: CC-BY 4.0
---

# 怎么用一份基线清单核对邮件系统的安全配置是否达标？

**基线的来源与适用范围**

NIST SP 800-177 Rev.1《Trustworthy Email》是对 SP 800-45 的补充，聚焦于通过协议层的安全机制提升邮件的可信度，涵盖发件域认证、传输层保护与内容层端到端保护等方面。它面向的是邮件系统的规划、部署与运维人员，适合作为一份定期核查的基线来源，而不是一次性验收标准。

**第一组：发件域认证是否闭环**

逐项确认：SPF 记录是否存在、是否覆盖全部合法发信源、DNS 查询次数是否在上限之内；DKIM 是否对所有出站邮件签名、密钥长度是否足够、是否有轮换计划；DMARC 是否已发布、当前策略处于哪一档、聚合报告地址是否真实有人在看。判定要点在于最后一条——只发布记录而无人分析报告，认证链条并未真正闭环。

**第二组：MTA 之间的传输保护**

确认出入站是否均支持 TLS；是否已通过 MTA-STS 或 DANE 建立防降级能力，若两者都未部署，则出站实际处于机会型加密状态，需在结论中如实标注；TLS-RPT 是否已配置并被定期查看；以及是否仍启用着已知不安全的协议版本与加密套件。

**第三组：用户访问链路**

确认提交与访问是否已采用隐式 TLS、明文端口是否仍在监听；客户端是否强制校验服务器证书；认证方式是否避免了在未加密通道上传输凭据；以及是否对异常登录（异地、暴力尝试）有检测与限制。

**第四组：日志、留存与内容层**

确认投递、认证、安全事件三类日志是否齐备并集中存储；留存周期是否与策略一致、且能用磁盘上最早一条记录验证；邮件留存与到期处置是否自动执行、备份副本是否同步遵循；以及对高敏感场景是否评估过内容层的端到端保护需求。

**核查顺序与周期建议**

建议按「先看是否存在、再看是否正确、最后看是否有人维护」三层推进——多数问题不是配置写错，而是配置写完之后无人跟进，例如新增发信源未纳入 SPF、证书轮换后 TLSA 未更新、报告地址无人订阅。因此基线核查应定期重复执行，并在每次架构变更、新增发信渠道或证书轮换后追加一次针对性复核。

参考：[NIST SP 800-177 Rev. 1 Trustworthy Email](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-177r1.pdf) ｜ [NIST SP 800-45 Version 2 Guidelines on Electronic Mail Security](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-45ver2.pdf)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/cfg-trustworthy-email-baseline-check.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
