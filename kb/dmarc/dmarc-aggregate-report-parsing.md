---
title: "DMARC Aggregate Report 人工解析与监控完全指南：rua XML结构、parsedmarc与dmarcian"
source: "https://ztpop.net/kb/dmarc-aggregate-report-parsing.html"
license: CC-BY 4.0
---

# DMARC Aggregate Report 人工解析与监控完全指南：rua XML结构、parsedmarc与dmarcian

## 1. DMARC聚合报告概览

### 1.1 数据流路径

DMARC（RFC 7489）定义了两种反馈报告：聚合报告（Aggregate Report, RUA）和法证报告（Forensic Report, RUF/RFC 9991）[1]。聚合报告以XML格式由接收MTA定期（通常每日）汇总发送至DMARC记录中rua标签指定的地址。数据流：发件域配置rua=mailto:dmarc-rua@example.com → 接收MTA收集24小时内所有发件域为example.com的邮件认证结果 → 打包为gzip压缩的XML → 发送至rua邮箱 → 域所有者解析 [1] [2]。

### 1.2 报告发送约束

接收MTA的聚合报告生成受DMARC策略中的pct字段影响：pct=100表示对100%的邮件生成报告（默认值），pct=50表示仅对50%的邮件抽样生成。域所有者可通过pct分阶段部署策略实现渐进式监控 [1] §6.4。

## 2. XML Schema 逐字段解析

### 2.1 根节点结构

```
<?xml version="1.0" encoding="UTF-8"?>
<feedback>
  <report_metadata>...</report_metadata>
  <policy_published>...</policy_published>
  <record>...</record>  <!-- 每发件源IP一条 -->
</feedback>
```

### 2.2 report\_metadata — 报告元信息

```
<report_metadata>
  <org_name>google.com</org_name>  <!-- 报告生成方 -->
  <email>noreply-dmarc-support@google.com</email>
  <extra_contact_info>https://support.google.com/a/answer/2466580</extra_contact_info>
  <report_id>20260724080000.12345@google.com</report_id>
  <date_range>
    <begin>1761264000</begin>  <!-- Unix时间戳，该报告覆盖的起始时间 -->
    <end>1761350399</end>    <!-- 结束时间（24h窗口） -->
  </date_range>
</report_metadata>
```

`org_name`指示谁生成的报告——Gmail为google.com，Outlook为outlook.com，腾讯为企业邮箱为exmail.qq.com。关键陷阱：有些接收方使用多个org\_name（如谷歌的多个数据中心可能以不同org\_name发送），需合并去重 [1]。

### 2.3 policy\_published — 发布的策略

```
<policy_published>
  <domain>example.com</domain>
  <adkim>r</adkim>  <!-- DKIM对齐模式: r=relaxed, s=strict -->
  <aspf>r</aspf>    <!-- SPF对齐模式: r=relaxed, s=strict -->
  <p>reject</p>    <!-- 父域策略 -->
  <sp>reject</sp>  <!-- 子域策略（可选） -->
  <pct>100</pct>   <!-- 抽样百分比 -->
  <fo>0</fo>       <!-- 法证报告选项 -->
</policy_published>
```

注意：`p`字段显示的是发布策略，而非实际执行策略。如果接收方因自身配置原因无法执行reject策略（如客户要求宽松），实际执行策略在policy\_evaluated中体现 [1] §7.7。

### 2.4 record + row — 认证结果核心

```
<record>
  <row>
    <source_ip>203.0.113.5</source_ip>
    <count>245</count>  <!-- 该IP的邮件数量 -->
    <policy_evaluated>
      <disposition>none</disposition>  <!-- none/quarantine/reject -->
      <dkim>pass</dkim>   <!-- pass/fail -->
      <spf>fail</spf>     <!-- pass/fail -->
    </policy_evaluated>
  </row>
  <identifiers>
    <header_from>example.com</header_from>  <!-- From头域 -->
    <envelope_from>example.com</envelope_from>  <!-- MAIL FROM -->
    <envelope_to>recipient@other.com</envelope_to>
  </identifiers>
  <auth_results>
    <dkim>
      <domain>example.com</domain>
      <result>pass</result>
      <selector>default</selector>
    </dkim>
    <spf>
      <domain>example.com</domain>
      <result>fail</result>  <!-- none/neutral/pass/fail/softfail/temperror/permerror -->
    </spf>
  </auth_results>
</record>
```

