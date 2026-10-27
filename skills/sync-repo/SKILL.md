---
name: sync-repo
description: 开工前同步、认领防撞、提交与推送的统一规矩。任何 Agent 动仓之前必读。
---
## 开工三步
1. `python3 tools/sync.py check` 看本地有没有未提交改动、与远端差几个提交。
2. 有 git：`git pull --rebase`；没有 git 环境（只有 API 的 Agent）：通过 GitHub API 读最新文件，写回时带上原文件 sha，sha 变了说明别人改过，停下来重读。
3. 认领即上锁：把选题的 `owner_agent` 改成你并推进一格状态，再开始干活。长任务先单独提交这一步；短任务可并入收尾提交——但认领改动必须进入版本历史，不许一直躺在工作区。别人看到 owner 不是自己，不要碰。

## 提交
- 一次提交只做一件事，信息格式 `<status>: <topic_id> <一句话>`；只暂存自己改动的文件，禁止 `git add -A` 扫入别人未提交的改动。
- 提交前必跑 `tools/validate.py` + `tools/build_index.py`，index 跟着内容一起提交。
- 推送被拒（远端有新提交）：`git pull --rebase` 后解冲突再推，禁止 force push。

## 冲突处理
- 同一文件同一段冲突：后来者保留对方内容，把自己的改动合并进去，并在选题 history 记一笔。
- 状态冲突（两人推进了同一选题）：以先提交者为准，后者回退自己的状态推进。
