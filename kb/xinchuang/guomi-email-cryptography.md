---
title: "国密密码学在邮件系统中的应用 — SM2/SM3/SM4/TLCP 算法体系与工程实践"
source: "https://ztpop.net/kb/guomi-email-cryptography.html"
license: CC-BY 4.0
---

# 国密密码学在邮件系统中的应用 — SM2/SM3/SM4/TLCP 算法体系与工程实践

## 一、国密算法体系总览：为什么邮件系统需要"自己的轮子"

密码算法是互联网安全的基石。邮件系统作为组织信息流转的核心通道，其传输加密和身份认证长期依赖国际算法体系——RSA/ECDSA 做签名、AES 做对称加密、SHA-256 做哈希。但在合规驱动和供应链可控的双重压力下，越来越多组织要求在邮件基础设施中部署国产密码算法，形成一条从 SMTP 握手到本地存储的全链路国密替代路径。

国家密码管理局发布的 SM 系列商用密码算法构成了一个完整的密码学工具箱，覆盖了非对称加密、哈希摘要、对称分组加密和基于标识的密码体系四个维度：

一、国密算法体系总览：为什么邮件系统需要"自己的轮子"

| 算法 | 类型 | 核心参数 | 对标国际算法 | 标准编号 | 在邮件系统中的应用 |
| --- | --- | --- | --- | --- | --- |
| **SM2** | 椭圆曲线公钥密码 | 256 bit 素数域曲线 | ECDSA P-256 / ECDH | GB/T 32918 | TLS 证书签名与密钥交换、S/MIME 签名 |
| **SM3** | 密码杂凑（哈希） | 256 bit 输出 | SHA-256 | GB/T 32905 | 证书指纹、DKIM 签名哈希、数据完整性校验 |
| **SM4** | 分组对称加密 | 128 bit 密钥/分组 | AES-128 | GB/T 32907 | TLS 会话对称加密、邮件存储加密 |
| **SM9** | 基于标识的密码 (IBE) | 256 bit BN 曲线，双线性对 | RSA-OAEP (近似，机制不同) | GM/T 0044 | 免证书邮件端到端加密、密钥分发 |

SM2 基于 256 位椭圆曲线，安全强度等价于 3072 位 RSA，但密钥更短、签名速度更快。SM3 在 SHA-256 基础上做了结构加强，输出同为 256 位。SM4 采用 32 轮 Feistel 结构，分组和密钥均为 128 位，对称加密效率与 AES-128 处于同一量级。SM9 是整个体系中最独特的存在——它不依赖数字证书，直接用邮件地址或用户标识作为公钥，从根本上改变了公钥分发范式。

值得注意的是，SM1 和 SM7 算法仍为未公开算法，仅在硬件密码芯片中以 IP 核形式存在，不在本文的软件部署讨论范围内。

## 二、SM2 椭圆曲线密码：邮件 TLS 的数学引擎

SM2 包含三个子标准：SM2-1 数字签名算法、SM2-2 密钥交换协议、SM2-3 公钥加密算法。在邮件系统中，SM2-1 用于 TLS 证书的身份签名，SM2-2 用于握手阶段的密钥协商（对应 TLS 中 ECDHE 的角色）。

### 2.1 与 ECDSA P-256 的技术差异

虽然 SM2 和 NIST P-256 同为 256 位椭圆曲线，但两者在多处存在关键差异，不能互换使用：

* **曲线参数不同：**
  SM2 的推荐曲线 sm2p256v1 使用了不同的素数域 p 和基点的选取方式。即使位数相同，两条曲线的点运算结果完全不同。
* **签名流程不同：**
  SM2 签名算法在计算消息摘要时需要将签名者的标识（Z\_A 值）和待签名消息拼接后再做 SM3 哈希，这个"签名者标识"的加入是 SM2 与 ECDSA 最显著的区别——它天然绑定了签名方的身份。
* **ASN.1 编码不同：**
  SM2 签名的 DER 编码长度约 70-72 字节，而 ECDSA P-256 签名的 DER 编码通常为 68-71 字节。
