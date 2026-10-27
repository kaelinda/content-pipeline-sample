#!/usr/bin/env python3
"""给一个选题添加一条独立信息源：一源一文件，并把 id 登记进选题的 sources 列表。"""
import argparse, os, glob, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm import parse, set_fields
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--topic", required=True, help="topic_id，如 t-20261027-002")
ap.add_argument("--url", required=True); ap.add_argument("--title", required=True)
ap.add_argument("--type", default="web", dest="stype"); ap.add_argument("--publisher", default="")
ap.add_argument("--by", default=""); ap.add_argument("--reliability", default="secondary")
a = ap.parse_args()
topic_path = os.path.join(root, "topics", f"{a.topic}.md")
if not os.path.exists(topic_path): sys.exit(f"选题不存在 {topic_path}")
existing = sorted(glob.glob(os.path.join(root, "sources", f"{a.topic}-s*.md")))
n = len(existing) + 1
sid = f"{a.topic}-s{n:02d}"
today = datetime.date.today().isoformat()
tpl = open(os.path.join(root, "templates/source.md"), encoding="utf-8").read()
content = (tpl.replace("{{id}}", sid).replace("{{topic_id}}", a.topic).replace("{{title}}", a.title)
           .replace("{{url}}", a.url).replace("{{source_type}}", a.stype)
           .replace("{{publisher}}", a.publisher).replace("{{date}}", today).replace("{{by}}", a.by))
if a.reliability != "secondary":
    content = content.replace("reliability: secondary", f"reliability: {a.reliability}")
path = os.path.join(root, "sources", f"{sid}.md")
open(path, "w", encoding="utf-8").write(content)
text = open(topic_path, encoding="utf-8").read()
data, _ = parse(text)
srcs = data.get("sources") or []
if sid not in srcs: srcs.append(sid)
open(topic_path, "w", encoding="utf-8").write(set_fields(text, {"sources": srcs, "updated": today}))
print(f"added {sid} -> {a.topic} ({len(srcs)} sources)")
