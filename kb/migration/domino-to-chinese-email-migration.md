---
title: "从 Lotus Domino/Notes 迁移至国产邮件系统：NSF 导出、格式转换与目录同步"
source: "https://ztpop.net/kb/domino-to-chinese-email-migration.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# 从 Lotus Domino/Notes 迁移至国产邮件系统：NSF 导出、格式转换与目录同步

## 摘要

Lotus Domino/Notes 曾是企业邮件与协作系统的标杆产品，但其专有的 NSF 存储格式和 Notes Rich Text（CD 记录）在迁移至标准邮件系统时带来了独特的技术挑战。本文提出一套完整的 Domino→国产邮件系统迁移方案，涵盖 NSF 数据库的邮件数据提取与解析（基于 C API 与 NSFNoteOpen 系列接口）、Notes Rich Text 到 MIME 格式的转换策略（CD 记录 OLE 对象处理）、LDAP 目录桥接的设计与增量同步方案、日历/任务/待办事项的跨系统迁移路径选择，以及 Notes ID 文件管理与权限迁移。引用 RFC 2822（Internet Message Format）、RFC 2045（MIME）、RFC 4791（CalDAV）及 IBM Domino C API 参考文档。

## 1. Domino/Notes 邮件体系的技术特性

### 1.1 NSF 存储格式概述

Domino 使用 NSF（Notes Storage Facility）格式存储所有数据。一个 NSF 文件（扩展名 .nsf）是一个嵌入式数据库，包含文档（NotesDocument）、视图（NotesView）、表单（NotesForm）和代理（NotesAgent）等元素。与标准邮件系统的关键差异：

Domino/Notes 与标准邮件系统核心差异

| 维度 | Lotus Domino/Notes | 标准邮件系统（IMAP/SMTP） |
| 存储格式 | NSF（专有嵌入式数据库） | Maildir/mbox（纯文本标准） |
| 富文本格式 | Notes Rich Text（CD 记录格式，二进制 + OLE） | MIME（RFC 2045-2049 [3]） |
| 邮件协议 | NRPC（Notes Remote Procedure Call） | SMTP/IMAP/POP3 |
| 目录服务 | Domino Directory（NSF 格式 NAB） | LDAP（RFC 4511） |
| 日历 | Notes Calendar（NSF 中的 Calendar 文档） | iCalendar/CalDAV（RFC 5545/4791 [4]） |
| 身份认证 | Notes ID 文件（公/私钥对 + 证书） | 用户名/密码 + X.509 证书（S/MIME） |

## 2. NSF 邮件数据导出

### 2.1 导出方案选型

```
方案 A: Domino 原生 NSFXML 工具（推荐轻量场景）
  命令: nsfxml user.nsf > user_data.xml
  局限: XML 输出不包含附件二进制嵌入

方案 B: C API 程序化导出（推荐大规模部署）
  接口: NSFNoteOpen, NSFItemGetText, NSFDbOpen
  优势: 完整访问所有 CD 记录与 OLE 对象

方案 C: 第三方工具（如 ComPoint/XPages REST → JSON）
  适用: 需同时导出 ACL 和设计元素的场景

方案 D: IMAP 迁移（启用 Domino IMAP Service）
  适用: 仅邮件数据迁移，不迁移日历/任务/富文本格式
```

### 2.2 C API NSF 导出示例

```
/* nsf_dump_mail.c — 基于 Domino C API 的 NSF 邮件提取 */
#include <nsfdb.h>
#include <nsfnote.h>
#include <nsfsearc.h>

void export_notes_documents(DBHANDLE hDB) {
    NOTEHANDLE hNote;
    STATUS error;
    char szBuf[8192];
    
    for (error = NSFDbOpenNoteByClass(hDB, NOTE_CLASS_DOCUMENT,
                                      0, &hNote, NULL);
         !error;
         error = NSFDbOpenNoteByClass(hDB, NOTE_CLASS_DOCUMENT,
                                      0, &hNote, NULL)) {
        NSFItemGetText(hNote, "Subject", szBuf, sizeof(szBuf));
        NSFItemGetText(hNote, "From", szBuf, sizeof(szBuf));
        NSFItemGetText(hNote, "Body", szBuf, sizeof(szBuf));
        NSFNoteClose(hNote);
    }
}
```

