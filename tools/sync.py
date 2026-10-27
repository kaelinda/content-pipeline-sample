#!/usr/bin/env python3
"""仓库同步小工具：check 看状态 / pull 拉取 / push 校验后推送。"""
import subprocess, sys, os
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(*args, check=True):
    r=subprocess.run(args,cwd=root,capture_output=True,text=True)
    if check and r.returncode!=0: print(r.stdout+r.stderr); sys.exit(r.returncode)
    return r
cmd=sys.argv[1] if len(sys.argv)>1 else "check"
if cmd=="check":
    st=run("git","status","--porcelain").stdout.strip()
    rem=run("git","remote",check=False).stdout.strip()
    print("remote:", rem or "(未配置远端：在 config.yaml 填 repo.remote 并 git remote add origin <地址>)")
    print("dirty files:", len(st.splitlines()) if st else 0)
    if st: print(st)
elif cmd=="pull":
    run("git","pull","--rebase"); print("pulled")
elif cmd=="push":
    st=run("git","status","--porcelain").stdout.strip()
    if st:
        print("拒绝推送：有未提交改动，先 git add + git commit 再 push。未提交文件：")
        print(st); sys.exit(1)
    run(sys.executable,"tools/validate.py")
    r=run("git","push",check=False)
    if r.returncode!=0:
        print(r.stdout+r.stderr)
        print("推送失败（见上）。若是首次推送且提示 no upstream，先执行：git push -u origin main")
        sys.exit(r.returncode)
    print("pushed")
else:
    print("usage: sync.py check|pull|push"); sys.exit(2)
