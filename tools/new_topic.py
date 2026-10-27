#!/usr/bin/env python3
import sys, os, glob, datetime, re
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
title = sys.argv[1] if len(sys.argv)>1 else "未命名选题"
typ = sys.argv[2] if len(sys.argv)>2 else "article"
today = datetime.date.today().isoformat()
stamp = today.replace("-","")
existing = glob.glob(os.path.join(root,"topics",f"t-{stamp}-*.md"))
nums = [int(m.group(1)) for f in existing if (m := re.search(r"-(\d+)\.md$", f))]
n = (max(nums) + 1) if nums else 1
tpl = open(os.path.join(root,"templates/topic.md"),encoding="utf-8").read()
os.makedirs(os.path.join(root,'topics'),exist_ok=True)
while True:
    tid = f"t-{stamp}-{n:03d}"
    path = os.path.join(root,"topics",f"{tid}.md")
    content = tpl.replace("{{id}}",tid).replace("{{title}}",title).replace("{{date}}",today).replace("type: article",f"type: {typ}")
    try:
        with open(path,"x",encoding="utf-8") as fh: fh.write(content)
        break
    except FileExistsError:
        n += 1  # 已存在（编号被占/并发撞号）：顺延，绝不覆盖
print(path)
