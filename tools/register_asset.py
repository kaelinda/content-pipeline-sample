#!/usr/bin/env python3
import argparse, os, json, hashlib, datetime
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--topic", required=True); ap.add_argument("--type", required=True)
ap.add_argument("--url", required=True); ap.add_argument("--file", default="")
a = ap.parse_args()
sha=""
if a.file and os.path.exists(a.file):
    sha = hashlib.sha256(open(a.file,"rb").read()).hexdigest()
rec = {"topic_id":a.topic,"type":a.type,"url":a.url,"sha256":sha,"name":os.path.basename(a.file) if a.file else "","registered_at":datetime.date.today().isoformat()}
with open(os.path.join(root,"assets/manifest.jsonl"),"a",encoding="utf-8") as f: f.write(json.dumps(rec,ensure_ascii=False)+"\n")
print("registered", rec)
