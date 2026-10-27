---
name: mirror-out
description: 把仓里的内容单向同步成飞书/Notion 页面给人阅读协作。镜像永远不是真源。
---
## 规矩
- 单向：仓 → 镜像。人在镜像里的评论要落实，先改仓再同步，不要直接改镜像正文后指望它回流。
- 飞书走 HTTP Open API（不需要 lark-cli）；Notion 走官方托管 MCP 或 REST API。
- 同步内容 = index/board.md 的看板 + 每篇 articles 的渲染版；sources 只同步标题和原链接。
- 镜像坏了/被删了：重跑同步即可恢复，所以镜像平台不需要备份策略。