* **密钥交换流程不同：**
  SM2-2 的密钥交换协议是专门设计的，不同于标准的 ECDH。

### 2.2 SM2 密钥对生成

使用 Tongsuo（原 BabaSSL）生成 SM2 密钥对：

```
# 生成 SM2 私钥（PEM 格式）
tongsuo ecparam -genkey -name SM2 -out sm2_private.pem

# 提取公钥
tongsuo ec -in sm2_private.pem -pubout -out sm2_public.pem

# 查看密钥参数
tongsuo ec -in sm2_private.pem -text -noout
```

私钥文件为 PEM 格式的 EC PRIVATE KEY，内部使用 SM2 OID (1.2.156.10197.1.301) 标记曲线类型。

### 2.3 SM2 自签名 CA 证书

构建一个完整的国密 PKI 体系首先需要自签名 CA 根证书：

```
# 创建 CA 目录结构
mkdir -p demoCA/{certs,crl,newcerts,private}
touch demoCA/index.txt
echo "01" > demoCA/serial

# 生成 CA 私钥
tongsuo ecparam -genkey -name SM2 -out demoCA/private/cakey.pem

# 生成 CA 证书请求（使用 SM3 哈希）
tongsuo req -new -sm3 \
  -key demoCA/private/cakey.pem \
  -out ca.csr \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=Mail System/CN=Root CA"

# 自签名 CA 根证书（有效期10年）
tongsuo req -x509 -sm3 -days 3650 \
  -key demoCA/private/cakey.pem \
  -in ca.csr \
  -out demoCA/cacert.pem

# 验证证书
tongsuo x509 -in demoCA/cacert.pem -text -noout | head -20
```

此时会输出证书的签名算法为
`sm2sign-with-sm3`
，确认国密链路已生效。

## 三、SM3 哈希与 SM4 对称加密：数据的完整性锚点和机密性保障

### 3.1 SM3：不只是"国产 SHA-256"

SM3 的消息分组长度为 512 位，输出摘要 256 位，基本结构与 SHA-256 类似——均为 Merkle-Damgård 结构的迭代哈希。但 SM3 在消息扩展和压缩函数上做出了特定的设计改动：

* 消息扩展阶段增加了额外的扩散轮次（扩展到 132 个字，SHA-256 为 64 个字）
* 压缩函数中的布尔函数和置换采用了不同设计
* 常量选择遵循了不同规则

这些改动使得 SM3 在抗碰撞和抗原像攻击方面具备与国际 Hash 函数至少同等的安全强度。在邮件系统中，SM3 的应用场景包括：

* **证书指纹：**
  SM2 证书的签名哈希（替代 SHA-256）
* **DKIM 签名：**
  邮件头签名的哈希算法（需客户端支持）
* **数据完整性：**
  邮件正文和附件的完整性校验码

命令行验证 SM3 哈希：

```
# 计算文件的 SM3 哈希
tongsuo dgst -sm3 /etc/postfix/main.cf

# 输出示例：
# SM3(/etc/postfix/main.cf)= a1b2c3d4e5f6...（64 个十六进制字符）
```

### 3.2 SM4：邮件传输层的对称加密主力

SM4 是国密体系中对称加密的主算法，分组长度和密钥长度均为 128 位，采用 32 轮非平衡 Feistel 结构。在性能方面，SM4 在 x86\_64 平台上配合 AES-NI 不具备原生加速优势（不同于 AES），但 Tongsuo 对 SM4 做了汇编级优化，实际吞吐量可达数百 MB/s，足以覆盖邮件服务器的 TLS 加密需求。

SM4 支持多种工作模式：

3.2 SM4：邮件传输层的对称加密主力

