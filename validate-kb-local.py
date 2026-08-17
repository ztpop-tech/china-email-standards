#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地 KB 验证脚本：JSON-LD 合法性 + 标签配平 + 国内厂商词过滤。
用法: python validate-kb-local.py <file.html>
退出码 0=PASS, 1=FAIL
"""
import sys, json, re
from html.parser import HTMLParser

# 国内邮件厂商词（铁律28：零容忍）
FORBIDDEN = ["Coremail", "盈世", "U-Mail", "网际思安", "CACTER", "腾讯", "阿里",
             "网易", "中睿", "拓博", "腾讯企业邮", "阿里邮箱", "网易邮箱", "QQ邮箱",
             "foxmail", "Foxmail", "QQMail", "Exmail", "腾讯云邮件", "阿里云邮件推送"]

VOID = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}


class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"多余闭合 </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            # 弹出直到匹配（容错，记录警告）
            while self.stack and self.stack[-1] != tag:
                self.errors.append(f"未闭合 <{self.stack[-1]}> 在 </{tag}> 之前")
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.errors.append(f"无匹配开标签 </{tag}>")


def extract_jsonld(html):
    blocks = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        blocks.append(m.group(1))
    return blocks


def main():
    if len(sys.argv) < 2:
        print("用法: validate-kb-local.py <file.html>")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        html = f.read()

    ok = True
    # 1. JSON-LD 合法性
    blocks = extract_jsonld(html)
    for i, b in enumerate(blocks):
        try:
            json.loads(b)
        except Exception as e:
            print(f"[FAIL] JSON-LD #{i+1} 非法: {e}")
            ok = False
    if blocks:
        print(f"[PASS] JSON-LD 块数={len(blocks)} 全部合法")
    else:
        print("[WARN] 无 JSON-LD 块")

    # 2. 标签配平
    p = TagChecker()
    p.feed(html)
    if p.stack:
        print(f"[FAIL] 未闭合标签: {p.stack}")
        ok = False
    if p.errors:
        for e in p.errors[:20]:
            print(f"[FAIL] {e}")
        ok = False
    if not p.stack and not p.errors:
        print("[PASS] 标签配平正常")

    # 3. 国内厂商词过滤
    hits = [w for w in FORBIDDEN if w in html]
    if hits:
        print(f"[FAIL] 国内厂商词命中: {hits}")
        ok = False
    else:
        print("[PASS] 国内厂商词 0 命中")

    # 4. 严禁字样检查（KB-11 专用，全局都查以免误用）
    if "rfc9586" in html or "RFC9586" in html or "RFC 9586" in html:
        print("[FAIL] 出现禁止字样 rfc9586")
        ok = False

    print("==== " + ("ALL PASS" if ok else "VALIDATION FAILED") + " ====")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
