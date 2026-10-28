---
name: upload-oss
description: 把图片/视频等大文件传到 S3 兼容对象存储并登记。生图、生视频的 Agent 必读。
---
## 原则
- 大文件永不进 Git。上传对象存储，仓里只登记 URL + sha256。
- 密钥只从环境变量读（OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET），永远不写进仓、不写进聊天。
- 没配桶时走 staging 模式：文件先放本地 `assets-staging/`，登记状态 pending，等配好桶后批量补传，流程不能因此卡住。

## 默认桶：Cloudflare R2（2026-10-28 定）
- 在 Cloudflare 控制台建一个私有桶（如 `content-assets`），不要整桶公开。
- 建一个仅限该桶的 R2 API Token，把它的 Access Key ID / Secret Access Key 填进本机 `.env`，不要发给云端 Agent。
- `.env` 填写示例（`<account_id>` 换成你自己的）：
  ```
  OSS_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
  OSS_BUCKET=<你的桶名>
  OSS_REGION=auto
  OSS_PUBLIC_BASE=
  ```
- 对外访问：已发布、需要在 Notion/飞书里嵌入的封面，才走公开地址。优先给桶绑自定义域名填进 `OSS_PUBLIC_BASE`；其次用 R2 公开桶的 r2.dev 地址。工作中的原图和未发布视频不要用公开地址。
- 换桶时不用改代码：改 `.env` 里的 endpoint/bucket/region 即可（COS/OSS 的 region 要改成对应区域，不能留 `auto`）。

## 用法
```bash
python3 tools/upload_asset.py --topic t-20261027-002 --type cover --file cover.png
```
工具会自动：算 sha256 → 按规范命名 `assets/<topic_id>/<type>-<sha前8位>.<ext>` → SigV4 签名 PUT 上传（纯标准库，不装 boto3）→ 写 manifest.jsonl → 把 URL 回填选题/文章的 assets。

## 当前未实现，如实说明
- 预签名 URL 模式尚未实现：不能靠“只给 Agent 一个上传 URL、不给密钥”来让云端 Agent 直传。不能持有密钥的 Agent 先把文件交给能配 `.env` 的 Agent 上传。
- HEAD 回读校验尚未实现：目前只校验上传 HTTP 返回 200/201，并在 manifest 里记下 sha256；下载方要自己对一下 sha256，不要手动改 manifest 凑数。
- 大文件分片上传尚未实现：工具是整文件读进内存、单次 PUT、60 秒超时，大成片先用控制台或 rclone 这类支持分片的工具传，再用 `register_asset.py` 登记。

## 验收
上传后 manifest 里应有该文件的一行（含 topic、type、url、sha256、upload_status=uploaded），且选题/文章的 assets 里有同一 URL。