| 模式 | 说明 | 适用场景 | TLS 套件中标识 |
| --- | --- | --- | --- |
| SM4-CBC | 密码块链接模式，需填充和 IV | 兼容性优先场景 | TLS\_SM4\_GCM\_SM3 或 ECC\_SM4\_CBC\_SM3 |
| SM4-GCM | Galois/Counter 模式，自带认证加密 | 推荐模式，性能更好 | TLS\_SM4\_GCM\_SM3 或 ECC\_SM4\_GCM\_SM3 |
| SM4-CTR | 计数器模式，可并行加解密 | 流式处理场景 | 在 TLCP 1.1 中支持 |

在实际部署中，应优先使用 SM4-GCM 模式——它不仅提供了加密，还内建了完整性认证（AEAD），避免了 CBC 模式中 padding oracle 类攻击的风险。

## 四、TLCP（GB/T 38636）：国密传输层协议的完整拼图

如果说 SM2/SM3/SM4 是三块积木，那么 TLCP（Transport Layer Cryptography Protocol，传输层密码协议，即 GB/T 38636-2020）就是把这些积木搭建成一个完整 TLS 栈的图纸。

### 4.1 TLCP 与 TLS 1.2 的核心差异

4.1 TLCP 与 TLS 1.2 的核心差异

| 维度 | TLS 1.2（RFC 5246） | TLCP（GB/T 38636） |
| --- | --- | --- |
| 签名算法 | RSA / ECDSA / EdDSA | SM2 签名（sm2sig\_sm3） |
| 密钥交换 | RSA / DHE / ECDHE | ECC-SM2 / ECDHE-SM2 |
| 对称加密 | AES-GCM / AES-CBC / ChaCha20 | SM4-GCM / SM4-CBC |
| 哈希算法 | SHA-256 / SHA-384 | SM3 |
| 证书体系 | 单证书（一个证书同时用于签名和密钥交换） | **双证书** （签名证书 + 加密证书分离） |
| 协议版本标识 | {3,3} (TLS 1.2) | {1,1} (TLCP 1.1) |

### 4.2 双证书体系详解

TLCP 最显著的特征是双证书体系——这也是它与标准 TLS 握手最大的区别。在 TLCP 握手过程中，服务端需要同时提供两份 SM2 证书：

* **签名证书（Sign Certificate）：**
  用于 ServerKeyExchange 中对密钥交换参数进行签名。CA 在为签名证书签发时，keyUsage 中标记 digitalSignature。
* **加密证书（Encrypt Certificate）：**
  用于密钥交换——客户端使用加密证书中的公钥加密 Pre-Master Secret 并发送给服务端。CA 签发时 keyUsage 中标记 keyEncipherment。

这种设计源于国密规范对密钥用途的严格分离：同一把密钥不得同时用于签名和加密。从安全角度看，这避免了因签名操作意外泄露密钥材料从而影响加密安全性的风险——在标准 TLS 中，一枚 RSA 证书同时承担两种角色正是被逐步淘汰的原因之一。

### 4.3 TLCP 握手流程（简化）

```
Client                          Server
  |                               |
  |--- ClientHello -------------->|  (1) 客户端随机数, 密码套件列表
  |                               |     支持: ECC_SM4_GCM_SM3, ECDHE_SM4_GCM_SM3
  |                               |
  |
<
-- ServerHello --------------|  (2) 服务端随机数, 选定密码套件
  |
<
-- Certificate --------------|  (3) 签名证书 + 加密证书（双证书）
  |
<
-- ServerKeyExchange --------|  (4) 服务端用签名证书私钥对密钥参数签名
  |
<
-- ServerHelloDone ----------|  (5) 握手第一阶段结束
  |                               |
  |--- ClientKeyExchange ------->|  (6) 客户端用加密证书公钥加密 Pre-Master
  |--- ChangeCipherSpec --------->|  (7) 切换至协商的加密参数
  |--- Finished ----------------->|  (8) 握手完成验证
  |                               |
  |
<
-- ChangeCipherSpec ---------|  (9)
  |
<
-- Finished -----------------|  (10)
  |                               |
  |==== 加密数据传输（SM4-GCM）====|
  |                               |
```

