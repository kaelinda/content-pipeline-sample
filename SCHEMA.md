# frontmatter 规范 v1

```yaml
---
id: t-20261027-001          # 全局唯一，t-日期-序号
title: 标题
status: idea                # idea|researching|drafting|imaged|video|published|archived
type: article               # article|video|图文|podcast
platforms: [douyin]         # 计划发布平台
sources: []                 # 信息源 id 列表，如 [t-20261027-002-s01, t-20261027-002-s02]；一源一文件存 sources/，含 url/类型/发布方/采集时间/可靠性，同一选题可挂任意多个
assets: []                  # 对象存储 URL（图片/视频），登记见 assets/manifest.jsonl
created: 2026-10-27
updated: 2026-10-27
owner_agent: Muse           # 当前负责的 Agent 名，交接时改这里
published_url: ""           # 发布后回填
history:
  - {at: 2026-10-27, from: "", to: idea, by: Muse, note: ""}
---
```
规则：status 只能按 README 的状态流前进；published 必须有 published_url；assets 里的每个 url 必须能在 manifest.jsonl 里查到。