注：Domino C API 当前支持版本为 R12+，需部署于兼容的 Linux/Windows 开发环境。NSF 文件打开前需确保 Domino Server 服务运行且具有含 NSF 访问权限的 Server ID。[2]

## 3. Notes Rich Text → MIME 格式转换

### 3.1 Notes CD 记录体系

Notes Rich Text 的二进制格式由一系列 CD（Composite Data）记录组成。每一条 CD 记录由头部（CDRECORDHEADER）+ 数据体构成。[2]

常见 Notes CD 记录类型

| CD 类型 | 标识符 | 对应 MIME 元素 |
| CDPARAGRAPH | 0x01 | 文本段落（HTML <p>） |
| CDTEXT | 0x02 | 文本片段（带字体/字号/颜色） |
| CDBITMAP | 0x05 | 内嵌图片（MIME image/\*） |
| CDTABLE | 0x10 | 表格（HTML <table>） |
| CDHOTSPOTBEGIN | 0x0E | 链接/动作区域（HTML <a>） |
| CDEMBEDDEDCTL | 0x1D | OLE 嵌入对象（需特殊处理） |

### 3.2 CD → MIME 转换策略

```
# cd_to_mime.py — Notes CD 记录到 MIME/HTML 转换
import struct
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class CDParser:
    """Notes CD 记录流解析器"""
    CD_HEADER_FMT = '<HHBBHH'
    
    def __init__(self, cd_data: bytes):
        self.cd_data = cd_data
        self.offset = 0
        self.html_parts = []
        self.attachments = []
    
    def parse(self):
        while self.offset < len(self.cd_data):
            if self.offset + 8 > len(self.cd_data):
                break
            header = struct.unpack_from(self.CD_HEADER_FMT, self.cd_data, self.offset)
            cd_id = header[4]
            cd_len = header[5]
            
            if cd_id == 0x01:  # CDPARAGRAPH
                self.html_parts.append('<br>')
            elif cd_id == 0x02:  # CDTEXT
                text_bytes = self.cd_data[self.offset+8:self.offset+cd_len]
                text = self._lmbcs_to_utf8(text_bytes)
                self.html_parts.append(text)
            elif cd_id == 0x05:  # CDBITMAP
                img_data = self._extract_bitmap(cd_len)
                cid = f'img{len(self.attachments)}@ztpop.net'
                self.html_parts.append(f'<img src="cid:{cid}">')
                self.attachments.append(('image', img_data, cid))
            elif cd_id == 0x10:  # CDTABLE
                self._parse_table(cd_len)
            self.offset += cd_len
            if self.offset % 2:
                self.offset += 1
    
    def _lmbcs_to_utf8(self, data: bytes) -> str:
        """LMBCS → UTF-8 转换（简化实现）
        实际需处理 LMBCS 分组转码，中文环境注意 GB2312/GBK 映射"""
        try:
            return data.decode('utf-8', errors='replace')
        except:
            return data.decode('latin-1', errors='replace')
    
    def to_mime(self) -> MIMEMultipart:
        msg = MIMEMultipart('related')
        html = '<html><body>' + ''.join(self.html_parts) + '</body></html>'
        msg.attach(MIMEText(html, 'html'))
        for atype, adata, cid in self.attachments:
            if atype == 'image':
                img = MIMEImage(adata)
                img.add_header('Content-ID', f'<{cid}>')
                msg.attach(img)
        return msg
```

LMBCS（Lotus Multi-Byte Character Set）是 Notes 的内部编码方案。中文环境中需特别处理 GB2312/GBK 与 LMBCS 的映射关系。[2]

## 4. LDAP 目录桥接同步