在第(4)步中，ServerKeyExchange 的 signed\_params 字段包含了对客户端随机数、服务端随机数和服务端加密证书的 SM2 签名。客户端在第(6)步验证该签名，确保密钥交换参数没有被篡改——这是整个 TLCP 安全性的核心保障。

### 4.4 国密密码套件

TLCP 定义了两类主要密码套件，对应两种密钥交换方式：

4.4 国密密码套件

| 密码套件 | 密钥交换 | 对称加密 | 哈希 | 前向安全性 |
| --- | --- | --- | --- | --- |
| ECC\_SM4\_CBC\_SM3 | ECC-SM2（静态） | SM4-CBC | SM3 | ❌ 无 |
| ECC\_SM4\_GCM\_SM3 | ECC-SM2（静态） | SM4-GCM | SM3 | ❌ 无 |
| ECDHE\_SM4\_CBC\_SM3 | ECDHE-SM2（临时） | SM4-CBC | SM3 | ✅ 有 |
| ECDHE\_SM4\_GCM\_SM3 | ECDHE-SM2（临时） | SM4-GCM | SM3 | ✅ 有 |

在条件允许的情况下，应优先选择 ECDHE\_SM4\_GCM\_SM3——它不仅提供前向安全性（即使服务端长期私钥泄露，历史会话也无法被解密），还使用 AEAD 模式（GCM）避免了 CBC 模式的固有缺陷。ECC-SM2 静态密钥交换方式仅应在客户端不支持临时密钥协商的遗留场景中使用。

## 五、RFC 8998：国密走进 TLS 1.3

2021 年 3 月，IETF 发布了 RFC 8998 ——《ShangMi (SM) Cipher Suites for TLS 1.3》。这是国密算法首次以独立 RFC 的形式进入 IETF 标准体系，意味着 SM2/SM3/SM4 可以在 TLS 1.3 框架内与其他国际密码套件共存，而不再局限于 TLCP 协议。

RFC 8998 定义了以下核心标识：

五、RFC 8998：国密走进 TLS 1.3

| 标识符 | 值 | 说明 |
| --- | --- | --- |
| TLS\_SM4\_GCM\_SM3 | {0x00, 0xC6} | TLS 1.3 国密切勿套件，SM4-GCM 加密 + SM3 哈希 |
| TLS\_SM4\_CCM\_SM3 | {0x00, 0xC7} | SM4-CCM 模式（资源受限设备） |
| SM2 曲线 ID | 41 (0x29) | TLS 1.3 supported\_groups 扩展中的 SM2 椭圆曲线 |
| sm2sig\_sm3 | 0x0708 | SignatureScheme：SM2 签名 + SM3 哈希 |

在 TLS 1.3 中使用 RFC 8998 国密切勿套件时，握手流程遵循标准 TLS 1.3 的 1-RTT 设计，但在以下环节使用国密算法：

* **supported\_groups 扩展：**
  客户端声明支持 SM2 曲线（ID=41）
* **signature\_algorithms 扩展：**
  声明 sm2sig\_sm3 (0x0708)
* **CertificateVerify：**
  使用 SM2 签名 + SM3 哈希
* **密钥协商：**
  使用 SM2 椭圆曲线完成 ECDHE
* **对称加密：**
  使用 SM4-GCM（AEAD）
* **HMAC/HKDF 中的哈希：**
  使用 SM3

使用 curl 测试 RFC 8998 国密连接的示例（需编译支持 Tongsuo 的 curl）：

```
# 使用 curl 与支持国密的服务器建立 TLS 1.3 连接
curl --curves SM2 \
     --ciphers TLS_SM4_GCM_SM3 \
     --tlsv1.3 \
     https://mail.example.com:443/

# 查看协商后的密码套件
curl -v --curves SM2 https://mail.example.com/ 2>&1 | grep -i cipher
```

## 六、SM9 IBE：邮件加密的范式跃迁

