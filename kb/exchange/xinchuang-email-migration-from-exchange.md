---
title: "从 Exchange 到信创邮件系统的迁移工程实践"
source: "https://ztpop.net/kb/xinchuang-email-migration-from-exchange.html"
license: CC-BY 4.0
---

# 从 Exchange 到信创邮件系统的迁移工程实践

## 摘要

随着信创替代工程的深入，大量长期依赖 Microsoft Exchange 的党政机关和企事业单位面临邮件系统整体迁移的挑战。Exchange 的封闭生态（MAPI/EWS、PST 归档格式、AD 目录集成）与信创邮件系统的开放标准架构之间存在天然差异。本文基于工程实践经验，系统性阐述从 Exchange 到信创邮件系统的迁移方法论，覆盖数据导出、协议选择、目录重建、权限映射、完整性校验和业务连续性保障等关键环节。

## 一、Exchange 数据生态与导出方案

Exchange 的数据模型由三个紧密耦合的组件构成：邮箱数据库（EDB）、Active Directory 用户目录、PST/OST 离线归档。迁移的第一步是厘清数据资产并进行标准化导出。

### 1.1 邮箱数据导出格式分析

Exchange 邮箱数据可以通过以下途径导出：

1.1 邮箱数据导出格式分析

| 导出方式 | 输出格式 | 适用场景 | 局限性 |
| New-MailboxExportRequest | PST 文件 | 单用户/批量导出 | 需 Exchange 管理权限，PST 有 50GB 硬限制 |
| IMAP 协议同步 | RFC 5322 EML | 中小规模、标准协议迁移 | 不保留 Exchange 特有属性（分类/标记） |
| EWS (Exchange Web Services) | XML/MIME | 需要保留 Exchange 元数据 | 代码工作量大，EWS 已弃用 |
| Microsoft Graph API | JSON/MIME | Exchange Online / Hybrid | 需 Azure AD 应用注册 |

对于信创迁移场景，推荐首选 IMAP 协议（RFC 3501）作为数据传输通道。IMAP 是 IETF 标准化协议，所有主流邮件客户端和服务器均支持，规避了 Exchange 私有协议带来的厂商锁定风险。

## 二、基于 RFC 3501 的 IMAP 迁移方案

IMAP4rev1（RFC 3501）定义了一组完整的邮箱操作原语：SELECT（选择邮箱）、FETCH（获取邮件）、APPEND（追加邮件）、COPY（复制邮件）、SEARCH（搜索邮件）等。迁移工具通过组合这些原语，将源服务器的邮件完整复制到目标信创邮件系统。

### 2.1 迁移架构设计

迁移架构由三部分组成：迁移调度器（orchestrator）、IMAP 源端客户端、IMAP 目标端客户端。调度器从迁移清单中读取用户列表，为每个用户创建独立的迁移任务，并行执行。为避免对生产 Exchange 造成压力，需设置连接限速。

### 2.2 IMAP 迁移核心步骤

```
#!/bin/bash
# IMAP 邮箱迁移脚本框架
# 依赖: curl (IMAP), openssl (TLS 验证)

SOURCE_HOST="exchange.example.com"
SOURCE_PORT="993"
TARGET_HOST="mail.xinchuang.local"
TARGET_PORT="993"
MIGRATION_USER="$1"

# 步骤 1: 连接源 IMAP 并列出所有文件夹
curl -s --ssl-reqd -u "${MIGRATION_USER}:${SRC_PASS}" \
    "imaps://${SOURCE_HOST}:${SOURCE_PORT}/" \
    -X 'LIST "" "*"' 2>/dev/null

# 步骤 2: 遍历每个文件夹，按 RFC 3501 FETCH 获取邮件
# (实际实现用 Python/Perl 的 IMAP 客户端库)
for folder in INBOX Sent Drafts Trash; do
    echo "Migrating folder: ${folder}"

    # 3a. SELECT 目标文件夹
    # 3b. FETCH 1:* (FLAGS INTERNALDATE BODY.PEEK[])
    # 3c. 将获取的邮件通过 APPEND 写入目标服务器同名文件夹

    imap_migrate_folder \
        --src-host "${SOURCE_HOST}" --src-port "${SOURCE_PORT}" \
        --dst-host "${TARGET_HOST}" --dst-port "${TARGET_PORT}" \
        --user "${MIGRATION_USER}" --folder "${folder}"
done

# 步骤 3: 验证邮件数量一致性
SRC_COUNT=$(imap_status "${SOURCE_HOST}" "${MIGRATION_USER}" "${folder}" | jq '.messages')
DST_COUNT=$(imap_status "${TARGET_HOST}" "${MIGRATION_USER}" "${folder}" | jq '.messages')
if [ "${SRC_COUNT}" -ne "${DST_COUNT}" ]; then
    echo "WARN: Count mismatch for ${MIGRATION_USER}/${folder}: ${SRC_COUNT} vs ${DST_COUNT}"
fi
```

### 2.3 突破 Exchange IMAP 约束

Exchange 对 IMAP 协议的实现存在一些约束：客户端 IP 连接限制（默认 20）、单次 FETCH 返回的邮件数量限制（默认 1000）。在批量迁移前，建议通过 Exchange Management Shell 提高这些阈值：

