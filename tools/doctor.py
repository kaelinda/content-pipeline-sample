#!/usr/bin/env python3
"""环境体检：新 Agent 开工前跑一遍。FAIL=必需缺失（退出码非0），WARN=可选缺失，PASS=就绪。"""
import os, sys, shutil, subprocess

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails, warns = [], []

def ok(name):
    print("PASS  " + name)

def warn(name, why):
    warns.append(name)
    print("WARN  " + name + " — " + why)

def fail(name, why):
    fails.append(name)
    print("FAIL  " + name + " — " + why)

# Python 版本
v = sys.version_info
if v >= (3, 9):
    ok("Python " + ".".join(map(str, v[:3])) + " (>=3.9)")
else:
    fail("Python 版本", "当前 " + ".".join(map(str, v[:3])) + "，需要 3.9+")

# 编码
if (sys.stdout.encoding or "").lower().replace("-", "") in ("utf8",):
    ok("终端编码 UTF-8")
else:
    warn("终端编码", "当前 " + str(sys.stdout.encoding) + "，中文可能乱码，建议设 PYTHONUTF8=1")

# git
if shutil.which("git"):
    ok("git 可用")
else:
    warn("git 不可用", "本地模式需要 git；纯 GitHub API 模式的 Agent 可忽略")

# git 提交身份（收尾提交必需，提前查，免得最后才发现提交不了）
try:
    _n = subprocess.run(["git", "-C", root, "config", "user.name"], capture_output=True, text=True).stdout.strip()
    _e = subprocess.run(["git", "-C", root, "config", "user.email"], capture_output=True, text=True).stdout.strip()
    if _n and _e:
        ok("git 提交身份已配置 (" + _n + ")")
    else:
        warn("git 提交身份未配置", '收尾提交会失败；先执行 git config user.name "你的Agent名" 和 git config user.email "名字@localhost"（仓内本地身份即可）')
except Exception:
    warn("git 提交身份检查失败", "无法读取 git config")

# 仓结构
need_dirs = ["topics", "sources", "research", "articles", "assets", "index", "tools", "skills", "templates"]
missing = [d for d in need_dirs if not os.path.isdir(os.path.join(root, d))]
if not missing:
    ok("仓目录结构完整")
else:
    fail("仓目录结构", "缺失 " + ", ".join(missing) + "（确认你在仓根目录运行）")
need_files = ["AGENTS.md", "SCHEMA.md", "START_HERE.md", "tools/validate.py", "tools/build_index.py"]
missing = [f for f in need_files if not os.path.exists(os.path.join(root, f))]
if not missing:
    ok("关键文件齐全")
else:
    fail("关键文件", "缺失 " + ", ".join(missing))

# 写权限
try:
    probe = os.path.join(root, ".doctor-probe")
    with open(probe, "w", encoding="utf-8") as f:
        f.write("ok")
    os.remove(probe)
    ok("仓目录可写")
except Exception as e:
    fail("仓目录可写", str(e))

# 索引存在
if os.path.exists(os.path.join(root, "index", "board.md")):
    ok("索引已生成 (index/board.md)")
else:
    warn("索引未生成", "先跑 python3 tools/build_index.py")

# OSS（可选）
oss_keys = ("OSS_ENDPOINT", "OSS_BUCKET", "OSS_ACCESS_KEY_ID", "OSS_ACCESS_KEY_SECRET")
if all(os.environ.get(k) for k in oss_keys):
    ok("OSS 凭据已配置（可真传）")
else:
    warn("OSS 未配置", "上传将走 staging 暂存模式，不影响其它干活；配置见 docs/environment.md")

print()
if fails:
    print("结论：有 " + str(len(fails)) + " 项必需条件不满足，先修 FAIL 再开工。")
    sys.exit(1)
print("结论：可以开工" + ("（有 " + str(len(warns)) + " 项可选能力缺失，见 WARN）" if warns else "") + "。下一步读 START_HERE.md 第 2 步。")