SM9 是国密体系中最具创新性的算法。它属于基于标识的密码（Identity-Based Cryptography, IBC），核心特征是用用户标识（如邮件地址）直接作为公钥，从而免去了传统 PKI 中证书颁发、分发、吊销的整套流程。

### 6.1 IBE 如何改变邮件加密

传统 S/MIME 或 PGP 邮件加密面临的核心困难不是算法强度，而是密钥分发——发送方需要首先获取接收方的公钥证书，验证证书链，然后用公钥加密。这个"预先获取"的门槛在现实中阻断了大量邮件加密的实际使用。

SM9 IBE 从根本上消除了这个门槛：

```
传统 PKI 邮件加密流程：
  发送方 → 查询 LDAP/密钥服务器 → 获取接收方证书 → 验证 CA 链 → 加密发送
  （需要收方提前生成密钥对并发布证书）

SM9 IBE 邮件加密流程：
  发送方 → 直接用 "user@domain.com" 作为公钥 → 加密发送
  （无需任何预查询，邮件地址即公钥）
```

### 6.2 SM9 的工作机制

SM9 基于双线性对（Bilinear Pairing）在椭圆曲线上构造，核心角色包括：

* **密钥生成中心（KGC）：**
  持有系统主私钥（Master Secret），负责根据用户标识为用户生成私钥。用户通过安全信道从 KGC 获取自己的私钥。
* **用户标识：**
  邮件地址、手机号等可作为公钥的任意字符串。
* **加解密：**
  发送方使用接收方的标识（如 mailto:user@example.com）和系统主公钥直接加密；接收方使用从 KGC 获得的私钥解密。

在邮件加密场景中，SM9 带来的工程收益是显著的：管理员不再需要维护用户证书库、处理证书过期续签、操作 CRL 或 OCSP 响应器。新增用户时，只需为其生成一次私钥即可。不过 SM9 也存在密钥托管（Key Escrow）问题——KGC 可以为任何用户生成私钥，因此 KGC 本身的安全和可信程度是整个体系的单点信任根。

### 6.3 与国际 IBE 方案对比

6.3 与国际 IBE 方案对比

| 方案 | 标准 | 基底曲线 | 配对类型 | 安全级别 |
| --- | --- | --- | --- | --- |
| SM9 | GM/T 0044-2016 | BN 曲线 (256 bit) | Ate 配对 | ≈ RSA 3072 |
| Boneh-Franklin IBE | RFC 5091 | 超奇异曲线 | Weil/Tate 配对 | ≈ RSA 2048 |
| Boneh-Boyen IBE | 学术方案 | MNT 曲线 | Weil 配对 | ≈ RSA 2048 |

SM9 的安全强度设定显著高于传统 IBE 方案，其选择的 BN 曲线在 256 位安全级别下与 RSA 3072 位相当。

## 七、运维实战：从 Tongsuo 编译到邮件服务器全链路配置

### 7.1 Tongsuo 编译安装

Tongsuo（铜锁）是 OpenSSL 的国密分支，前身为 BabaSSL，2022 年更名。它同时支持国密和标准 TLS，是邮件服务器国密化的首选密码库。

```
# 下载 Tongsuo 8.4.0（稳定版）
wget https://github.com/Tongsuo-Project/Tongsuo/archive/refs/tags/8.4.0.tar.gz
tar -xzf 8.4.0.tar.gz
cd Tongsuo-8.4.0

# 配置编译选项
./config --prefix=/opt/tongsuo \
         --openssldir=/opt/tongsuo/ssl \
         enable-ntls \
         enable-sm2 \
         enable-sm3 \
         enable-sm4

# 编译（-j 参数根据 CPU 核心数调整）
make -j$(nproc)

# 安装
make install

# 配置环境变量
echo 'export PATH=/opt/tongsuo/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/opt/tongsuo/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 验证安装
tongsuo version
# 输出应包含：Tongsuo 8.4.0
```

关键编译选项说明：

* `enable-ntls`
  ：启用 NTLS（国密 TLS，即 TLCP 实现）