```
# Exchange Management Shell - 提高 IMAP 连接限制
Set-ImapSettings -MaxConnectionsPerUser 100
Set-ReceiveConnector "EXCHANGE\Client Frontend EXCHANGE" -MaxInboundConnection 10000

# 重启 IMAP 服务使配置生效
Restart-Service MSExchangeImap4
Restart-Service MSExchangeImap4Backend
```

## 三、PST 归档文件的解析与导入

对于历史归档中存储为 PST 格式的大量邮件数据，需要使用专门的解析工具将其转换为标准 RFC 5322 格式（即 .eml 文件），再导入信创邮件系统。

### 3.1 PST 文件结构概述

PST 文件采用微软的二进制结构化存储格式（Compound Binary File），内部由节点数据库（NDB）、列表/表/属性（LTP）和消息对象（Message Object）三层组成。解析 PST 需处理 ANSI（32 位）和 Unicode（64 位）两种编码版本。

### 3.2 PST 解析与批量转换

在 Linux 信创环境下，推荐使用 libpff（开源 PST 解析库）进行批量转换：

```
# 安装 libpff 工具集（麒麟 V10 / 统信 UOS 通用）
# 编译安装
git clone https://github.com/libyal/libpff.git
cd libpff
./synclibs.sh && ./autogen.sh
./configure --prefix=/opt/pfftools && make -j$(nproc) && make install

# 列出 PST 文件中的文件夹结构
/opt/pfftools/bin/pffinfo /mnt/archive/user_zhangsan.pst

# 导出所有邮件为 RFC 5322 格式的独立 .eml 文件
/opt/pfftools/bin/pffexport \
    -t /tmp/pst_export/user_zhangsan \
    -m eml \
    /mnt/archive/user_zhangsan.pst

# 验证导出的邮件数量
find /tmp/pst_export/user_zhangsan -name "*.eml" | wc -l
```

### 3.3 批量导入信创邮件系统

导出为 .eml 文件后，可通过 LMTP 协议直接将邮件投递到信创邮件系统，保留原始邮件的所有头信息（From、Date、Message-ID 等），确保邮件完整性和可追溯性：

```
# 通过 LMTP 批量投递 .eml 文件到信创邮件系统
for eml_file in /tmp/pst_export/user_zhangsan/**/*.eml; do
    # 使用 sendmail/lmtp 方式投递
    cat "${eml_file}" | /opt/mta/sbin/sendmail -t user_zhangsan@xinchuang.local
done
```

## 四、用户目录与属性映射

Exchange 的 Active Directory 使用层次化的组织单位（OU）结构来管理用户和组，而信创邮件系统通常使用 LDAP（OpenLDAP 或 389 DS）或数据库来存储用户目录。迁移的关键挑战在于属性映射。

### 4.1 核心属性映射表

4.1 核心属性映射表

| AD 属性 | 作用 | 信创系统对应的映射目标 |
| sAMAccountName | 用户登录名 | uid（POSIX account） |
| userPrincipalName | 用户主体名 (UPN) | 邮件地址 |
| mail | 主电子邮件地址 | mail |
| proxyAddresses | 邮箱别名 (SMTP:sip:) | mailAlternateAddress |
| memberOf | 组成员关系 | LDAP groupOfNames / 邮件列表 |
| msExchMailboxGuid | Exchange 邮箱 GUID | 删除（信创系统自行生成） |
| msExchRecipientTypeDetails | 收件人类型 | 映射为 accountType（user/shared/room） |
| displayName | 显示名称 | cn 或 displayName |

### 4.2 目录迁移脚本示例

使用 LDIF 格式从 AD 导出用户数据，然后通过转换脚本映射为信创 LDAP 的目标 Schema：

```
# 从 AD 导出用户到 LDIF（在 Windows AD 服务器上执行）
ldifde -f ad_users.ldif -s dc01 -d "OU=Users,DC=example,DC=com" \
    -r "(objectClass=user)" -l "sAMAccountName,mail,displayName,memberOf"

# 在信创服务器上：转换并导入到 OpenLDAP
python3 <<'PYEOF'
import re

with open('ad_users.ldif', 'r') as f:
    content = f.read()

# 将 AD objectClass 替换为信创 Schema
content = content.replace('objectClass: user', 'objectClass: inetOrgPerson')
content = content.replace('objectClass: organizationalPerson', '')
content = content.replace('sAMAccountName:', 'uid:')

# 移除 Exchange 特有属性
content = re.sub(r'^msExch.*\n?', '', content, flags=re.MULTILINE)
content = re.sub(r'^objectCategory:.*\n?', '', content, flags=re.MULTILINE)

with open('xinchuang_users.ldif', 'w') as f:
    f.write(content)

print("LDIF 转换完成，请检查后执行 ldapadd 导入")
PYEOF

# 导入到信创 LDAP
ldapadd -x -H ldaps://ldap.xinchuang.local -D "cn=admin,dc=xinchuang,dc=local" \
    -W -f xinchuang_users.ldif
```

