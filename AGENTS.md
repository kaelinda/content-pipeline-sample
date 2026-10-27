# AGENTS.md — 所有 Agent 的统一规矩

0. **开工前先读 `START_HERE.md` 并跑 `python3 tools/doctor.py`**，体检有 FAIL 不要开工。

1. **只改你任务范围内的文件。** 状态变化只改对应 `topics/*.md` 的 frontmatter，不要手改 `index/`（那是生成的）。
2. **每次推进状态必须走合法流转**：idea → researching → drafting → imaged → video → published，用 `tools/set_status.py` 改，它会校验并写 `updated` 和 `history`。
3. **正文写 Markdown，元数据写 frontmatter。** 必填：id / title / status / type / created / updated / owner_agent。
4. **图片/视频不进 Git。** 按 `skills/upload-oss` 用 `tools/upload_asset.py` 上传对象存储并自动登记（没配桶时自动走 staging pending，不要卡住流程）；仅登记外部现成链接时才用 `register_asset.py`。
5. **引用要有来源，且一源一档。** 同一选题的每个信息源用 `tools/add_source.py` 单独建 `sources/<topic_id>-sNN.md`（url、类型、发布方、采集时间、可靠性、快照要点），选题只登记 id；多个信息源互相冲突时在各自文件里注明，不许只留一个链接了事。调研结论写进 `research/`，不凭空写事实。
6. **提交信息格式**：`<status>: <topic_id> <一句话>`，例：`drafting: t-20261027-001 完成初稿`。
7. 干完活跑一遍 `python3 tools/validate.py`，不通过不要提交。

## 先读哪个 skill（按任务类型）
| 任务 | 先读 |
|---|---|
| 任何动仓的活 | skills/sync-repo（认领即上锁） |
| 搜选题/找资料 | skills/collect-sources |
| 写文章 | skills/write-article |
| 生图/生视频 | skills/make-media + skills/upload-oss |
| 发布 | skills/publish |
| 同步飞书/Notion 给人看 | skills/mirror-out |
| 季度自检 | skills/backup-restore |