* `enable-sm2/sm3/sm4`
  ：显式启用各 SM 算法
* `--prefix`
  ：安装到独立目录，避免与系统 OpenSSL 冲突

### 7.2 为邮件服务器签发 SM2 双证书

使用 Tongsuo 和自建 CA 为邮件服务器颁发 TLCP 双证书（签名证书 + 加密证书）：

```
# === 1. 生成签名密钥对 ===
tongsuo ecparam -genkey -name SM2 -out mail_sign.key

# === 2. 生成加密密钥对 ===
tongsuo ecparam -genkey -name SM2 -out mail_enc.key

# === 3. 生成签名证书请求 ===
tongsuo req -new -sm3 \
  -key mail_sign.key \
  -out mail_sign.csr \
  -subj "/C=CN/ST=Shanghai/O=Mail System/CN=mail.example.com"

# === 4. 生成加密证书请求 ===
tongsuo req -new -sm3 \
  -key mail_enc.key \
  -out mail_enc.csr \
  -subj "/C=CN/ST=Shanghai/O=Mail System/CN=mail.example.com"

# === 5. CA 签发签名证书（标记为签名用途） ===
tongsuo ca -md sm3 \
  -keyfile demoCA/private/cakey.pem \
  -cert demoCA/cacert.pem \
  -in mail_sign.csr \
  -out mail_sign.crt \
  -extensions v3_sign \
  -days 3650

# === 6. CA 签发加密证书（标记为加密用途） ===
tongsuo ca -md sm3 \
  -keyfile demoCA/private/cakey.pem \
  -cert demoCA/cacert.pem \
  -in mail_enc.csr \
  -out mail_enc.crt \
  -extensions v3_enc \
  -days 3650

# === 7. 验证证书 ===
tongsuo x509 -in mail_sign.crt -text -noout | grep -E "Signature|Public Key"
tongsuo verify -CAfile demoCA/cacert.pem mail_sign.crt mail_enc.crt
```

### 7.3 Postfix TLS 国密配置

Postfix 本身不直接调用 Tongsuo，而是通过系统的 OpenSSL/Tongsuo 动态链接库工作。因此需要确保 Postfix 编译时链接的是 Tongsuo 的 libssl 和 libcrypto：

```
# 编译 Postfix 时指向 Tongsuo
make -f Makefile.init makefiles \
  CCARGS="-DUSE_TLS -I/opt/tongsuo/include" \
  AUXLIBS="-L/opt/tongsuo/lib64 -lssl -lcrypto -Wl,-rpath,/opt/tongsuo/lib64"

make && make install
```

在 Postfix main.cf 中配置国密 TLS：

```
# /etc/postfix/main.cf — 国密 TLS 配置

# 启用 TLS
smtpd_use_tls = yes
smtp_use_tls = yes

# 签名证书和私钥
smtpd_tls_cert_file = /etc/postfix/certs/mail_sign.crt
smtpd_tls_key_file = /etc/postfix/certs/mail_sign.key

# 加密证书和私钥（用于 TLCP 双证书场景）
# Postfix 原生不支持双证书配置，此处由 Tongsuo 底层自动协商
# 如果使用 TLCP 双证书模式，需要将两张证书合并
# cat mail_sign.crt mail_enc.crt > /etc/postfix/certs/mail_bundle.crt
# smtpd_tls_cert_file = /etc/postfix/certs/mail_bundle.crt

# CA 证书链
smtpd_tls_CAfile = /etc/postfix/certs/ca_bundle.crt

# 强制 TLS 加密（生产环境推荐）
smtpd_tls_security_level = encrypt
smtpd_tls_auth_only = yes

# SMTP 客户端 TLS 策略
smtp_tls_security_level = may
smtp_tls_CAfile = /etc/postfix/certs/ca_bundle.crt

# 日志级别
smtpd_tls_loglevel = 1

# TLS 协议版本与密码套件（由 Tongsuo 处理国密切勿协商）
# Postfix 不直接设置国密切勿套件，依赖 Tongsuo 的 openssl.cnf 配置
smtpd_tls_mandatory_protocols = TLSv1.2, TLSv1.3
smtpd_tls_protocols = TLSv1.2, TLSv1.3
```

