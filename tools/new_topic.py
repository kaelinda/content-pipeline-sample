#!/usr/bin/env python3
import sys, os, glob, datetime
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
title = sys.argv[1] if len(sys.argv)>1 else "未命名选题"
typ = sys.argv[2] if len(sys.argv)>2 else "article"
today = datetime.date.today().isoformat()
stamp = today.replace("-","")
existing = glob.glob(os.path.join(root,"topics",f"t-{stamp}-*.md"))
n = len(existing)+1
tid = f"t-{stamp}-{n:03d}"
tpl = open(os.path.join(root,"templates/topic.md"),encoding="utf-8").read()
content = tpl.replace("{{id}}",tid).replace("{{title}}",title).replace("{{date}}",today).replace("type: article",f"type: {typ}")
os.makedirs(os.path.join(root,'topics'),exist_ok=True); path = os.path.join(root,"topics",f"{tid}.md")
open(path,"w",encoding="utf-8").write(content)
print(path)
