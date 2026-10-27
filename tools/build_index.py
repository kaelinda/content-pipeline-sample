#!/usr/bin/env python3
import os, glob, csv, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm import parse
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=[]
for p in sorted(glob.glob(os.path.join(root,"topics/*.md"))):
    d,_ = parse(open(p,encoding="utf-8").read()); d["file"]=os.path.relpath(p,root); rows.append(d)
os.makedirs(os.path.join(root,"index"),exist_ok=True)
fields=["id","title","status","type","platforms","source_count","owner_agent","updated","published_url","file"]
for r in rows: r["source_count"]=len(r.get("sources") or [])
with open(os.path.join(root,"index/topics.csv"),"w",newline="",encoding="utf-8") as f:
    wtr=csv.DictWriter(f,fieldnames=fields); wtr.writeheader()
    for r in rows: wtr.writerow({k: (", ".join(r.get(k,[])) if isinstance(r.get(k),list) else r.get(k,"")) for k in fields})
json.dump(rows, open(os.path.join(root,"index/index.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=2)
order=["idea","researching","drafting","imaged","video","published","archived"]
board=["# 选题看板（自动生成，勿手改）\n"]
for s in order:
    items=[r for r in rows if r.get("status")==s]
    if not items: continue
    board.append(f"## {s} ({len(items)})\n")
    for r in items: board.append(f"- [{r.get('title','')}](<../{r.get('file','')}>) — {r.get('type','')} · {r.get('owner_agent','')} · {r.get('updated','')}")
    board.append("")
open(os.path.join(root,"index/board.md"),"w",encoding="utf-8").write("\n".join(board))
print(f"indexed {len(rows)} topics")
