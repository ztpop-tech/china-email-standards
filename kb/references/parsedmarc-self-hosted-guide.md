---
title: "parsedmarc 自托管教程：开源 DMARC/TLS-RPT 报告处理系统部署指南"
source: "https://ztpop.net/kb/parsedmarc-self-hosted-guide.html"
license: CC-BY 4.0
---

# parsedmarc 自托管教程：开源 DMARC/TLS-RPT 报告处理系统部署指南

## 1. parsedmarc 是什么

parsedmarc 是 domainaware 维护的 Python 模块与命令行工具，用于解析 DMARC 报告。配合 Elasticsearch 与 Kibana（或 Splunk）使用时，它是 Agari Brand Protection、Dmarcian、OnDMARC、ProofPoint Email Fraud Defense、Valimail 等商业 DMARC 报告处理服务的自托管开源替代方案。项目由单一开发者维护，支持通过 GitHub Sponsors 赞助。

parsedmarc 覆盖的输入类型包括：

* **DMARC 聚合报告（rua）**：兼容旧草案与 1.0 schema（RFC 7489），以及最终 DMARC 标准 RFC 9989 的 RFC 9990 新 schema。
* **DMARC 失败报告（ruf，原取证报告）**：RFC 6591 与 RFC 9991 两种格式。
* **SMTP TLS 报告**：RFC 8460（TLS-RPT）的 TLS 报告。

它可以从 IMAP 收件箱、Microsoft Graph 或 Gmail API 读取报告邮件，透明处理 gzip 或 zip 压缩附件，输出一致的 JSON/CSV 数据结构；可选将结果发送至 Elasticsearch、OpenSearch、Splunk、PostgreSQL（配合预置仪表盘），也可输出至 Apache Kafka、Amazon S3、Azure Log Analytics（Microsoft Sentinel）、Graylog（GELF）、syslog 或 HTTP webhook。

## 2. 与商业服务的对比定位

商业 DMARC 报告服务（Dmarcian、EasyDMARC、PowerDMARC 等）的核心价值是「解析报告 + 可视化解读」。自托管 parsedmarc 用开源组件复刻了这条链路：

| 能力 | 商业 SaaS | parsedmarc 自托管 |
| --- | --- | --- |
| 解析 rua/ruf 报告 | 内置 | 内置（含 RFC 9990/9991 新格式） |
| TLS-RPT 处理 | 部分支持 | 内置（RFC 8460） |
| 可视化 | 云端仪表盘 | Kibana/Splunk 仪表盘 |
| 数据主权 | 报告送第三方 | 完全本地 |
| 运维成本 | 订阅费 | 服务器 + Elasticsearch 资源 |

选择自托管的典型场景：报告数据敏感不愿外送（金融/政务）、已有 Elasticsearch 基础设施、批量域名需要无限制处理、或预算限制。商业服务的优势则是零运维与开箱即用的策略建议。

## 3. 安装 parsedmarc（Debian/Ubuntu）

### 3.1 系统依赖

parsedmarc 需要 Python 3.10 或更新版本。官方文档支持的版本为 3.10–3.14（3.14 需 imapclient≥3.1.0）。Debian 系安装依赖：

```
sudo apt-get install -y python3-pip python3-venv python3-dev libxml2-dev libxslt-dev
```

CentOS/RHEL/Rocky Linux 对应：`sudo dnf install -y python3 python3-pip python3-devel libxml2-devel libxslt-devel`。

### 3.2 创建专用系统用户与虚拟环境

官方推荐创建专用系统用户并以 `/opt/parsedmarc` 为家目录，使目录所有权正确：

```
sudo useradd --system --create-home --home-dir /opt/parsedmarc \
    --shell /usr/sbin/nologin --skel /dev/null parsedmarc
sudo -u parsedmarc python3 -m venv /opt/parsedmarc/venv
sudo -u parsedmarc /opt/parsedmarc/venv/bin/pip install --upgrade pip
sudo -u parsedmarc /opt/parsedmarc/venv/bin/pip install --upgrade parsedmarc
```

升级 parsedmarc 时重跑最后一条命令并重启服务即可。可选依赖：解析 Outlook .msg 文件需安装 `msgconvert`（Debian 系 `sudo apt-get install libemail-outlook-message-perl`）。

### 3.3 IP 地理数据库

parsedmarc 内置 IPinfo Lite 数据库（CC BY-SA 4.0），启动时自动从 GitHub 刷新（watch 模式下收到 SIGHUP 也刷新），设置 `offline` 标志可禁用。默认无需任何 IP 数据库配置。若偏好 MaxMind GeoLite2，需在配置中显式指定 `ip_db_path`（自某版本起不再自动探测系统路径，以避免无关发行版包静默覆盖内置库导致 ASN 富化失效）。

## 4. 配置 parsedmarc

parsedmarc 6.0.0 起大部分 CLI 选项迁移至 INI 配置文件，用 `-c` 指定：

