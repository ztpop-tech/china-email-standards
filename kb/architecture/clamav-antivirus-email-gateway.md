---
title: "摘要：ClamAV是邮件安全网关中部署最广泛的开源反病毒引擎，由Cisco Talos维护，以GPLv2协议授权。它通过多线程守护进程（clamd）为SMTP网关提供实时病毒扫描服务，支持对邮件正文和附件进行解包后深度检测。本文覆盖ClamAV的核心架构、与Amavis/Postfix的集成配置、性能优化参数和病毒库更新策略。所有配置参数适用于生产环境部署。"
source: "https://ztpop.net/kb/clamav-antivirus-email-gateway.html"
mirror_date: 2026-07-25
license: CC-BY 4.0
---

# 摘要：ClamAV是邮件安全网关中部署最广泛的开源反病毒引擎，由Cisco Talos维护，以GPLv2协议授权。它通过多线程守护进程（clamd）为SMTP网关提供实时病毒扫描服务，支持对邮件正文和附件进行解包后深度检测。本文覆盖ClamAV的核心架构、与Amavis/Postfix的集成配置、性能优化参数和病毒库更新策略。所有配置参数适用于生产环境部署。

## 1. ClamAV架构概览

ClamAV包含三个核心组件：
**clamd**
（多线程扫描守护进程）、
**freshclam**
（病毒库自动更新工具）和
**clamscan**
（命令行扫描器）。邮件网关场景中，Amavis通过Unix域套接字或TCP连接向clamd提交待扫描文件，clamd加载病毒签名数据库进行匹配后返回判定结果。

性能关键：clamd启动时将整个病毒签名库加载到内存中。2026年7月的ClamAV官方病毒库（main.cvd + daily.cvd + bytecode.cvd）总大小约400MB。加载到内存中后，clamd保持这些数据结构在RAM中以实现亚秒级扫描延迟——这是区别于每次启动重新加载的clamscan的关键优势。

```
# 查看当前病毒库版本和签名数量
clamscan --version
# 输出示例：ClamAV 1.3.0/27745/Mon Jul 10 12:00:00 2026
# 27745 = 病毒库版本号

sigtool --info /var/lib/clamav/main.cvd
# 输出：Build time, Version, Signatures count, Functionality level
```

## 2. 安装与基础配置

```
# CentOS/RHEL 安装
yum install -y epel-release
yum install -y clamav clamav-update clamd

# Ubuntu/Debian 安装
apt-get install -y clamav clamav-daemon

# 麒麟 V10 / 统信 UOS
yum install -y clamav clamav-update
```

核心配置文件
`/etc/clamd.conf`
（注释掉Example行以启用）：

```
# /etc/clamd.conf — 生产环境推荐配置
LogFile /var/log/clamav/clamd.log
LogTime yes
LogSyslog yes
PidFile /var/run/clamd.pid
DatabaseDirectory /var/lib/clamav
LocalSocket /var/run/clamd.sock
LocalSocketGroup clamav
LocalSocketMode 666
User clamav
MaxConnectionQueueLength 200
MaxThreads 20
ReadTimeout 300
StreamMaxLength 100M
MaxFileSize 100M
MaxScanSize 400M
MaxRecursion 16
MaxFiles 10000
AlertEncrypted yes
AlertOLE2 yes
AlertPDF yes
AlertMacros yes
ScanMail yes
ScanArchive yes
ScanPDF yes
ScanOLE2 yes
ScanHTML yes
ScanPE yes
ScanELF yes
```

2. 安装与基础配置

| 参数 | 含义 | 建议值 |
| `MaxThreads` | 并发扫描线程数 | CPU核数 × 2（不超过50） |
| `StreamMaxLength` | 单次扫描最大数据量 | 100MB（匹配Postfix message\_size\_limit） |
| `MaxScanSize` | 解包后最大扫描数据量 | 400MB（压缩炸弹保护） |
| `MaxRecursion` | 嵌套解包最大层数 | 16（防ZIP炸弹） |
| `MaxFiles` | 单次扫描最大解包文件数 | 10000 |
| `MaxConnectionQueueLength` | 等待队列最大长度 | 200 |

**压缩炸弹（Zip Bomb）防护**
：攻击者可能发送一个42KB的ZIP文件，解压后展开为4.5PB的垃圾数据（42.zip攻击）。
`MaxScanSize=400M`
和
`MaxRecursion=16`
确保了ClamAV不会在这种攻击下耗尽系统内存。

## 3. 病毒库自动更新

freshclam通过HTTPS从Cisco Talos的CDN下载增量病毒库更新（daily.cvd使用增量diff格式，每次更新仅下载变动部分，约100KB-2MB）。推荐配置：

