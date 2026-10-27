#!/usr/bin/env python3
import os, glob, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm import parse
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED={"idea","researching","drafting","imaged","video","published","archived"}
REQ=["id","title","status","type","created","updated"]
errors=[]
manifest=set()
mp=os.path.join(root,"assets/manifest.jsonl")
if os.path.exists(mp):
    for line in open(mp,encoding="utf-8"):
        if line.strip(): manifest.add(json.loads(line)["url"])
for p in glob.glob(os.path.join(root,"topics/*.md"))+glob.glob(os.path.join(root,"articles/*.md")):
    d,_=parse(open(p,encoding="utf-8").read())
    req = ["id","topic_id","title","status","created","updated"] if "topic_id" in d else REQ
    for k in req:
        if not d.get(k): errors.append(f"{p}: 缺少 {k}")
    if d.get("status") and "topic_id" not in d and d["status"] not in ALLOWED: errors.append(f"{p}: 状态非法 {d['status']}")
    if d.get("status")=="published" and not d.get("published_url"): errors.append(f"{p}: published 无 published_url")
    for u in (d.get("assets") or []):
        if u and u not in manifest: errors.append(f"{p}: assets 未登记 {u}")
src_ids={}
for p in glob.glob(os.path.join(root,"sources/*.md")):
    if os.path.basename(p)=="README.md": continue
    d,_=parse(open(p,encoding="utf-8").read())
    for k in ["id","topic_id","url","source_type","captured_at"]:
        if not d.get(k): errors.append(f"{p}: 信息源缺少 {k}")
    if d.get("id"): src_ids[d["id"]]=d
topic_ids={parse(open(p,encoding="utf-8").read())[0].get("id") for p in glob.glob(os.path.join(root,"topics/*.md"))}
for sid,d in src_ids.items():
    if d.get("topic_id") not in topic_ids: errors.append(f"sources/{sid}.md: topic_id 不存在 {d.get('topic_id')}")
for p in glob.glob(os.path.join(root,"topics/*.md")):
    d,_=parse(open(p,encoding="utf-8").read())
    for sid in (d.get("sources") or []):
        if sid not in src_ids: errors.append(f"{p}: sources 登记了不存在的信息源 {sid}")
        elif src_ids[sid].get("topic_id") != d.get("id"): errors.append(f"{p}: 信息源 {sid} 的 topic_id 对不上")
import re as _re, fnmatch as _fn
SECRET_PATTERNS=[_re.compile(r"AKIA[0-9A-Z]{16}"), _re.compile(r"ghp_[A-Za-z0-9]{30,}"), _re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), _re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")]
BAD_NAMES=(".env","*.pem","*.key","credentials*")
for dirpath,_,files in os.walk(root):
    if ".git" in dirpath or "assets-staging" in dirpath: continue
    for fn in files:
        fp=os.path.join(dirpath,fn); base=os.path.basename(fp)
        if base!=".env.example" and any(_fn.fnmatch(base,p_) for p_ in BAD_NAMES): errors.append(f"{fp}: 疑似密钥文件不应进仓")
        if base==".env" or (base.startswith(".env.") and base!=".env.example"): errors.append(f"{fp}: .env 文件不应进仓")
        try: txt=open(fp,encoding="utf-8",errors="strict").read()
        except Exception: continue
        for pat in SECRET_PATTERNS:
            if pat.search(txt): errors.append(f"{fp}: 命中密钥样式 {pat.pattern[:18]}...，立即移除并轮换该密钥")
for dirpath,_,files in os.walk(root):
    if ".git" in dirpath or "assets-staging" in dirpath: continue
    for fn in files:
        fp=os.path.join(dirpath,fn)
        if os.path.getsize(fp) > 5*1024*1024: errors.append(f"{fp}: 超过 5MB，大文件应放对象存储")
if errors:
    print("VALIDATE FAILED:"); [print(" -",e) for e in errors]; sys.exit(1)
print("VALIDATE OK")
