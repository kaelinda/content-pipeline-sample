# content-pipeline-sample

> **新 Agent？先读 [`START_HERE.md`](START_HERE.md)，跑一遍 `python3 tools/doctor.py` 体检，再开工。** 环境依赖（必需只有 Python 3.9+ 与 git，零 pip 包）写在 `docs/environment.md`。

一个最小可跑的多 Agent 内容生产样板仓。设计目标只有一个：**换任何平台、换任何 Agent，都不用迁数据。**

## 原理（四句话）
1. 文字真源 = Git 里的 Markdown，一篇一个文件，状态写在文件头部的 YAML frontmatter 里。
2. 图片/视频真源 = S3 兼容对象存储，默认 Cloudflare R2（免出站流量费、全球 Agent 都容易访问；腾讯 COS / 阿里 OSS / MinIO 为备选），仓里只登记 URL + sha256，不存大文件。
3. 索引、看板、选题库表格都是脚本从 Markdown 自动生成的，可随时重建、可丢弃。
4. 飞书 / Notion / Obsidian / content-dashboard 都只是这批文件的不同“视图”，谁坏了都不丢数据。

## 目录
```
topics/     选题，一篇一个 .md，frontmatter.status 是唯一状态源
sources/    信息源，一源一文件（同一选题可挂多个不同信息源）
research/   调研笔记 / 综合分析
articles/   文章成稿
scripts/    生视频脚本等
assets/     素材清单 manifest.jsonl（只登记，不存大二进制）
index/      自动生成：topics.csv / index.json / board.md（勿手改）
templates/  各类模板
tools/      Agent 通用脚本（纯 Python 标准库，无需 pip 安装任何东西）
prompts/    给不同 Agent 的任务话术（复制粘贴即可派活）
views/      Obsidian Bases 选题看板视图
```

## 30 秒跑通闭环
```bash
python3 tools/new_topic.py "你的选题标题"
python3 tools/set_status.py topics/<生成的文件>.md researching --agent Muse
python3 tools/set_status.py topics/<文件>.md drafting --agent claude-code
python3 tools/upload_asset.py --topic <topic_id> --type cover --file cover.svg   # 自动上传/暂存并登记，回填 assets（没配桶时走 staging）
python3 tools/set_status.py topics/<文件>.md imaged
python3 tools/set_status.py topics/<文件>.md video
python3 tools/set_status.py topics/<文件>.md published --url https://example.com/published/1
python3 tools/build_index.py
python3 tools/validate.py
cat index/board.md
```

## 状态流（不许跳级倒退要写理由）
`idea → researching → drafting → imaged → video → published`，另有 `archived` 随时可归档。

## 技能层 skills/（每个 Agent 干活前先读对应的一篇）
- `sync-repo` 同步与防冲突（认领即上锁、提交规范、没有 git 时用 GitHub API + sha 防覆盖）
- `upload-oss` 上传对象存储（默认 R2，SigV4 直传，密钥只走环境变量，没配桶有 staging 模式；预签名 URL 与 HEAD 回读校验尚未实现，见该 skill）
- `collect-sources` 采集信息源（一源一档、可靠性三级、事实结论的支撑标准）
- `write-article` 写作与交接 / `make-media` 生图生视频 / `publish` 发布回填
- `mirror-out` 单向镜像到飞书（HTTP API，不用 lark-cli）/ Notion（托管 MCP）
- `backup-restore` 季度恢复演练（只用仓+桶重建，证明真能迁移）

## 配置层
`config.example.yaml`（可进仓，不含密钥）+ `.env.example`（密钥模板，.env 永不进仓）。默认桶已定为 R2：按 `skills/upload-oss` 建桶、建桶级 Token、填 `.env` 后，`tools/upload_asset.py` 就能直传；没配好之前先走 staging，不卡流程。

## 给 Agent 的规矩
见 `AGENTS.md`。任何 Agent（Muse / Grok Bot / WorkBuddy / Hermes / Claude Code / 豆包）只需会读写文件 + git，或会调 GitHub API，就能干活——不需要装 lark-cli、不需要任何平台专用 CLI。
