# 环境依赖清单（提前写明，拿到就能对照准备）

## 必需（缺了干不了活）

| 依赖 | 版本 | 检查命令 | 说明 |
|---|---|---|---|
| Python | 3.9+（建议 3.11+） | `python3 --version`（Windows 用 `python --version`） | 本仓全部工具只用标准库，**零 pip 依赖**，`requirements.txt` 是空的（只有注释） |
| git | 任意近版本 | `git --version` | 仅「本地模式」需要；纯 GitHub API 模式的 Agent 不需要 |
| git 提交身份 | — | `git config user.name` | 没配会在收尾提交时才失败，开工前配好；仓内本地身份即可：`git config user.name "你的Agent名"`、`git config user.email "名字@localhost"`（doctor 会查这一项） |
| UTF-8 环境 | — | `python3 -c "import sys; print(sys.stdout.encoding)"` | 文件全是 UTF-8；Windows 终端乱码时设 `PYTHONUTF8=1` |

## 可选（缺了只是对应能力不可用，doctor 会标 WARN）

| 依赖 | 用途 | 缺失影响 | 配置方式 |
|---|---|---|---|
| OSS 凭据（OSS_ENDPOINT / OSS_BUCKET / OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET / OSS_REGION / OSS_PUBLIC_BASE） | 上传图片/视频到 S3 兼容桶 | 上传走 staging 暂存模式，事后补传 | 复制 `.env.example` 为 `.env` 填入（.env 永不进仓） |
| GitHub token / 已授权的 GitHub App | API 模式 Agent 读写仓 | 只能本地模式干活 | 由平台侧授权，不写进仓 |
| 飞书 app_id/secret、Notion token | 镜像同步到飞书/Notion | 镜像功能不可用，真源不受影响 | 同上，放 `.env` |
| Obsidian | 人类本地打开仓看板/编辑 | Agent 不需要；人可用任何 Markdown 编辑器替代 | 打开仓根目录即是一个 vault |

## 网络

- 本地模式：能访问你的 git 远端（github.com 或自建 Gitea）。
- 上传时：能访问桶 endpoint。镜像时：能访问飞书/Notion API。
- 除此以外无外部服务依赖：不调任何模型 API、不连数据库、不需要 Docker、不需要 Node。

## 一键体检

```bash
python3 tools/doctor.py
```
输出分三级：FAIL=必需项缺失（先修再干活）、WARN=可选项缺失（注明影响）、PASS=就绪。退出码非 0 表示有 FAIL。
