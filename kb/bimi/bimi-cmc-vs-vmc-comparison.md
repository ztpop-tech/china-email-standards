---
title: "CMC 与 VMC 对比分析：颁发机构、适用范围、成本对比与应用场景"
source: "https://ztpop.net/kb/bimi-cmc-vs-vmc-comparison.html"
license: CC-BY 4.0
---

# CMC 与 VMC 对比分析：颁发机构、适用范围、成本对比与应用场景

翻译自 BIMI Group 和 CA/Browser Forum 技术规范

CMC（Common Mark Certificate，通用标志证书）是 BIMI Group 在 2025-2026 年引入的新证书类型，与传统的 VMC（Verified Mark Certificate）形成互补。两张证书的对比直接影响企业选择 BIMI 部署路径的决策。

## 颁发机构差异

VMC 由受信任的 CA（证书颁发机构，如 DigiCert、Entrust、GlobalSign、Sectigo）颁发，遵循 CA/Browser Forum 的基线要求。CA 需通过 WebTrust 审计，每年接受第三方合规检查。

CMC 则由商标注册机构或授权的注册代理颁发，无需经过 WebTrust 审计流程。CMC 的存在是为了降低商标验证的门槛，使更多中小企业能够部署 BIMI。

| 对比维度 | VMC（验证标志证书） | CMC（通用标志证书） |
| --- | --- | --- |
| 颁发机构 | 受信任 CA（WebTrust 审计） | 商标注册机构 / 授权代理 |
| 验证深度 | EV/OV 级别，含组织验证 | 基础级别，仅验证商标 |
| 适用对象 | 中大型企业、品牌方 | 中小型企业、商标持有人 |
| 成本 | $1,200-$3,500/年 | 显著低于 VMC |
| DMARC 要求 | p=quarantine 或 p=reject | p=none 也可能接受 |
| 证书格式 | .p7b / .pem | 标准 X.509 |
| WebTrust 审计 | 必需 | 不要求 |
| 接受方覆盖 | Gmail、Apple Mail、Yahoo! Mail | 部分邮箱服务商 |

## 适用范围差异

### CMC 的基础验证级别

CMC 仅验证商标的基础所有权，不验证组织合法身份。这意味着申请 CMC 只需证明商标已注册，无需提交企业注册文件、法人授权等组织验证材料。CMC 的验证周期较短（3-7 个工作日），成本也更低。

### VMC 的完整品牌验证

VMC 提供最高级别的品牌信任。所有主流邮箱服务商（Gmail、Apple Mail、Yahoo! Mail）均支持 VMC 展示的品牌标志。VMC 的 EV 级别证书还会在邮箱客户端中显示绿色的组织名称。

## 应用场景建议

* **中小企业 / 初创品牌**：从 CMC 开始部署 BIMI，成本低、门槛低，先实现标志展示
* **知名品牌 / 金融机构**：选择 EV-VMC，最高信任级别，完整的品牌保护
* **电商 / 高流量发件方**：OV-VMC 平衡成本与信任度
* **多品牌集团**：为主品牌部署 VMC，子品牌部署 CMC

## BIMI Group 路线图

BIMI Group 计划在 2027 年前实现 CMC 与 VMC 的互操作，允许使用 CMC 申请的域名逐步过渡到 VMC 级别。同时正在推动更多邮箱服务商接受 CMC 展示。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-cmc-vs-vmc-comparison.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
