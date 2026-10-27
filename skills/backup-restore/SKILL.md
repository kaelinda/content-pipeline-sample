---
name: backup-restore
description: 证明这套数据真的可迁移：定期只用仓+桶重建全部视图。
---
## 每季度一次
1. 在一个干净目录 clone 仓 + 按 manifest 把对象存储文件列一遍，校验 sha256 抽查 5 个。
2. 跑 build_index + validate，用 Obsidian 打开仓看一眼看板。
3. 任选一个镜像按 mirror-out 重跑同步。
4. 演练结果记进 research/ 一篇笔记；哪一步过不了，哪一步就是假的可迁移，当场修。
