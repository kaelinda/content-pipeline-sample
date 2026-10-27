---
name: upload-oss
description: 把图片/视频等大文件传到 S3 兼容对象存储并登记。生图、生视频的 Agent 必读。
---
## 原则
- 大文件永不进 Git。上传对象存储，仓里只登记 URL + sha256。
- 密钥只从环境变量读（OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET），永远不写进仓、不写进聊天。
- 没配桶时走 staging 模式：文件先放本地 `assets-staging/`，登记状态 pending，等配好桶后批量补传，流程不能因此卡住。

## 用法
```bash
python3 tools/upload_asset.py --topic t-20261027-002 --type cover --file cover.png
```
工具会自动：算 sha256 → 按规范命名 `assets/<topic_id>/<type>-<sha前8位>.<ext>` → SigV4 签名 PUT 上传（纯标准库，不装 boto3）→ 写 manifest.jsonl → 把 URL 回填选题/文章的 assets。
也支持预签名 URL 模式：管理员生成 presigned PUT URL，Agent 只拿 URL 上传，连密钥都不用给 Agent。

## 验收
上传后工具会 HEAD 回读校验大小一致；不一致报错，不要手动改 manifest 凑数。