对于 SMTPS（465 端口），在 master.cf 中启用：

```
# /etc/postfix/master.cf
smtps     inet  n       -       n       -       -       smtpd
  -o smtpd_tls_wrappermode=yes
  -o smtpd_sasl_auth_enable=yes
```

### 7.4 Dovecot IMAP/POP3 国密 TLS 配置

```
# /etc/dovecot/conf.d/10-ssl.conf

ssl = required
ssl_cert =
```

重启服务后，检查日志确认国密连接已建立：

```
# Postfix 日志
tail -f /var/log/maillog | grep "TLS"

# Dovecot 日志
tail -f /var/log/dovecot.log | grep "SSL"

# 期望看到类似输出：
# TLS connection established: TLSv1.3 with cipher TLS_SM4_GCM_SM3
```

### 7.5 Tongsuo 配置文件的国密段

Tongsuo 的行为受 openssl.cnf 控制，需要在配置文件中激活国密支持：

```
# /opt/tongsuo/ssl/openssl.cnf 关键片段

[openssl_init]
ssl_conf = ssl_module

[ssl_module]
system_default = system_default_sect

[system_default_sect]
# 启用国密切勿套件
CipherString = DEFAULT:@SECLEVEL=1
# 启用 SM2 曲线
Groups = SM2:P-256:P-384
# 签名算法包含 sm2sig_sm3
SignatureAlgorithms = sm2sig_sm3:ECDSA+SHA256:RSA-PSS+SHA256

# CA 默认使用 SM3 哈希
default_md = sm3
```

## 八、证书格式与密钥管理

### 8.1 国密 PKCS#12

国密证书的 PKCS#12 格式（.p12/.pfx）与传统 RSA 证书类似，但需使用 SM3 作为 MAC 算法和加密算法：

```
# 将 SM2 证书和私钥打包为 PKCS#12
tongsuo pkcs12 -export \
  -in mail_sign.crt \
  -inkey mail_sign.key \
  -certfile demoCA/cacert.pem \
  -out mail_bundle.p12 \
  -macalg sm3 \
  -keypbe sm4-cbc \
  -certpbe sm4-cbc

# 从 PKCS#12 提取证书和私钥
tongsuo pkcs12 -in mail_bundle.p12 -out extracted.pem -nodes
```

### 8.2 SM2 证书链验证

```
# 验证完整的证书链（CA 根 → 服务器证书）
tongsuo verify -CAfile demoCA/cacert.pem \
  -untrusted intermediate.crt \
  mail_sign.crt

# 验证证书有效期和关键字段
tongsuo x509 -in mail_sign.crt -text -noout | grep -A2 "Validity"
tongsuo x509 -in mail_sign.crt -text -noout | grep -A5 "Subject Public Key"
```

## 九、合规驱动：密评与等保 2.0 密码要求映射

部署国密算法不只是技术选择，更是合规要求。《中华人民共和国密码法》第二十七条要求关键信息基础设施运营者使用商用密码进行保护，并自行或委托机构开展商用密码应用安全性评估（简称"密评"）。

GB/T 39786-2021《信息安全技术 信息系统密码应用基本要求》是密评的核心依据，从四个技术层面规定了密码应用要求。下表给出了邮件系统在密评框架中的典型映射：

九、合规驱动：密评与等保 2.0 密码要求映射