```
parsedmarc -c /etc/parsedmarc.ini
```

最小可用的 IMAP 监控配置示例（官方 example.ini 简化）：

```
[general]
save_aggregate = True
save_failure = True

[imap]
host = imap.example.com
user = dmarc@example.com
password = 你的密码

[mailbox]
watch = True
delete = False
```

输出至 Elasticsearch（配合 Kibana 仪表盘）时追加：

```
[elasticsearch]
hosts = 127.0.0.1:9200
ssl = False
```

其他输出目标（按需启用）：`[opensearch]`、`[splunk_hec]`（Splunk HEC）、`[s3]`、`[syslog]`、`[gelf]`（Graylog）、`[webhook]`（含 aggregate\_url/failure\_url/smtp\_tls\_url）。

## 5. 命令行解析报告文件

未配置邮箱监控时，可直接解析报告文件、邮件或目录：

```
parsedmarc -o /var/lib/parsedmarc/output report.xml.gz
parsedmarc -r -o /var/lib/parsedmarc/output /var/spool/dmarc/
```

常用选项：`-r` 递归扫描目录；`-o` 输出目录（JSON/CSV 文件写入处）；`--aggregate-json-filename` / `--failure-json-filename` 自定义输出文件名；`--offline` 不做在线地理定位/DNS 查询；`--no-prettify-json` 单行输出 JSON；`-n` 指定 DNS 服务器；`-t` 设置 DNS 超时（默认 2.0 秒）；`--dns-retries` 设置重试次数。设置 `archive_directory` 后，成功处理的报告文件会被移动到 `<archive_directory>/<年>/<月>/<Aggregate|Failure|SMTP-TLS>/`。

## 6. 接入 DMARC 报告流

让解析器收到报告的第一步是把 DMARC 记录的 `rua`（聚合）与 `ruf`（失败）指向专属邮箱：

```
v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com; ruf=mailto:dmarc@example.com; fo=1
```

官方文档提示：如需并行测试两个报告解析方案，rua/ruf 标签中可用逗号分隔最多两个 mailto URI。若邮件服务器是 Microsoft Exchange，需确保补丁不低于 Exchange 2010 UR22（KB4295699）/ 2013 CU21（KB4099855）/ 2016 CU11（KB4134118）。

部署在代理后的系统需在 `/etc/environment` 配置 `http_proxy` / `https_proxy` 环境变量，parsedmarc 才会通过代理访问外部服务。

## 7. 监控与可视化

watch 模式下（`[mailbox] watch = True`），parsedmarc 周期性检查配置的 IMAP 邮箱，新报告到达即自动解析入库。数据写入 Elasticsearch 后，官方提供 Kibana 仪表盘（docs/source/kibana.md）展示：

* DMARC 合规总览：按域、按日期的通过率趋势。
* 来源 IP 聚合：识别未授权发送源与可能仿冒域名的服务器。
* 对齐分析：SPF/DKIM 对齐比例，定位未对齐的合法发件通道。
* 失败样本：ruf 报告中的具体消息头部（strip\_attachment\_payloads 可去除附件载荷）。
* TLS-RPT 视图：TLS 失败类型分布（证书问题/协商失败等）。

推荐将 Kibana 仪表盘与 ztpop.net 的 [DMARC XML 报告解析器](/tools/dmarc-xml-parser.html) 配合使用：前者做持续监控与历史趋势，后者适合对单份报告做快速人工核查。单次快速验证也可以用 [SPF 深度诊断](/tools/spf-deep-diagnose.html) 与 [域名健康评分](/tools/domain-health-score.html) 确认认证记录本身是否正确。

## 8. 常见问题

**Q：parsedmarc 需要 Elasticsearch 才能用吗？** 不需要。最小部署只解析并输出 JSON/CSV 文件；Elasticsearch/OpenSearch/Splunk/PostgreSQL 是可选的可视化后端。

**Q：rua 和 ruf 报告格式有什么不同？** rua 聚合报告是 XML（gzip/zip 压缩），汇总一段时间内的认证结果统计；ruf 失败报告是原始消息样本（通常含附件），用于分析具体失败原因。parsedmarc 对两者输出统一结构的数据。

**Q：能处理 RFC 9990/9991 新格式吗？** 能。parsedmarc 已支持最终 DMARC 标准（RFC 9989）对应的 RFC 9990 聚合报告 schema 与 RFC 9991 失败报告格式，以及旧版草案格式。

**Q：报告邮箱用什么协议接入？** IMAP（imapclient）、Microsoft Graph 与 Gmail API 三种方式均可；邮件服务器为 Exchange 时需满足官方列出的最低补丁版本。

**Q：数据安全如何保证？** 完全自托管意味着报告与解析结果不出本地网络；生产环境建议为 Elasticsearch 启用 TLS 与认证，并用专用低权限邮箱账号收取报告。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/parsedmarc-self-hosted-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