## 五、邮件权限模型转换

Exchange 的委托访问（Delegate Access）和文件夹权限通过 AD ACL 实现，信创邮件系统则基于 IMAP ACL（RFC 4314）标准。权限模型的转换规则如下：

五、邮件权限模型转换

| Exchange 权限 | IMAP ACL 权限 (RFC 4314) | 说明 |
| Full Access (完全访问) | lrswipkxtead | 全部 ACL 权限位 |
| Send As (代理发送) | p (post) + 外部 SASL 认证 | 需要邮件服务额外配置 |
| Send on Behalf (代表发送) | w (write) + Sender 头改写 | 由 MTA 在投递时处理 |
| Reviewer (审阅者) | lrs | 查看、读取、标记已读/未读 |
| Editor (编辑者) | lrwsipte | 读写+标记+删除 |

## 六、数据完整性校验

迁移完成后必须进行多层次的数据校验。根据 GB/T 37002 对电子邮件系统数据完整性的要求，校验应包括邮件数量、邮件大小和内容摘要三个维度。

```
#!/bin/bash
# 邮箱迁移完整性校验脚本
# 比较源 Exchange 和目标信创系统的邮件总量

USER_EMAIL="$1"
SRC_IMAP="exchange.example.com"
DST_IMAP="mail.xinchuang.local"
LOG_FILE="/var/log/migration/verify_${USER_EMAIL}.log"

echo "=== 迁移校验: ${USER_EMAIL} ===" | tee -a "${LOG_FILE}"

# 获取源和目标各文件夹的邮件计数
for folder in INBOX Sent Drafts Trash "Junk E-mail"; do
    SRC=$(imap_search_count "${SRC_IMAP}" "${USER_EMAIL}" "${folder}")
    DST=$(imap_search_count "${DST_IMAP}" "${USER_EMAIL}" "${folder}")

    if [ "${SRC}" -eq "${DST}" ]; then
        echo "  [PASS] ${folder}: ${SRC} = ${DST}" | tee -a "${LOG_FILE}"
    else
        echo "  [FAIL] ${folder}: Source=${SRC}, Dest=${DST}, Diff=$((SRC-DST))" | tee -a "${LOG_FILE}"
    fi

    # 抽样校验：对比第一封和最后一封邮件的 Message-ID 和大小
    SRC_FIRST_MSGID=$(imap_get_message_id "${SRC_IMAP}" "${USER_EMAIL}" "${folder}" 1)
    DST_FIRST_MSGID=$(imap_get_message_id "${DST_IMAP}" "${USER_EMAIL}" "${folder}" 1)
    if [ "${SRC_FIRST_MSGID}" != "${DST_FIRST_MSGID}" ]; then
        echo "  [WARN] Message-ID mismatch for item 1 in ${folder}" | tee -a "${LOG_FILE}"
    fi
done

echo "校验完成。结果见 ${LOG_FILE}"
```

## 七、分阶段迁移与业务连续性

对于生产系统，推荐采用三阶段切换策略，最大限度减少业务中断：

### 7.1 阶段一：并行运行期（7-14 天）

将信创邮件系统部署完成并通过基础验证后，配置 SMTP 中继，使 Exchange 将所有外发邮件通过信创 MTA 代理发送。此阶段的关键配置是在 Exchange 上设置发送连接器指向信创 MTA：

```
# Exchange Management Shell - 创建到信创 MTA 的发送连接器
New-SendConnector -Name "XinchuangRelay" -AddressSpaces "*" \
    -SmartHosts mail.xinchuang.local -SmartHostAuthMechanism None \
    -DNSRoutingEnabled $false -SourceTransportServers EXCH01
```

### 7.2 阶段二：分批迁移（14-30 天）

按部门/OU 分批次迁移用户邮箱数据。每批约 50-100 个用户，在非工作时间（如周末夜间）执行。每批迁移完成后，立即执行完整性校验并通知用户验证。

### 7.3 阶段三：正式切换与回退预案

修改 MX 记录指向信创邮件系统，将 Exchange 降级为备用中继节点。回退预案要求 MX 记录 TTL 预先降低到 300 秒，确保在发现问题时可在 5 分钟内回切至 Exchange。

## 八、常见问题与处置

1. **日历和联系人数据丢失**：IMAP 标准协议不传输日历和联系人。对于依赖于 Exchange 日历协同的团队，需评估信创邮件系统的 CalDAV/CardDAV 支持能力，或通过 EWS 导出 iCalendar 格式后再导入。
2. **附件编码异常**：部分非标准 MIME 编码的附件在 IMAP 传输过程中可能出现损坏。建议在迁移前后对附件进行 SHA-256 校验。
3. **邮件文件夹层级超过 IMAP 路径限制**：Exchange 允许任意深度的文件夹嵌套，某些邮件服务器对文件夹路径长度有限制。迁移前应执行路径长度审计。
4. **S/MIME 签名邮件**：IMAP FETCH BODY[] 返回原始 MIME，S/MIME 签名原样保留，在信创邮件系统的 WebMail 中只要正确实现 MIME 解析即可正常显示。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/xinchuang-email-migration-from-exchange.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