### 4.1 Domino Directory → OpenLDAP 架构

```
Domino Directory → LDAP Bridge → 目标系统目录

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Domino LDAP  │────→│ LDAP Bridge  │────→│ 目标 LDAP /  │
│ (389/636)    │     │ (同步引擎)    │     │  数据库       │
└──────────────┘     └──────────────┘     └──────────────┘
Domino Directory    增量/全量同步          国产邮件系统
(NAB, person文档)   属性映射与转换         用户认证/授权
```

### 4.2 属性映射规则

Domino Person 文档 → LDAP 属性映射

| Domino 字段 | LDAP 属性 | 备注 |
| FullName | cn, displayName | 可能包含层级名称 |
| ShortName/UID | uid, sAMAccountName | 取第一个 CN 组分 |
| InternetAddress | mail | 主 SMTP 地址 |
| MailDomain | mailRoutingAddress | 邮件路由域 |
| HTTPPassword | userPassword | 密码 hash 转换（DXL 工具） |
| Department | departmentNumber | 部门 |
| Certificate | userCertificate | Notes 证书 → X.509（可选） |

### 4.3 Python LDAP 桥接同步实现

```
# domino_ldap_bridge.py — Domino 目录到 OpenLDAP 同步
import ldap3
from ldap3 import MODIFY_REPLACE
import time, logging

DOMINO_LDAP = 'ldap://domino.ztpop.net:389'
DOMINO_BASE = 'o=ztpop'
TARGET_LDAP = 'ldap://target.ztpop.net:389'
TARGET_BASE = 'dc=mail,dc=ztpop,dc=net'

dom_conn = ldap3.Connection(DOMINO_LDAP, user='cn=admin,o=ztpop',
                            password='domino_pass', auto_bind=True)
tgt_conn = ldap3.Connection(TARGET_LDAP, user='cn=admin,dc=mail',
                            password='target_pass', auto_bind=True)

dom_conn.search(
    search_base=DOMINO_BASE,
    search_filter='(objectClass=dominoPerson)',
    search_scope=ldap3.SUBTREE,
    attributes=['cn', 'mail', 'department', 'telephoneNumber']
)

for entry in dom_conn.entries:
    if not entry.mail.value:
        continue
    email = entry.mail.value
    target_dn = f'mail={email},ou=users,{TARGET_BASE}'
    attrs = {
        'objectClass': ['inetOrgPerson', 'mailRecipient'],
        'uid': email.split('@')[0],
        'cn': entry.cn.value if entry.cn else email,
        'mail': email,
        'departmentNumber': entry.department.value if entry.department else '',
    }
    if tgt_conn.search(target_dn, '(objectClass=*)', attributes=['cn']):
        tgt_conn.modify(target_dn, {
            'cn': [(MODIFY_REPLACE, [entry.cn.value])],
            'mail': [(MODIFY_REPLACE, [email])],
        })
    else:
        tgt_conn.add(target_dn, attributes=attrs)
    logging.info(f'Synced: {email}')

# 调度执行：建议每 30 分钟增量同步
# */30 * * * * python3 domino_ldap_bridge.py
```

## 5. 日历与任务迁移挑战

### 5.1 Notes Calendar → iCalendar/CalDAV

Notes 日历文档的字段与 iCalendar（RFC 5545 [5]）的对应：

Notes Calendar → iCalendar 字段映射

| Notes 字段 | iCalendar 属性 | 注意事项 |
| CalendarDateTime | DTSTART / DTEND | Notes 使用 TIMEDATE 格式 |
| CalendarDescription | DESCRIPTION | 含 CD 富文本 → 纯文本或 HTML |
| CalendarRepeat | RRULE | 重复规则格式差异 |
| CalendarParticipants | ATTENDEE | 参与者状态映射 |
| AppointmentType | TRANSP | 忙/闲/私人映射 |
| Room\_Resources | RESOURCES | 会议室/设备映射 |
| Alarms | VALARM | 触发偏移量转换 |

### 5.2 Notes To Do → VTODO 转换

