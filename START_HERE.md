# START HERE — 新 Agent 上手指南（先读这一页）

你拿到这个仓，不需要任何背景知识，按下面 5 步走就能干活。全程不需要装任何平台专用 CLI（不用 lark-cli），工具全是 Python 标准库。

## 第 0 步：确认你是哪种 Agent

| 你的能力 | 怎么干活 |
|---|---|
| 有本地文件系统 + 能跑命令（Claude Code / Hermes / 本地脚本型） | clone 本仓，按本文走（推荐） |
| 只有 GitHub API / MCP（云端 Agent） | 读同样的文件规则；写文件走 API 并带原文件 sha 防覆盖；状态推进的校验逻辑照 `tools/set_status.py` 的规则手动执行 |
| 只有聊天、不能读写文件 | 你不能直接干活：把任务拆成明确的文件操作清单，交给上面两种 Agent 执行，不要凭空声称已完成 |

## 第 1 步：体检环境（1 分钟）

```bash
python3 tools/doctor.py
```
全是 PASS/WARN 才能开工（WARN 是可选能力缺失，会注明影响什么）。依赖清单见 `docs/environment.md`：必需只有 Python 3.9+ 和 git，无任何 pip 包要装。若 doctor 提示 git 提交身份未配置，按提示先配一个仓内本地身份，否则最后一步提交会失败。

## 第 2 步：读规矩（5 分钟，按顺序）

1. `AGENTS.md` — 全体规矩与「按任务先读哪个 skill」路由表
2. `SCHEMA.md` — frontmatter 字段规范（什么必填、状态怎么流转）
3. 与你任务对应的 `skills/<name>/SKILL.md` 一篇

## 第 3 步：看现在有什么活

```bash
cat index/board.md        # 选题看板：每个状态下有哪些选题
cat assets/manifest.jsonl # 已有素材登记
```
选题文件在 `topics/`，一篇一个；同一选题的信息源在 `sources/`，一源一文件。

## 第 4 步：认领并干活

```bash
python3 tools/set_status.py topics/<id>.md researching --agent <你的名字>
```
认领即上锁：先推进状态再开始干活；这次状态推进要进入版本历史——长任务单独提交它，短任务可以并入本次收尾提交，但不许让认领改动一直躺在工作区（见 skills/sync-repo）。所有工具的用途与用法见 `tools/catalog.json`（机器可读）或 README 的闭环示例。

## 第 5 步：交活标准（缺一不可）

```bash
python3 tools/build_index.py
python3 tools/validate.py   # 必须 OK
git add <你本次改动的文件...> && git commit -m "<status>: <topic_id> <一句话>"
```
- 图片/视频不要进 git：用 `tools/upload_asset.py`（没配桶自动走 staging 暂存，不要卡住）。
- 干完把 `owner_agent` 交给下一环节或留空待认领，在 history 里写清还差什么。
- 只提交你本次改动的文件：接手时工作区可能有别人未提交的改动，不要用 `git add -A` 一把扫进你的提交（一次提交只做一件事）。

## 卡住了看哪里

- 字段不知道填什么 → `SCHEMA.md` 和 `templates/` 里的模板
- 状态推不动 → 状态流是 idea→researching→drafting→imaged→video→published，不许跳级；报错信息会说差哪一步
- 环境缺东西 → `docs/environment.md` 的分级表，可选依赖缺失不影响基本干活