#### 2.4.1 policy\_evaluated 解读

`disposition`是该批邮件的实际执行动作：`none`（仅监控不操作）、`quarantine`（标记为垃圾邮件）、`reject`（拒收）。`dkim`和`spf`字段表示是否通过了相应认证，二者任意pass即DMARC pass。解析时的关键指标：`dkim:fail + spf:fail + disposition:none`表示DMARC完全失败的邮件但未被处理，需要立即关注；`disposition:reject + spf:fail dkim:pass`表示虽然DKIM通过但SPF未对齐且配置为strict对齐，导致DMARC失败。

#### 2.4.2 auth\_results vs policy\_evaluated 的区别

`auth_results`报告的是原始SPF和DKIM的验证结果（包含所有被验证的域名），而`policy_evaluated`仅报告与From域对齐后的结果。例如：SPF验证结果为pass但使用的域为send.thirdparty.com，而From域为example.com，<spf><result>pass</result><domain>send.thirdparty.com</domain></spf>，但policy\_evaluated中的spf=pass仅当SPF通过且与From域对齐 [1] §3.1.1。

## 3. 纯手动解析 XML 报告（无外部工具）

### 3.1 解压与基础统计

```
# DMARC报告以gzip压缩的附件形式发送至rua邮箱
# 下载附件后解压
gzip -d google-com!example.com!1761264000!1761350399.xml.gz

# 使用 xmllint 或 Python 快速统计
xmllint --xpath "count(//feedback/record)" report.xml
# 输出：42 条记录

# 统计按策略结果分组
xmllint --xpath "//policy_evaluated/disposition/text()" report.xml \
  | sort | uniq -c
# 39 none  2 quarantine  1 reject

# 统计 pass/fail 比例
xmllint --xpath "//policy_evaluated/dkim/text()" report.xml \
  | sort | uniq -c
# 40 pass  2 fail
```

### 3.2 Python 解析脚本基础

```
#!/usr/bin/env python3
"""快速解析 DMARC 聚合报告"""
import xml.etree.ElementTree as ET

tree = ET.parse('report.xml')
ns = ''  # DMARC XML 无默认命名空间

total_records = 0
total_volume = 0
fail_volume = 0

for record in tree.findall('feedback/record'):
    total_records += 1
    count = int(record.findtext('row/count', '0'))
    total_volume += count
    dkim = record.findtext('row/policy_evaluated/dkim', 'unknown')
    spf = record.findtext('row/policy_evaluated/spf', 'unknown')
    if dkim == 'fail' and spf == 'fail':
        fail_volume += count

print(f"记录数: {total_records}")
print(f"邮件总量: {total_volume}")
print(f"DMARC失败量: {fail_volume} ({fail_volume/total_volume*100:.1f}%)")

# 提取失败源IP
for record in tree.findall('feedback/record'):
    dkim = record.findtext('row/policy_evaluated/dkim', 'unknown')
    spf = record.findtext('row/policy_evaluated/spf', 'unknown')
    if dkim == 'fail' and spf == 'fail':
        ip = record.findtext('row/source_ip', 'unknown')
        count = record.findtext('row/count', '0')
        print(f"  失败源IP: {ip} ({count}封)")
```

### 3.3 批量处理多个.gz报告

```
# 解压所有报告
for f in *.gz; do gzip -d "$f"; done

# 合并为一个CSV用于Excel分析（使用xsltproc或Python）
python3 << 'EOF'
import gzip, io, xml.etree.ElementTree as ET, glob, csv

with open('dmarc_report.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['org','report_id','begin','end','domain','sp_policy','dkim_p','spf_p',
                'source_ip','count','disposition','dkim_auth','spf_auth','header_from'])
    for gz in glob.glob('*.gz'):
        with gzip.open(gz, 'rt', encoding='utf-8') as fh:
            try:
                root = ET.fromstring(fh.read())
            except:
                continue
        meta = root.find('feedback/report_metadata')
        org = meta.findtext('org_name','')
        rid = meta.findtext('report_id','')
        begin = meta.findtext('date_range/begin','')
        end_ = meta.findtext('date_range/end','')
        pp = root.find('feedback/policy_published')
        domain = pp.findtext('domain','')
        sp_pol = pp.findtext('sp','')
        for record in root.findall('feedback/record'):
            ip = record.findtext('row/source_ip','')
            c = record.findtext('row/count','0')
            disp = record.findtext('row/policy_evaluated/disposition','')
            dk = record.findtext('row/policy_evaluated/dkim','')
            sp = record.findtext('row/policy_evaluated/spf','')
            hf = record.findtext('identifiers/header_from','')
            dk_res = record.findtext('auth_results/dkim/result','')
            sp_res = record.findtext('auth_results/spf/result','')
            w.writerow([org,rid,begin,end_,domain,sp_pol,dk,sp,ip,c,disp,dk_res,sp_res,hf])
print("CSV generated: dmarc_report.csv")
EOF
```

