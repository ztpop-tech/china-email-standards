---
title: "怎样排查被滥用的 OAuth 授权应用，并判断哪些邮件数据可能已被读取？"
source: "https://ztpop.net/kb/oauth-app-grant-abuse-forensic-review.html"
license: CC-BY 4.0
---

# 怎样排查被滥用的 OAuth 授权应用，并判断哪些邮件数据可能已被读取？

1
怎样排查被滥用的 OAuth 授权应用，并判断哪些邮件数据可能已被读取？
▼

**先理解这条访问通道的性质**

OAuth 授权与口令登录是两条平行的访问通道，这一点在排查时必须先想清楚，否则处置动作会做错方向。

RFC 6749 定义的授权框架中，用户（资源所有者）向应用（客户端）授予的是一个**与口令无关的独立许可**。应用凭此许可换取 access token，之后每次访问只出示令牌。RFC 6749 §3.3 定义的 `scope` 参数决定了这个许可的边界——它能读什么、能写什么、能不能代为发信。

由此得到三条直接影响处置的性质：

* **改口令不影响它。**令牌不携带口令，也不因口令变更而自动失效（是否失效取决于授权服务器的策略实现）。
* **它是用户自己点「同意」授予的。**因此在日志里表现为完全合法的授权流程，没有认证失败，没有异常登录，**传统的登录异常检测对它几乎完全无效**。
* **它可以在后台持续运行。**只要 refresh token 有效，应用可以在用户完全无感的情况下长期读取邮件。

RFC 6819 系统梳理了 OAuth 2.0 的威胁模型，RFC 9700 在此基础上给出了当前的安全最佳实践。**对防守方而言，这两份文档的价值在于：它们说明了哪些环节是设计上就需要额外控制的，从而指出了排查的重点位置。**

**枚举与分类：把全部授权摊开看**

排查的第一步是拿到完整清单。这里有一个容易踩的坑：**授权分为用户级同意与管理员级同意（面向整个组织），两者在管理界面中的位置往往不同，必须分别枚举。**

1. **枚举组织内全部已授权应用**，记录：应用标识、应用名称、发布者、授权类型（用户级／管理员级）、授权范围、授权用户数、首次授权时间、最近使用时间。
2. **按范围（scope）分类。**把涉及邮件读取、邮件发送、邮箱设置修改、目录读取的授权单独挑出来。**这几类是影响面判定的核心，其余可以先放一边。**
3. **按授权时间与时间线交叉。**授权时间落在暴露窗口内的，优先核查。
4. **按发布者核验状态分类。**多数平台会标记发布者是否经过核验。**未核验的发布者不等于恶意，但它应当排在核查队列的前面。**
5. **识别「用户数异常」的模式。**一个只被极少数用户授权、却拥有宽泛邮件读取范围的应用，值得单独看一眼；反过来，短时间内被大量用户集中授权的应用同样值得关注。

Microsoft Learn 的《Detect and remediate illicit consent grants》一文给出了面向非法同意授权的检测与处置路径，可作为枚举与判定的操作参照。

**怎样读懂 scope，据此判定「能看到什么」**

影响面判定的核心问题是：**这个授权到底允许应用访问哪些数据？**答案完全写在 scope 里，但需要正确解读。

RFC 6749 §3.3 规定，授权服务器可以完全或部分忽略客户端请求的范围，也可以基于自身策略或资源所有者的指示给出不同的范围；若最终授予的范围与请求不同，**授权服务器必须在响应中包含实际授予的 scope**。

**这条规范在取证中的含义很实际：不能只看应用「请求了什么」，必须查「实际授予了什么」。**两者可能不同，而只有后者决定真实的访问边界。

解读时按下列维度拆解：

* **读还是写。**只读范围意味着数据泄露风险，可写范围额外意味着邮件可能被篡改、删除或代为发出。
* **作用于本人邮箱还是全组织。**这是影响面上最大的分水岭。**组织级的邮件读取范围意味着影响面是全体用户，而不只是点击同意的那一个人。**
* **是否包含离线访问。**包含离线访问意味着可获得 refresh token，从而具备长期持续访问能力。
* **是否涉及邮箱配置。**能修改邮箱设置的范围，意味着应用本身就可以创建转发规则。

把 scope 的解读结论写成一句话：**「该应用自某时刻起，具备对某范围内邮件数据的某种访问能力，且该能力持续到吊销为止。」**这句话就是影响面评估的基础。

