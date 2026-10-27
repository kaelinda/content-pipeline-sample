---
name: collect-sources
description: 给选题搜集、登记信息源：一源一档、可靠性分级、快照留底。
---
## 步骤
1. 先看选题文件里已有的 sources，别重复采。
2. 每发现一个新来源：`python3 tools/add_source.py --topic <id> --title .. --url .. --type official-doc|media|video|social|paper --publisher .. --by <你的名字> --reliability primary|secondary|social`
3. 在生成的 sources/ 文件里补：快照要点（关键原文摘录）、与本选题的关系、与其它来源是否冲突。

## 分级
- primary：一手官方（官网、官方文档、原始数据、当事人原文）
- secondary：二手报道/解读（注明转述自谁）
- social：社媒帖子/评论（只能做线索，不能单独支撑事实结论）
一个选题的事实结论至少要有一个 primary 或两个独立 secondary 支撑。
