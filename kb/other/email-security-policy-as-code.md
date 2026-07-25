---
title: "Email Security Policy as Code 实践：SPF/DKIM/DMARC/MTA-STS 策略代码化"
source: "https://ztpop.net/kb/email-security-policy-as-code.html"
license: CC-BY 4.0
---

# Email Security Policy as Code 实践：SPF/DKIM/DMARC/MTA-STS 策略代码化

## 1. Policy as Code 架构总览

将邮件安全策略代码化的核心思路是：将SPF、DKIM、DMARC、MTA-STS策略定义为代码（YAML/HCL/JSON），存储在Git仓库中，通过CI/CD管道自动部署到DNS提供商和邮件服务器，并通过自动化测试确保证书有效性和策略正确性。整体架构如下：

```
┌────────────────────────────────────────────────────────────────┐
│                    代码仓库 (Git)                                 │
│                                                                 │
│  ├── policies/                  邮件安全策略定义                    │
│  │   ├── spf/          SPF 策略（主域+子域）                       │
│  │   ├── dkim/         DKIM 公钥记录 + 选择器定义                   │
│  │   ├── dmarc/        DMARC 策略 + 聚合报告地址                    │
│  │   └── mta-sts/      MTA-STS 策略 + TLS 报告配置                │
│  ├── terraform/        Terraform 基础设施代码                      │
│  │   ├── dns/          DNS 记录（TXT, CNAME）                     │
│  │   └── servers/      邮件服务器配置                             │
│  ├── tests/            Policy 验证测试                            │
│  └── Makefile          CI/CD 编排流程                             │
└───────────────────────────┬────────────────────────────────────┘
                            │ commit → push
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                    CI/CD 管道 (GitHub Actions)                    │
│                                                                 │
│  Step 1: Lint       — 语法检查（yamllint, jsonlint, spf-verify)  │
│  Step 2: Validate   — 策略语义验证（10-lookup SPF限制、DKIM位长） │
│  Step 3: Plan       — Terraform plan 预览变更                    │
│  Step 4: DeployDNS  — 应用到DNS提供商                            │
│  Step 5: Verify     — 端到端验证（DNS传播+邮件投递测试）           │
│  Step 6: DeployMTA  — 部署到邮件服务器配置（如适用）               │
└────────────────────────────────────────────────────────────────┘
```

此架构参考了 BCP 177 (RFC 7502) [1] 对 DNS 安全运维最佳实践的指导，以及 RFC 7489 [2]（DMARC规范）和 RFC 8461 [3]（MTA-STS规范）中关于策略管理的治理要求。

## 2. 策略代码化设计

### 2.1 策略定义结构（YAML格式）

```
# policies/config.yaml — 邮件安全策略主配置文件

email_security:
  organization: "Example Corp"
  domain: "example.com"
  
  # 策略版本控制 — 用于审计和回退
  version: "v2.4.1"
  last_reviewed: "2026-07-15"
  owner: "security-team@example.com"

  spf:
    # SPF 版本标识
    version: "spf1"
    
    # 授权发送服务器
    include:
      - "_spf.example.com"       # 自有服务器
      - "spf.protection.outlook.com"  # Office 365
      - "spf.sendgrid.net"       # 第三方邮件服务
      - "spf.mandrillapp.com"    # 营销邮件
    
    # 授权的IPv4地址
    ip4:
      - "203.0.113.0/24"
      - "198.51.100.0/24"
    
    # 授权的IPv6地址
    ip6:
      - "2001:db8::/32"
    
    # 使所有其他服务器失败
    all: "-all"

  dkim:
    selectors:
      - name: "s1"
        description: "主签名选择器（Dovecot）"
        key_algorithm: "rsa-sha256"
        key_size: 2048
        key_file: "keys/s1-dkim-private.pem"
        domains:
          - "example.com"
          - "mail.example.com"
      
      - name: "s2"
        description: "第三方邮件服务选择器（SendGrid）"
        key_source: "managed"
        domains:
          - "example.com"

  dmarc:
    # DMARC 策略版本
    version: "DMARC1"
    
    # 策略（p=quarantine 过渡期，逐步提升到 p=reject）
    policy: "reject"
    subdomain_policy: "reject"
    percentage: 100
    
    # 聚合报告（RUA）
    aggregate_report_uri:
      - "mailto:dmarc-rua@example.com"
      - "mailto:dmarc@rua.agari.com"  # 第三方分析
    
    # 取证报告（RUF）
    forensic_report_uri:
      - "mailto:dmarc-ruf@example.com"
    
    # 报告间隔（秒）
    reporting_interval: 86400
    
    # 不对ADKIM失败的邮件进行SPF对齐检查
    adkim: "r"      # Relaxed
    aspf: "r"       # Relaxed

  mta_sts:
    # MTA-STS策略（RFC 8461）
    policy_id: "v1.0"
    
    # 允许的TLS发送方MTA
    mx:
      - "mx1.example.com"
      - "mx2.example.com"
      - "*.mail.protection.outlook.com"  # Office 365 MX
    
    # 模式：enforce/testing/none
    mode: "enforce"
    
    # 策略生效时长（秒）
    max_age: 86400      # 1 day — 建议谨慎设置，逐步升级

  tls_reporting:
    # TLS-RPT (RFC 8460) 配置
    rua:
      - "mailto:tls-report@example.com"
      - "https://tls-report.example.com/reports"
```