**吊销与清理的完整动作**

1. **先取证再吊销。**导出授权详情、同意记录、令牌颁发记录与应用的 API 调用审计。**吊销之后，部分平台会连带清除相关记录，届时无法回溯授予了什么范围。**
2. **撤销授权同意。**用户级同意与管理员级同意分别撤销，两者不互相覆盖。
3. **吊销令牌。**RFC 7009 定义了吊销端点：请求携带 `token` 参数，可选携带 `token_type_hint`；成功吊销返回 HTTP 200，而对本就无效的令牌同样返回 200。**优先吊销 refresh token**——按 RFC 7009，若授权服务器支持吊销 access token，则吊销 refresh token 时应当同时使基于同一授权许可签发的全部 access token 失效。
4. **禁用或删除应用注册。**若应用注册在本组织租户内，仅撤销同意不够，还应处理注册本身。
5. **检查该应用是否留下了其他持久化。**具备邮箱配置写权限的应用可能已创建转发规则或委托权限，必须联动排查。**只吊销授权而不查规则，等于清了入口留了后门。**
6. **覆盖最长令牌有效期后复核。**自包含 access token 在自然过期前仍可能被资源服务器接受，这是必须承认的残留窗口。

**从单次处置走向常态控制**

* **收紧用户同意策略。**把「任意用户可授权任意应用访问邮件」改为需要管理员审批，是消除这一整类风险最直接的手段。CISA 的 SCuBA 项目发布了面向主流云办公平台的安全配置基线，其中涉及应用授权与同意管控的条目可作为配置对照。
* **建立应用白名单与审批流程。**审批时重点看 scope 而不是应用名称与图标。**名称和图标是可以随便起的，scope 不能。**
* **对新增高权限授权设置告警。**尤其是涉及邮件读取范围的管理员级同意。
* **定期复核存量授权。**把长期未使用但仍持有宽泛范围的授权清理掉。RFC 9700 强调令牌生命周期与最小权限，存量清理正是这一原则的落地。
* **关注原生应用的特殊性。**RFC 8252 说明了原生应用在 OAuth 流程中的特点与相应要求，涉及移动端与桌面端客户端的场景需要按其建议单独评估。
* **把这一项写进事件响应剧本。**NIST SP 800-61 Rev. 3 强调响应能力需要预先准备。**「检查 OAuth 授权」应当与「检查邮箱规则」并列，成为每一次邮箱失陷处置的固定动作，而不是想起来才做。**

参考：RFC 6749《The OAuth 2.0 Authorization Framework》§3.3 Access Token Scope、§10 Security Considerations，D. Hardt 编，2012 年 10 月，Standards Track，DOI 10.17487/RFC6749，https://www.rfc-editor.org/rfc/rfc6749.html ；RFC 6819《OAuth 2.0 Threat Model and Security Considerations》，T. Lodderstedt 编、M. McGloin、P. Hunt，2013 年 1 月，https://www.rfc-editor.org/rfc/rfc6819.html ；RFC 9700《Best Current Practice for OAuth 2.0 Security》，T. Lodderstedt、J. Bradley、A. Labunets、D. Fett，2025 年 1 月，BCP 240，https://www.rfc-editor.org/rfc/rfc9700.html ；RFC 7009《OAuth 2.0 Token Revocation》，T. Lodderstedt 编、S. Dronia、M. Scurtescu，2013 年 8 月，https://www.rfc-editor.org/rfc/rfc7009.html ；RFC 8252《OAuth 2.0 for Native Apps》，W. Denniss、J. Bradley，2017 年 10 月，BCP 212，https://www.rfc-editor.org/rfc/rfc8252.html ；Microsoft Learn《Detect and remediate illicit consent grants》，https://learn.microsoft.com/en-us/defender-office-365/detect-and-remediate-illicit-consent-grants ；Microsoft Learn 审计解决方案文档，https://learn.microsoft.com/en-us/purview/audit-solutions-overview ；Google Workspace 管理员帮助中心，https://support.google.com/a/ ；CISA《Secure Cloud Business Applications (SCuBA) Project》，https://www.cisa.gov/scuba ；NIST SP 800-61 Rev. 3，https://csrc.nist.gov/pubs/sp/800/61/r3/final

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/oauth-app-grant-abuse-forensic-review.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