| 密评层面 | 要求 | 邮件系统国密实现 | 涉及算法 |
| --- | --- | --- | --- |
| 网络和通信安全 | 身份鉴别、通信机密性、通信完整性 | TLS/TLCP 国密传输加密（SMTP/IMAP/POP3） | SM2 + SM3 + SM4 |
| 设备和计算安全 | 身份鉴别、远程管理通道加密 | SSH 国密切勿套件（Tongsuo）、管理后台 TLS | SM2 + SM3 + SM4 |
| 应用和数据安全 | 数据传输机密性、存储机密性、不可否认性 | S/MIME SM2 签名、SM4 邮件存储加密、操作审计签名 | SM2 + SM3 + SM4 |
| 密钥管理 | 密钥全生命周期管理 | 基于 KGC 的 SM9 密钥分发、PKI CA 使用国密算法签发证书 | SM2 + SM9 |

对于等保三级系统，密评要求尤为严格：网络通信层面必须使用密码技术进行身份鉴别和重要数据加密；应用层面需要实现数据的机密性、完整性和不可否认性。邮件系统的国密改造，本质上就是将上述四个层面中的国际密码算法替换为 SM 系列算法，并确保密码产品的采购和使用符合国家密码管理主管部门的要求。

GM/T 0024-2014《SSL VPN 技术规范》则更进一步，规定了基于国密算法的 SSL VPN 技术要求，对于通过 VPN 接入邮件系统的远程用户场景，同样构成了国密改造的技术边界。

## 十、部署建议与踩坑记录

以下是在邮件系统国密化过程中由实际运维踩出的常见问题及建议：

* **Tongsuo 与系统 OpenSSL 冲突：**
  始终使用独立 prefix 编译安装 Tongsuo，不要覆盖系统 OpenSSL。通过 LD\_LIBRARY\_PATH 控制运行时链接，或在编译邮件服务时使用 -rpath 硬编码路径。
* **双证书坑：**
  部分 MUA（邮件客户端）和 MTA 不支持 TLCP 双证书。此时可退而使用 RFC 8998 单证书模式——仅用签名证书完成 TLS 1.3 国密连接。双证书的主要场景是严格的 TLCP 合规要求。
* **客户端兼容性：**
  主流邮件客户端（Outlook、Thunderbird、Apple Mail）默认不支持国密切勿套件。对端到端国密的期待需要限定在可控客户端环境中（国密浏览器、定制邮件客户端）。传输层国密（服务器间 MTA-to-MTA TLS）是当前最现实的落地路径。
* **性能基准：**
  SM2 签名操作约 3000-5000 次/秒（单核 x86\_64），SM4-GCM 加密吞吐约 500-800 MB/s。对于邮件服务器的并发量级，国密算法的性能开销通常不构成瓶颈。
* **证书更新：**
  SM2 证书同样有有效期，建议设置证书到期监控（Prometheus blackbox\_exporter 可检查 TLS 证书过期时间），并在到期前 30 天自动续签。

### 关键要点

* SM2/SM3/SM4 构成了完整的"非对称+哈希+对称"密码学三角形，SM9 在此基础上增加了基于标识的免证书加密能力，共同覆盖了邮件系统从传输层到应用层的全部密码需求。
* TLCP（GB/T 38636）的双证书体系（签名+加密分离）是与标准 TLS 最大的工程差异，在严格合规场景下必须部署双证书，在兼容性优先的场景下可退而使用 RFC 8998 单证书国密切勿套件。
* RFC 8998 将国密算法纳入 TLS 1.3 标准框架，使得 SM2/SM3/SM4 可与国际密码套件在同一端口共存——这是"双轨制"（国际+国密）部署的技术基础，也是金融、政务等行业邮件系统的主流方案。
* Tongsuo（铜锁）是当前最成熟的国密开源密码库，编译配置相对直观，但在与 Postfix/Dovecot 集成时需要注意动态链接和 TLS 协议协商的正确配置。
* SM9 IBE 为邮件端到端加密提供了一条"零证书"路径，但密钥托管问题是其工程化的主要挑战，目前更适用于内部可控的封闭邮件体系。
* 国密部署应分段推进：先实现 MTA-to-MTA 传输层国密（SMTP TLS），再考虑客户端接入层的国密 TLS，最后评估 SM9/SM2 S/MIME 的端到端加密方案。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/guomi-email-cryptography.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
