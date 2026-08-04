---
title: "NIST SP 800-63B 中防钓鱼认证（AAL）如何分级与落地？"
source: "https://ztpop.net/kb/nist-sp800-63b-aal-phishing-resistant.html"
license: CC-BY 4.0
---

# NIST SP 800-63B 中防钓鱼认证（AAL）如何分级与落地？

1
NIST SP 800-63B 中防钓鱼认证（AAL）如何分级与落地？
▼

**AAL2 与 AAL3 的分级**

NIST SP 800-63B 定义：**AAL2** 通过安全认证协议要求证明持有并控制两个不同的认证因子，需使用经批准的密码技术，但**不要求**验证者伪装抵抗；**AAL3** 基于「通过密码学协议证明持有密钥」进行认证，要求使用**硬件认证器**且至少一个密码学认证器提供验证者伪装抵抗（verifier impersonation resistance），并须抗重放（replay resistant）。

**什么是「防钓鱼」认证器**

该文件未直接使用 phishing-resistant 一词，其等效概念即 §5.2.5 的「验证者伪装抵抗」：认证器输出即使被攻击者骗取也无法在其冒充验证者/依赖方时复用。§8.2 表 8-2 在缓解「Phishing or Pharming」一行明确指出——应使用提供验证者伪装抵抗的认证器。换言之，具备该特性的硬件密钥（如 FIDO/U2F 类多因子密码设备）即 SP 800-63B 所指的防钓鱼认证器，仅 AAL3 强制。

**硬件与 FIPS 140 要求**

用于在 AAL3 认证的多因子认证器**须为硬件密码模块**，并通过 FIPS 140 二级（整体）及以上、且至少达到 FIPS 140 三级物理安全的验证。这为邮件系统选择防钓鱼 MFA（如基于公钥加密的硬件密钥）提供了合规基线。

**邮件不得用于带外认证**

§5.1.3.1 明确规定：不能证明持有特定设备的带外方式（如 VoIP 或**电子邮件**）不得用于带外认证。因此邮件本身不可作为第二因子的传递通道，高安全场景应改用防钓鱼硬件密钥或 PKI，避免把一次性口令发到可能被攻陷的邮箱。

参考：NIST SP 800-63B《数字身份指南：认证与生命周期管理》(https://pages.nist.gov/800-63-3/sp800-63b.html；DOI 10.6028/NIST.SP.800-63B)，§4.2/§4.3、§5.2.5、§8.2 表8-2、§5.1.3.1

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/nist-sp800-63b-aal-phishing-resistant.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