### 2.2 策略生成器（Python）

```
#!/usr/bin/env python3
"""policy_generator.py — 从YAML配置生成DNS记录"""

import yaml, dns.resolver, hashlib, base64, json
from pathlib import Path

class EmailSecurityPolicyGenerator:
    """邮件安全策略 DNS 记录生成器"""
    
    def __init__(self, config_path: str = "policies/config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.domain = self.config['email_security']['domain']
        self.records = []
    
    def generate_spf_record(self) -> str:
        """生成 SPF TXT 记录"""
        spf_cfg = self.config['email_security']['spf']
        parts = [f"v={spf_cfg['version']}"]
        
        for inc in spf_cfg.get('include', []):
            parts.append(f"include:{inc}")
        for ip4 in spf_cfg.get('ip4', []):
            parts.append(f"ip4:{ip4}")
        for ip6 in spf_cfg.get('ip6', []):
            parts.append(f"ip6:{ip6}")
        for redirect in spf_cfg.get('redirect', []):
            parts.append(f"redirect={redirect}")
        
        parts.append(spf_cfg['all'])
        return ' '.join(parts)
    
    def generate_dkim_records(self) -> list[dict]:
        """生成 DKIM DNS 记录"""
        records = []
        dkim_cfg = self.config['email_security']['dkim']
        
        for selector in dkim_cfg.get('selectors', []):
            if selector.get('key_source') == 'managed':
                continue  # 第三方管理，不生成DNS
            
            # 读取私钥并导出公钥
            key_path = Path(selector['key_file'])
            if key_path.exists():
                import subprocess
                result = subprocess.run(
                    ["openssl", "rsa", "-pubout", "-in", str(key_path)],
                    capture_output=True, text=True
                )
                pubkey_pem = result.stdout
                # 转换为 Base64 格式并移除 PEM 头尾
                pubkey_b64 = base64.b64encode(
                    base64.b64decode(
                        ''.join(pubkey_pem.strip().split('\n')[1:-1])
                    )
                ).decode()
            else:
                # 如果是首次生成，创建密钥对
                print(f"[WARN] 密钥文件 {key_path} 不存在，请先运行 ./generate_dkim_keys.sh")
                pubkey_b64 = ""
            
            dkim_record = {
                "name": f"{selector['name']}._domainkey.{self.domain}.",
                "type": "TXT",
                "value": f"v=DKIM1; k={selector['key_algorithm'].split('-')[0]}; p={pubkey_b64}"
            }
            records.append(dkim_record)
        
        return records
    
    def generate_dmarc_record(self) -> dict:
        """生成 DMARC DNS 记录"""
        dmarc_cfg = self.config['email_security']['dmarc']
        parts = [f"v={dmarc_cfg['version']}"]
        parts.append(f"p={dmarc_cfg['policy']}")
        parts.append(f"sp={dmarc_cfg.get('subdomain_policy', dmarc_cfg['policy'])}")
        parts.append(f"pct={dmarc_cfg.get('percentage', 100)}")
        
        rua = dmarc_cfg.get('aggregate_report_uri', [])
        if rua:
            parts.append(f"rua={' ,'.join(rua)}")
        
        ruf = dmarc_cfg.get('forensic_report_uri', [])
        if ruf:
            parts.append(f"ruf={' ,'.join(ruf)}")
        
        parts.append(f"ri={dmarc_cfg.get('reporting_interval', 86400)}")
        parts.append(f"adkim={dmarc_cfg.get('adkim', 'r')}")
        parts.append(f"aspf={dmarc_cfg.get('aspf', 'r')}")
        
        return {
            "name": f"_dmarc.{self.domain}.",
            "type": "TXT",
            "value": '; '.join(parts)
        }
    
    def generate_mta_sts_record(self) -> dict:
        """生成 MTA-STS DNS 记录"""
        sts_cfg = self.config['email_security']['mta_sts']
        return {
            "name": f"_mta-sts.{self.domain}.",
            "type": "TXT",
            "value": f"v=STSv1; id={sts_cfg['policy_id']}"
        }
    
    def generate_tls_report_record(self) -> dict:
        """生成 TLS-RPT DNS 记录"""
        tls_cfg = self.config['email_security'].get('tls_reporting', {})
        rua = tls_cfg.get('rua', [])
        if not rua:
            return None
        return {
            "name": f"_smtp._tls.{self.domain}.",
            "type": "TXT",
            "value": f"v=TLSRPTv1; rua={' ,'.join(rua)}"
        }
    
    def generate_mta_sts_policy_file(self) -> str:
        """生成 MTA-STS 策略文件（部署用于 .well-known/mta-sts.txt）"""
        sts_cfg = self.config['email_security']['mta_sts']
        lines = [
            f"version: {sts_cfg['policy_id']}",
        ]
        for mx in sts_cfg.get('mx', []):
            lines.append(f"mx: {mx}")
        lines.append(f"mode: {sts_cfg['mode']}")
        lines.append(f"max_age: {sts_cfg['max_age']}")
        return '\n'.join(lines) + '\n'
    
    def generate_all(self) -> dict:
        """生成所有 DNS 记录"""
        return {
            "spf": {
                "name": f"{self.domain}.",
                "type": "TXT",
                "value": self.generate_spf_record()
            },
            "dkim": self.generate_dkim_records(),
            "dmarc": self.generate_dmarc_record(),
            "mta_sts_dns": self.generate_mta_sts_record(),
            "tls_report": self.generate_tls_report_record(),
            "mta_sts_policy": self.generate_mta_sts_policy_file()
        }

if __name__ == '__main__':
    gen = EmailSecurityPolicyGenerator()
    records = gen.generate_all()
    
    # 输出所有 DNS 记录
    for key, record in records.items():
        if isinstance(record, list):
            for r in record:
                print(f"{r['name']} → {r['type']} = {r['value'][:80]}...")
        elif record:
            print(f"{record['name']} → {record['type']} = {record['value'][:80]}...")
    
    # 输出 MTA-STS 策略文件
    with open("mta-sts.txt", "w") as f:
        f.write(records['mta_sts_policy'])
    print("\nMTA-STS 策略文件已写入 mta-sts.txt")
```