```
# notes_todo_to_ical.py
import icalendar
from datetime import datetime

def convert_notes_todo_to_vtodo(notes_doc: dict):
    vtodo = icalendar.VTodo()
    vtodo.add('uid', f'{notes_doc["unid"]}@ztpop.net')
    vtodo.add('dtstamp', datetime.utcnow())
    vtodo.add('summary', notes_doc.get('Subject', ''))
    vtodo.add('description', notes_doc.get('Body', ''))
    priority_map = {'1': 1, '2': 5, '3': 9}
    vtodo.add('priority', priority_map.get(notes_doc.get('Priority', '3'), 3))
    if notes_doc.get('DueDate'):
        vtodo.add('due', datetime.fromtimestamp(notes_doc['DueDate']))
    status_map = {'Completed': 'COMPLETED', 'In Process': 'IN-PROCESS',
                  'Not Started': 'NEEDS-ACTION'}
    vtodo.add('status', status_map.get(notes_doc.get('Status', 'Not Started')))
    if notes_doc.get('PercentComplete'):
        vtodo.add('percent-complete', int(notes_doc['PercentComplete']))
    return vtodo
```

## 6. Notes ID 文件管理与权限迁移

### 6.1 Notes ID 文件体系

每个 Notes 用户拥有一个唯一的 ID 文件（.ID），包含：

* 公/私钥对（RSA 1024/2048 位）；
* Notes 证书（由 Domino 认证中心签发）；
* 加密密钥（用于 Notes 级加密）；
* 口令保护（与 Notes 用户口令分离管理）。

### 6.2 迁移策略

```
策略 1: 证书转换（推荐）
  从 ID 文件中提取 RSA 私钥 → 生成 X.509 证书对 → 导入 S/MIME 证书存储
  工具: Domino Certificate Authority + 转换脚本

策略 2: 保留 Notes 客户端（过渡期）
  用户继续使用 Notes 客户端访问旧数据
  新邮件系统使用独立的 S/MIME 证书
  阶段 2 时撤销 Notes 证书

策略 3: 重新颁发证书（最简方案）
  在新邮件系统直接颁发 S/MIME 证书
  旧 Notes ID 文件保留用于旧数据访问
```

## 7. 迁移验证与回滚

### 7.1 验证清单

1. **邮件数量验证：** 源端 NSF 文档计数 vs 目标端 IMAP 文件夹计数，误差 ≤ 0.01%；
2. **富文本渲染验证：** 随机抽样 5% 的富文本邮件，人工比对渲染效果；
3. **附件完整性：** 所有附件可正常打开，SHA-256 校验和一致；
4. **日历事件验证：** 随机抽样 10% 的日历事件，检查时间、参与者、重复规则正确转换；
5. **目录一致性：** 目标 LDAP 中的用户列表与 Domino Directory 一致。

### 7.2 回滚方案

* 保留原始 NSF 备份 60 天，未决法律 hold 期间保留 6 年；
* 保持 Domino 服务可用至少 30 天；
* 备份所有 Notes ID 文件及口令，保留 90 天以上。

## 参考文献

1. RFC 2822 — Internet Message Format, P. Resnick, 2001.
2. IBM Domino C API Reference, Release 12.0, IBM Corporation, 2023.
3. RFC 2045 — Multipurpose Internet Mail Extensions (MIME) Part One, N. Freed & N. Borenstein, 1996.
4. RFC 4791 — Calendaring Extensions to WebDAV (CalDAV), C. Daboo et al., 2007.
5. RFC 5545 — Internet Calendaring and Scheduling Core Object Specification, B. Desruisseaux, 2009.
6. RFC 4511 — Lightweight Directory Access Protocol (LDAP): The Protocol, J. Sermersheim, 2006.
7. Kauffman, S., "Lotus Notes and Domino: Migration Strategies and Best Practices", IBM Redbooks, 2019.
8. NIST SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems, 2010.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/domino-to-chinese-email-migration.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
