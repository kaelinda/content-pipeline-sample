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
    run(sys.executable,"tools/validate.py"); run(sys.executable,"tools/build_index.py")
    run("git","push"); print("pushed")
else:
    print("usage: sync.py check|pull|push"); sys.exit(2)