## 3. Terraform DNS 资源管理

### 3.1 使用 Terraform 管理邮件安全 DNS 记录

Terraform 将 DNS 提供商视为数据源和目标。以下示例使用 AWS Route53 作为 DNS 提供商，原理适用于任何支持 Terraform Provider 的 DNS 服务（阿里云 DNS、腾讯云 DNSPod、Cloudflare 等）：

```
# terraform/dns/main.tf — 邮件安全策略 DNS 记录管理

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  # 使用环境变量: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
}

data "aws_route53_zone" "main" {
  name         = var.domain
  private_zone = false
}

# ---- SPF 记录 ----
resource "aws_route53_record" "spf" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain
  type    = "TXT"
  ttl     = 300
  
  records = [
    var.spf_record
  ]

  lifecycle {
    # 确保 SPF 记录不超过 DNS 单条限制（255字符）
    # 超过时需拆分为多个记录，但 RFC 7208 [4] 要求一次性查询
    precondition {
      condition     = length(var.spf_record) <= 255
      error_message = "SPF 记录超出 255 字符限制，需使用 include 拆分"
    }
  }
}

# ---- DKIM 公钥记录 ----
resource "aws_route53_record" "dkim" {
  for_each = var.dkim_selectors
  
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${each.key}._domainkey.${var.domain}"
  type    = "TXT"
  ttl     = 300
  
  records = [
    "v=DKIM1; k=${each.value.key_type}; p=${each.value.public_key}"
  ]
}

# ---- DMARC 记录 ----
resource "aws_route53_record" "dmarc" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "_dmarc.${var.domain}"
  type    = "TXT"
  ttl     = 300
  
  records = [
    var.dmarc_record
  ]
}

# ---- MTA-STS DNS 记录（策略ID指针）----
resource "aws_route53_record" "mta_sts" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "_mta-sts.${var.domain}"
  type    = "TXT"
  ttl     = 300
  
  records = [
    "v=STSv1; id=${var.mta_sts_policy_id}"
  ]
}

# ---- TLS-RPT（RFC 8460）记录 ----
resource "aws_route53_record" "tls_report" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "_smtp._tls.${var.domain}"
  type    = "TXT"
  ttl     = 300
  
  records = [
    "v=TLSRPTv1; rua=${var.tls_report_uri}"
  ]
}
```

