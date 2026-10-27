#!/usr/bin/env python3
import sys, os, argparse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm import parse, set_fields
ORDER = ["idea","researching","drafting","imaged","video","published"]
ap = argparse.ArgumentParser()
ap.add_argument("file"); ap.add_argument("status")
ap.add_argument("--agent", default=""); ap.add_argument("--url", default=""); ap.add_argument("--note", default="")
a = ap.parse_args()
text = open(a.file,encoding="utf-8").read()
data,_ = parse(text)
cur = data.get("status","idea")
if a.status != "archived":
    if cur not in ORDER or a.status not in ORDER: sys.exit(f"非法状态 {cur} -> {a.status}")
    if ORDER.index(a.status) != ORDER.index(cur)+1: sys.exit(f"不能跳级/倒退：{cur} -> {a.status}（要跳级请先改 SCHEMA 并说明理由）")
if a.status=="published" and not (a.url or data.get("published_url")): sys.exit("published 必须带 --url 发布链接")
today = datetime.date.today().isoformat()
upd = {"status":a.status,"updated":today}
if a.agent: upd["owner_agent"]=a.agent
if a.url: upd["published_url"]=a.url
entry = '{at: %s, from: %s, to: %s, by: %s, note: "%s"}' % (today, cur, a.status, a.agent or data.get("owner_agent",""), a.note)
open(a.file,"w",encoding="utf-8").write(set_fields(text, upd, entry))
print(f"OK {data.get('id')} {cur} -> {a.status}")
