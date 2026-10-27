# 给各 Agent 的任务话术（复制粘贴，替换 <...> 即可）

## 1. 搜选题（给 Grok Bot / Muse / 豆包）
> 在 content-pipeline-sample 仓里，用 tools/new_topic.py 新建 3 个关于 <领域> 的选题，把每个选题的一句话价值和大纲填进 topics/ 对应文件，状态保持 idea，owner_agent 写你的名字。跑 validate.py 通过后提交。

## 2. 写文章（给 Claude Code / WorkBuddy / Hermes）
> 认领 topics/<id>.md：先用 tools/set_status.py 把它推进到 researching 并在 research/ 写调研笔记（事实带来源），再推进 drafting，在 articles/ 写成稿，最后跑 build_index.py 和 validate.py 后提交。图片只登记对象存储 URL，不进 Git。

## 3. 生图（给任意生图 Agent）
> 读 articles/<文章>.md，按文末配图要求生成封面图，用 tools/upload_asset.py 上传并登记（没配桶自动走 staging），再把选题推进到 imaged。

## 4. 做视频（给 Muse / Lemo 流程）
> 读 articles/<文章>.md，在 scripts/ 生成分镜脚本并成片，成片上传对象存储并登记，把选题依次推进 video → published（带发布链接）。