```
# terraform/dns/variables.tf — 变量定义

variable "domain" {
  description = "主域名"
  type        = string
}

variable "spf_record" {
  description = "SPF TXT 记录值"
  type        = string
  sensitive   = false
}

variable "dkim_selectors" {
  description = "DKIM 选择器配置"
  type = map(object({
    key_type   = string
    public_key = string
  }))
}

variable "dmarc_record" {
  description = "DMARC TXT 记录值"
  type        = string
}

variable "mta_sts_policy_id" {
  description = "MTA-STS 策略版本ID"
  type        = string
  default     = "v1"
}

variable "tls_report_uri" {
  description = "TLS-RPT 报告接收地址"
  type        = string
  default     = "mailto:tls-report@example.com"
}
```

### 3.2 环境差异化配置

```
# terraform/dns/prod.auto.tfvars — 生产环境特定配置

domain       = "example.com"
mta_sts_policy_id = "v2"

spf_record = "v=spf1 include:_spf.example.com include:spf.protection.outlook.com -all"

dmarc_record = "v=DMARC1; p=reject; sp=reject; pct=100; rua=mailto:dmarc-rua@example.com; ri=86400"

dkim_selectors = {
  "s1" = {
    key_type   = "rsa"
    public_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD..."
  }
  "s2" = {
    key_type   = "ed25519"
    public_key = "MCowBQYDK2VwAyEA..."
  }
}

tls_report_uri = "mailto:tls-report@example.com"
```

```
# terraform/dns/staging.auto.tfvars — 预发环境

domain       = "staging.example.com"
mta_sts_policy_id = "v1"

# 预发环境的 DMARC 使用 p=none（仅监控）
spf_record = "v=spf1 include:_spf.staging.example.com -all"
dmarc_record = "v=DMARC1; p=none; sp=none; pct=100; rua=mailto:dmarc-staging@example.com"

dkim_selectors = {
  "s1" = {
    key_type   = "rsa"
    public_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD..."  # 测试密钥
  }
}

tls_report_uri = "mailto:tls-report-staging@example.com"
```

## 4. CI/CD 管道集成

### 4.1 GitHub Actions 工作流

```
# .github/workflows/email-security-policy.yml

name: Email Security Policy CI/CD

on:
  push:
    branches: [main, staging]
    paths:
      - 'policies/**'
      - 'terraform/**'
      - 'tests/**'
  pull_request:
    paths:
      - 'policies/**'
      - 'tests/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pyyaml dnspython
          sudo apt-get install -y swaks jq
      
      - name: Lint YAML configuration
        run: |
          yamllint policies/config.yaml
      
      - name: Validate SPF record
        run: |
          python3 tests/validate_spf.py
      
      - name: Validate DKIM key length
        run: |
          python3 tests/validate_dkim.py
      
      - name: Validate DMARC policy
        run: |
          python3 tests/validate_dmarc.py
      
      - name: Validate MTA-STS policy
        run: |
          python3 tests/validate_mta_sts.py

  terraform-plan:
    runs-on: ubuntu-latest
    needs: validate
    environment: terraform-plan
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.7.0
      
      - name: Terraform Init
        run: terraform init
        working-directory: terraform/dns
      
      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: terraform/dns
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      
      - name: Upload TF plan
        uses: actions/upload-artifact@v4
        with:
          name: tfplan
          path: terraform/dns/tfplan

  deploy-dns:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    needs: terraform-plan
    environment: production-dns
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.7.0
      
      - name: Terraform Apply
        run: terraform apply -auto-approve tfplan
        working-directory: terraform/dns
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  
  verify-deployment:
    runs-on: ubuntu-latest
    needs: deploy-dns
    steps:
      - name: Wait for DNS propagation
        run: sleep 120  # 等待DNS传播（TTL 300s）
      
      - name: Verify SPF
        run: |
          dig TXT example.com +short | grep "v=spf1" || echo "SPF 验证失败"
      
      - name: Verify DKIM
        run: |
          dig TXT s1._domainkey.example.com +short | grep "v=DKIM1" || echo "DKIM 验证失败"
      
      - name: Verify DMARC
        run: |
          dig TXT _dmarc.example.com +short | grep "v=DMARC1" || echo "DMARC 验证失败"
      
      - name: End-to-end mail delivery test
        run: |
          # 使用 swaks 发送测试邮件到验证邮箱
          swaks --to email-test@example.com \
            --from test@example.com \
            --server smtp.example.com \
            --auth LOGIN \
            --auth-user test@example.com \
            --header-X-Test-ID "CI-$(date +%s)" \
            --body "Policy deployment verification test $(date)"
```