```
# /etc/freshclam.conf
DatabaseDirectory /var/lib/clamav
UpdateLogFile /var/log/clamav/freshclam.log
PidFile /var/run/freshclam.pid
DatabaseOwner clamav
Checks 24            # 每天检查24次（每小时一次）
NotifyClamd yes      # 更新后通知clamd重新加载
DatabaseMirror database.clamav.net
ScriptedUpdates yes  # 使用增量更新脚本
CompressLocalDatabase no
```

`Checks 24`
配合
`ScriptedUpdates yes`
是推荐的平衡配置——每小时检查一次增量更新，在更新及时性和网络带宽之间取得平衡。Cisco Talos每天发布4-6次病毒库更新（紧急爆发期可能增加到每小时一次）。

## 4. Amavis + ClamAV 集成

Amavis（A Mail Virus Scanner）是Postfix生态中最成熟的邮件内容过滤器，充当Postfix与ClamAV/SpamAssassin之间的中间层：

```
# /etc/amavis/conf.d/15-content_filter_mode
use strict;
@bypass_virus_checks_maps = (
   \%bypass_virus_checks, \@bypass_virus_checks_acl, \$bypass_virus_checks_re);
@bypass_spam_checks_maps  = (
   \%bypass_spam_checks, \@bypass_spam_checks_acl, \$bypass_spam_checks_re);

# /etc/amavis/conf.d/15-av_scanners
@av_scanners = (
    ['ClamAV-clamd',
    \&ask_daemon, ["CONTSCAN {}
", "/var/run/clamd.sock"],
    qr/OK$/m, qr/FOUND$/m,
    qr/^.*?: (?!Infected Archive)(.*) FOUND$/m ],
);
```

Postfix集成需在
`master.cf`
中加入Amavis的SMTP/LMTP服务过滤行：

```
# /etc/postfix/master.cf
smtp-amavis unix - - n - 8 smtp
  -o smtp_data_done_timeout=1200
  -o smtp_send_xforward_command=yes
  -o disable_dns_lookups=yes

127.0.0.1:10025 inet n - n - - smtpd
  -o content_filter=
  -o smtpd_recipient_restrictions=permit_mynetworks,reject
  -o receive_override_options=no_header_body_checks

# /etc/postfix/main.cf
content_filter = smtp-amavis:[127.0.0.1]:10024
```

邮件流路径：Postfix smtpd → Amavis (10024) → ClamAV (clamd.sock) + SpamAssassin → 返回Amavis → Postfix reinject (10025) → 投递到邮箱。

## 5. ClamAV支持的文件格式

5. ClamAV支持的文件格式

| 类别 | 支持格式 |
| 归档 | ZIP, RAR (v2-v5), 7-Zip, Tar, Gzip, Bzip2, CPIO, ARJ, CAB, CHM, ISO 9660, DMG, XAR |
| 可执行文件 | PE (EXE/DLL/SYS), ELF, Mach-O, UPX/FSG/Petite压缩壳, .NET assemblies |
| 文档 | Microsoft Office (OLE2/XML), PDF, RTF, HTML |
| 邮件 | MBOX, Maildir, TNEF (winmail.dat) |

## 6. 性能基准与容量规划

基于生产环境的实际测量（Intel Xeon E5-2680 v4, 14核, 64GB RAM）：

* clamd单线程扫描吞吐量：约30-50封邮件/秒（平均邮件大小80KB）
* MaxThreads=20时的并发吞吐量：约400-600封邮件/秒
* clamd内存占用（启动后）：约1.2GB（病毒库400MB + 运行时800MB）
* 扫描延迟中位数（P50）：80ms；P99：350ms

对于日均10万封邮件的企业，单台ClamAV实例（MaxThreads=10）即可满足需求。日处理量超过50万封时，建议部署ClamAV集群配合TCP负载均衡器。

```
# 压力测试：测量clamd扫描吞吐量
time for f in /opt/test-corpus/*; do
  clamdscan --no-summary "$f" > /dev/null
done
# 计算：N个文件 / 总耗时 = 平均吞吐量（封/秒）
```

## 参考文献

1. ClamAV Project, "ClamAV — Open Source Antivirus Engine for Email Scanning," Cisco Talos, GPLv2.
   <https://docs.clamav.net/>
2. NIST SP 800-83 Rev. 1, "Guide to Malware Incident Prevention and Handling for Desktops and Laptops," §4 Malware Prevention, NIST, 2013.
3. Amavis Project, "amavisd-new — Interface between MTA and Content Checkers,"
   <https://gitlab.com/amavis/amavis>
4. RFC 5321, "Simple Mail Transfer Protocol," §4.5.3.1 Sending Strategy, IETF, 2008.
5. MTE (Malware Traffic Evaluation) Guidelines, "Best Practices for Email Malware Scanning Performance," 2024.
6. . 引用日期：2026-07-11.

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/clamav-antivirus-email-gateway.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
