---
title: "国密 TLS 证书怎么在邮件服务上部署？双证书是什么意思？"
source: "https://ztpop.net/kb/xc-guomi-tls-cert-deployment.html"
license: CC-BY 4.0
---

# 国密 TLS 证书怎么在邮件服务上部署？双证书是什么意思？

**为什么是「双证书」：签名与加密职责分离**

TLCP（依据 **GB/T 38636-2020《信息安全技术 传输层密码协议(TLCP)》**）要求服务端同时具备**签名证书**与**加密证书**两张证书：

* **签名证书**：私钥由使用者自行产生并独占，用于身份鉴别与握手签名，保证不可否认。
* **加密证书**：其密钥对通常由密钥管理机构产生并托管，用于密钥交换，以便在合规监管与数据恢复场景下具备可控性。

**这与国际 TLS 的单证书模式是结构性差异**，也是部署时最容易配错的地方——把两张证书配反会导致握手失败或不可否认性丧失。

**两条技术路线怎么选**

**路线 A：TLCP。**面向国内合规评价（密评）时的主流选择，双证书体系，与既有国密基础设施衔接顺畅。

**路线 B：TLS 1.3 国密套件。**RFC 8998 ShangMi (SM) Cipher Suites for TLS 1.3 在 RFC 8446 The Transport Layer Security (TLS) Protocol Version 1.3 的框架内注册了基于 SM 系列算法的套件（对称侧为 SM4-GCM 与 SM4-CCM，杂凑侧为 SM3），可与国际生态在同一协议版本下共存。

**选择判定：**面向内部与自有客户端、且需通过密评的链路，优先 TLCP；面向需要与广泛外部生态互通的链路，TLS 1.3 国密套件的兼容成本更低。**两者不是二选一，同一系统的不同链路可分别采用。**

**邮件服务的部署顺序：从可控端开始**

邮件的端口多、对端多，务必分批推进，顺序建议为：

1. **Web 访问入口（443）**：对端是浏览器/自有客户端，最可控，先行验证证书链与兼容性。
2. **客户端提交与访问端口（465、587、993、995）**：需确认客户端支持情况，不支持的先保留国际算法双栈。
3. **内部服务器间链路**：两端均自有，可强制。
4. **跨域投递（25）**：最后处理，且必须允许协商到国际算法，禁止回退明文。

**双栈并存：同端口协商 vs 分端口部署**

过渡期几乎一定是双栈。两种做法：

* **同端口按客户端能力协商**：服务端同时装载国密与国际证书，依据客户端 ClientHello 的算法能力选择。**对用户无感，是首选做法。**
* **分端口部署**：国密与国际服务分列不同端口。实现简单，但需要用户端改配置，且会增加边界端口数量（与等保的端口最小化要求相冲突）。

**判定条件：**若能实现同端口协商，就不要分端口——分端口在测评时会额外产生解释成本。

**证书链与吊销状态：容易被忽略的两项**

证书本身合规还不够，RFC 5280 Internet X.509 Public Key Infrastructure Certificate and CRL Profile 定义的链路校验同样要满足：

* **中间证书必须完整下发**：缺失中间证书是最常见的「浏览器能开、邮件客户端报错」原因——很多邮件客户端不会自动补链。
* **吊销状态可校验**：应支持 RFC 6960 X.509 Internet PKI Online Certificate Status Protocol (OCSP) 定义的 OCSP 查询；对邮件服务器间链路，建议启用装订（stapling）以避免对端查询失败导致的握手中断。
* **主机名校验规则**：邮件相关协议的服务端身份校验规程见 RFC 7817 Updated TLS Server Identity Check Procedure for Email-Related Protocols，证书中的名称必须与客户端实际连接的主机名一致，不能只配主域名。

**上线前的验证清单**

* 对每个端口实际发起握手，记录协议版本、套件标识、证书类型（签名/加密）。
* 确认无明文回退路径，且弱算法与旧协议版本已禁用。
* 用不带本地信任锚的干净环境验证证书链完整性。
* 把证书有效期纳入监控，**到期前留出足够更换窗口——双证书体系意味着要监控的证书数量翻倍。**
* 记录基线协商结果，后续每次变更都与基线比对，防止悄然降级。

国际侧的 TLS 配置通用建议可参考 NIST SP 800-52 Rev.2 Guidelines for TLS Implementations。

参考：[RFC 8998 ShangMi (SM) Cipher Suites for TLS 1.3](https://www.rfc-editor.org/rfc/rfc8998.html) ｜ [RFC 8446 The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446.html) ｜ [RFC 5280 Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280.html) ｜ [RFC 6960 X.509 Internet PKI Online Certificate Status Protocol (OCSP)](https://www.rfc-editor.org/rfc/rfc6960.html) ｜ [RFC 7817 Updated TLS Server Identity Check Procedure for Email-Related Protocols](https://www.rfc-editor.org/rfc/rfc7817.html) ｜ [NIST SP 800-52 Rev.2 Guidelines for TLS Implementations](https://csrc.nist.gov/pubs/sp/800/52/r2/final) ｜ [国家标准全文公开系统（GB/T 标准检索）](https://openstd.samr.gov.cn/bzgk/gb/)

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/xc-guomi-tls-cert-deployment.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