## 5. 自动化验证测试

### 5.1 SPF 验证

```
#!/usr/bin/env python3
# tests/validate_spf.py — SPF 策略验证

import dns.resolver
import sys

def validate_spf(domain: str):
    """验证 SPF 记录是否符合最佳实践"""
    errors = []
    warnings = []
    
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
    except dns.resolver.NoAnswer:
        errors.append(f"未找到 {domain} 的 TXT 记录")
        return errors, warnings
    
    spf_records = []
    for rdata in answers:
        txt = rdata.to_text().strip('"')
        if txt.startswith('v=spf1'):
            spf_records.append(txt)
    
    if len(spf_records) == 0:
        errors.append("未找到 SPF 记录！")
    elif len(spf_records) > 1:
        # RFC 7208 [4] 规定 SPF 记录只能有一条
        errors.append("存在多条 SPF 记录（超过1条）")
    
    for record in spf_records:
        # 检查 -all（必须）
        if not record.endswith('-all') and not record.endswith('~all'):
            warnings.append("SPF 策略未使用 -all（硬失败），建议从 ~all 升级到 -all")
        
        # 检查 DNS 查询次数限制（RFC 7208 限制为10次）
        lookup_count = record.count('include:') + record.count('a:') + record.count('mx:')
        import re
        ip4_count = len(re.findall(r'ip4:', record))
        ip6_count = len(re.findall(r'ip6:', record))
        
        if lookup_count > 10:
            errors.append(f"SPF DNS 查询次数 {lookup_count} 超过 RFC 7208 10次限制")
        
        # 检查单条记录长度
        if len(record) > 255:
            errors.append(f"SPF 记录长度 {len(record)} 超过 255 字符")
    
    return errors, warnings

if __name__ == '__main__':
    import yaml
    with open('policies/config.yaml') as f:
        config = yaml.safe_load(f)
    domain = config['email_security']['domain']
    
    errors, warnings = validate_spf(domain)
    
    for e in errors:
        print(f"[ERROR] {e}")
    for w in warnings:
        print(f"[WARN] {w}")
    
    if errors:
        sys.exit(1)
    print(f"[OK] SPF 策略验证通过 ({domain})")
```

### 5.2 DMARC 验证

```
#!/usr/bin/env python3
# tests/validate_dmarc.py — DMARC 策略验证

import dns.resolver, yaml, sys, re

def validate_dmarc(domain: str):
    errors = []
    warnings = []
    
    dmarc_domain = f"_dmarc.{domain}"
    
    try:
        answers = dns.resolver.resolve(dmarc_domain, 'TXT')
    except dns.resolver.NoAnswer:
        errors.append(f"未找到 DMARC 记录")
        return errors, warnings
    except dns.resolver.NXDOMAIN:
        errors.append(f"DMARC 域名 {dmarc_domain} 不存在")
        return errors, warnings
    
    for rdata in answers:
        txt = rdata.to_text().strip('"')
        if not txt.startswith('v=DMARC1'):
            continue
        
        # 解析 DMARC 标记
        tags = dict()
        for kv in txt.split(';'):
            kv = kv.strip()
            if '=' not in kv:
                continue
            k, v = kv.split('=', 1)
            tags[k.strip()] = v.strip()
        
        # 验证策略值
        policy = tags.get('p', 'none')
        if policy == 'none':
            warnings.append("DMARC 策略为 p=none（仅监控模式）")
        elif policy == 'quarantine':
            warnings.append("DMARC 策略为 p=quarantine（建议逐步升级到 p=reject）")
        elif policy not in ('reject',):
            errors.append(f"无效的 DMARC 策略值: {policy}")
        
        # 验证 RUA 地址存在
        if 'rua' not in tags:
            warnings.append("DMARC 未配置 RUA（聚合报告）地址")
        
        # 验证 RUA 地址格式
        if 'rua' in tags:
            rua = tags['rua']
            # 格式必须为 mailto: 开头
            if not rua.startswith('mailto:'):
                errors.append(f"RUA 格式不正确（需 mailto: 前缀）: {rua}")
        
        # 验证百分比
        pct = int(tags.get('pct', '100'))
        if pct < 100 and policy == 'reject':
            warnings.append(f"p=reject 但 pct={pct} 意味着并非100%流量强制执行")
        
        # 验证报告间隔
        ri = int(tags.get('ri', '86400'))
        if ri < 3600:
            warnings.append(f"报告间隔 ri={ri} 过短（建议≥3600秒）")
    
    return errors, warnings

if __name__ == '__main__':
    with open('policies/config.yaml') as f:
        config = yaml.safe_load(f)
    domain = config['email_security']['domain']
    
    errors, warnings = validate_dmarc(domain)
    
    for e in errors:
        print(f"[ERROR] {e}")
    for w in warnings:
        print(f"[WARN] {w}")
    
    if errors:
        sys.exit(1)
    print(f"[OK] DMARC 策略验证通过 ({domain})")
```