## 4. 自动化监控栈：parsedmarc + Elasticsearch + Grafana

### 4.1 parsedmarc 部署

```
# parsedmarc 是最主流的DMARC报告解析工具
# GitHub: https://github.com/domainaware/parsedmarc

# 安装
pip3 install parsedmarc

# 配置 /etc/parsedmarc.ini
[general]
imap_host = imap.example.com
imap_port = 993
imap_ssl = True
imap_user = dmarc-rua@example.com
imap_password = S3cur3P@ss
save_aggregate = True
save_forensic = True
save_mbox = False
# 存储至Elasticsearch
elasticsearch_host = 127.0.0.1
elasticsearch_port = 9200
elasticsearch_use_ssl = False
# 排除自身报告（避免循环）
filter_domains = []
filter_org_domains = []
# GeoIP 数据库（可选）
geoipdb_path = /usr/share/GeoIP/GeoLite2-City.mmdb

[elasticsearch]
index_prefix = dmarc
# 自动创建索引
create_ilm = True
index_suffix = history
```

### 4.2 Elasticsearch + Kibana 可视化

```
# parsedmarc 运行后自动创建索引
parsedmarc --config /etc/parsedmarc.ini

# 定时执行（crontab）
# 每6小时解析一次
0 */6 * * * /usr/local/bin/parsedmarc --config /etc/parsedmarc.ini

# 查询 Elasticsearch
curl -X GET "localhost:9200/dmarc_*/_search?q=disposition:reject&size=0"

# Kibana 创建仪表盘的关键字段
# - disposition: none / quarantine / reject
# - dkim_result / spf_result 按域聚合
# - source_ip 按地理位置聚合（需GeoIP）
# - header_from 按域分析
```

### 4.3 Grafana 监控面板

配置Grafana连接Elasticsearch数据源后，关键面板：① DMARC失败率趋势图（按天统计pass/fail比例）；② 按接收方（org\_name）分类的认证结果堆叠图；③ 失败源IP Top N表格；④ pct实施度仪表——检查是否有接收方因pct<100导致抽样偏差。

## 5. 常见异常诊断

### 5.1 子域未覆盖

症状：聚合报告中大量mail.example.com的认证失败，但example.com的策略正常。疑因DMARC记录的sp字段未设置，默认继承p值。明确设置sp=reject可以消除歧义。聚合报告中的policy\_published/sp字段显示实际的子域策略。

### 5.2 同一域名多个org\_name发送报告

Gmail和Google Workspace可能以google.com和googlemail.com两个org\_name发送报告。Outlook/Office 365可能使用protection.outlook.com。需要在数据分析时合并同一发送者的报告，否则统计偏差。

### 5.3 pct偏差导致误判

如果pct=50，报告仅覆盖50%流量。假设今天报告显示100% pass，但可能未覆盖的50%恰好包含所有失败邮件。RFC 7489 §6.4警告这种抽样偏差。正式部署reject策略前，pct应从10→50→100逐步提升，每阶段观察7天以上 [1]。

### 5.4 报告缺失

并非所有接收MTA都发送聚合报告。常见缺失源：自建Postfix默认不发送DMARC报告（需配置OpenDMARC的AuthservID和ReportInfo）；小型ISP的MTA无DMARC实现；部分接收方以报告周期不一致为由延迟发送（长达72小时）。监控周期建议设置为1周而非1天以容忍延迟。

### 5.5 伪造报告的防护

聚合报告的XML文件理论上可被伪造。建议：① 只接收来自已知org\_name域的邮件（如google.com、outlook.com）；② DMARC记录中的rua格式支持rua=mailto:report@...!xx:xx的URI编码；③ 通过DKIM验证邮件来源的真实性（报告邮件应由接收方的DKIM签名）。

## 参考文献

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/dmarc-aggregate-report-parsing.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