## 6. 通过DNS作为数据源的差异化配置

一种轻量级的策略代码化方法是直接将 DNS 作为"数据源"和"配置存储"——通过 TXT 记录中的结构化编码，让邮件服务器动态从 DNS 读取其安全策略，无需重新部署邮件服务器软件。RFC 8616 [5]（SMTP email auto-configuration）描述了通过 DNS 自动发现配置的概念。以下是一个示例方案：

```
#!/bin/bash
# dns_policy_discovery.sh — 从DNS发现邮件安全策略并应用

DOMAIN="example.com"

echo "=== 从 DNS 发现邮件安全策略 ==="

# 1. 读取 MTA-STS 策略
echo ""
echo "--- MTA-STS 策略 ---"
dig _mta-sts.$DOMAIN TXT +short

# 2. 检查 SPF 记录
echo ""
echo "--- SPF 记录 ---"
dig $DOMAIN TXT +short | grep "v=spf1"

# 3. 检查 DMARC 记录
echo ""
echo "--- DMARC 记录 ---"
dig _dmarc.$DOMAIN TXT +short

# 4. 检查 TLS-RPT
echo ""
echo "--- TLS-RPT 记录 ---"
dig _smtp._tls.$DOMAIN TXT +short

# 5. 验证一致性 — DNS数据源模式
# 通过定期DNS查询，将结果与代码仓库中的期望值对比
echo ""
echo "--- 策略一致性验证 ---"
python3 <<'PYCHECK'
import dns.resolver, json

domain = "example.com"

# 期望值从策略定义文件读取
with open("tests/expected_records.json") as f:
    expected = json.load(f)

# 检查 SPF
spf = dns.resolver.resolve(domain, 'TXT')
spf_value = ' '.join([r.to_text().strip('"') for r in spf if 'v=spf1' in r.to_text()])
if spf_value == expected['spf']:
    print(f"[OK] SPF 与期望一致")
else:
    print(f"[CHANGED] SPF 不一致")
    print(f"  DNS: {spf_value[:60]}...")
    print(f"  Git: {expected['spf'][:60]}...")

# 检查 DMARC
dmarc = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
dmarc_value = '; '.join([r.to_text().strip('"') for r in dmarc if 'v=DMARC1' in r.to_text()])
print(f"  实际: {dmarc_value[:80]}")
PYCHECK
```

## 参考文献

1. **BCP 177 / RFC 7502** — DNS Best Current Practices，P. Hoffman et al.，2015，https://datatracker.ietf.org/doc/html/rfc7502
2. **RFC 7489** — Domain-based Message Authentication, Reporting, and Conformance (DMARC)，M. Kucherawy & E. Zwicky，2015，https://datatracker.ietf.org/doc/html/rfc7489
3. **RFC 8461** — SMTP MTA Strict Transport Security (MTA-STS)，M. Dahlberg et al.，2018，https://datatracker.ietf.org/doc/html/rfc8461
4. **RFC 7208** — Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1，S. Kitterman，2014，https://datatracker.ietf.org/doc/html/rfc7208
5. **RFC 8616** — Email Autoconfiguration with DNS，C. Holstead et al.，2019，https://datatracker.ietf.org/doc/html/rfc8616
6. **RFC 8460** — SMTP TLS Reporting (TLS-RPT)，M. Kucherawy et al.，2018，https://datatracker.ietf.org/doc/html/rfc8460

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-security-policy-as-code.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
