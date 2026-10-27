# Review 与优化 Plan（2026-10-27）

审查方式：通读全部 tools / skills / 文档后，在副本与双 clone + 裸远端环境里逐项实测（并发认领、删号重建、坏数据注入、密钥样式注入、http 端点、大文件路径等）。**基线结论：骨架成立**——Git+Markdown、一源一档、状态流、纯脚本索引在正常路径下能跑通，原仓 `validate` 通过、全仓无真实密钥。但工具层目前是「演示级正确」：下面四类问题会在多 Agent 真实并发的第一周就咬人，**投入真实选题前先修第一、二批**。

---

## 一、问题清单（按严重程度）

### P0 会丢数据 / 机制失效

| # | 问题 | 实测证据 |
|---|---|---|
| P0-1 | **编号复用静默覆盖**：new_topic / add_source 用「现有文件数+1」编号且覆盖写、从不查目标是否存在 | 删掉 002 后新建 → 算出 003 并覆盖已有 003，手写内容丢失；add_source 同样覆盖 s03 |
| P0-2 | **fm.py 会把标准 YAML 写坏且 validate 看不见**：简易正则解析遇到块状列表时读成空串，set_fields 改写后旧行残留，产物连真 YAML 解析器都报错；而校验器与肇事者共用同一解析，自检全程无感 | 块状 `sources:` 经任一工具改写后 PyYAML ParserError，但 validate 照样 OK；另外 note 含引号/`}` 生成非法 history、列表元素含逗号被劈开、标题尾引号被吃字符、BOM 文件直接崩栈 |
| P0-3 | **sync.py push 假成功**：push 只 validate→build_index→git push，从不 commit | 有未提交改动时打印 `pushed`、退出码 0，远端纹丝不动；build_index 在 push 内改的 index 不会被提交，之后 `commit -a` 会把旧索引和新内容混提交，出现「index 标题 A、topics 标题 B」；check 也不报 ahead/behind |
| P0-4 | **认领只是君子协定**：工具层无所有权校验、无锁 | owner 已是 alice 的选题，bob 直接推进状态即无声抢走；双 Agent 同时认领，rebase 时在同一文件同位置冲突——skill 承诺的「带 sha 防覆盖」没有任何工具实现 |
| P0-5 | **状态机有后门且无门禁**：目标为 archived 时完全跳过合法性校验（`nonsense → archived` 都放行，归档后又恢复不出来）；各环节不验产物 | 空选题无文章、无信息源、无素材，一路点到 published（url 填 `not-a-url`）全通过，validate 也 OK；另外 type=article 的选题也被迫走 imaged/video 两步 |
| P0-6 | **validate 与 SCHEMA 声称的必填大面积脱节** | 逐项实测放行：缺 owner_agent/platforms/history、`updated: banana`、非法日期、type 非法、两选题同 id、文章 topic_id 指向不存在的选题、信息源缺 publisher/reliability、已发布选题挂 staging/example 占位链接；manifest 有一行坏 JSON 时 validate 直接崩栈而非定位报错 |
| P0-7 | **upload_asset 的三条技能承诺在代码里不存在**：HEAD 回读校验、预签名模式、pending 批量补传，grep 零命中；且没有任何工具读 config.yaml（只认环境变量）、endpoint 的 http 被写死成 https（本地 MinIO 连不上）、全文件读进内存+单 PUT+60 秒超时（视频必爆）、content-type 恒为 octet-stream、登记不校验 topic 存在，register_asset 对不存在的 `--file` 静默记空 sha | 全部实测复现；SigV4 路径从未对任何真实端点验证过——所有演示走的都是 staging |
| P0-8 | **密钥防线只有一句话**：.gitignore 只精确忽略 `.env` 一个名字 | `.env.local`、`*.pem`、`*.key`、`credentials.json` 全部 NOT-IGNORED，`git add -A` 即进仓；validate 无任何密钥样式扫描，无 CI 扫描 |

### P1 文档与代码对不上（照着文档做就会翻车）

- README「30 秒跑通闭环」里 `set_status ... --platform douyin` 是坏命令（根本没这个参数），新用户第一跑就报错。
- 素材登记口径三份文档三个说法：README 用 register_asset、AGENTS 说优先 upload_asset、prompts 话术 #3 教用 register_asset、make-media 说一律 upload-oss。
- set_status 不限制只能对 topics/ 用，可对 articles 执行并把文章状态改坏。
- build_index 对残缺选题不报警，照样生成空行进 CSV。
- history 实际是倒序插入（最新在最上），SCHEMA/注释未声明，按「最后一条=最新」读的消费者会读错。

### P2 缺失的关键能力

- 无 CI：validate、index 同步全靠人记得跑；无 tests（边界 bug 无回归网）。
- mirror-out / backup-restore / publish 链接检查都只有技能文字、无脚本，季度恢复演练等于手工作业。
- README 声称 content-dashboard 是这批文件的「视图」，仓里没有任何对接接口说明。
- validate 的 5MB 检查走磁盘文件系统而非 git 跟踪清单，口径与「大文件不进 Git」不完全一致。

---

## 二、优化 Plan（四批，按序执行）

### 第一批 · 防丢数据（改动小、收益最大，建议先做，约半天量级※）

1. **修编号**（P0-1）：编号改为「现有最大号+1」，且目标文件用排他创建、存在即报错；id 末尾可加 2 位随机后缀缓解双人同日撞号。验收：复刻「删 002 再新建」用例不覆盖任何文件。
2. **堵密钥洞**（P0-8）：.gitignore 补 `.env.*`、`*.pem`、`*.key`、`credentials*`、`.obsidian/`；validate 增加密钥样式扫描（AKIA/ghp_/私钥头等几条正则）。验收：注入测试密钥文件后 validate 必须报错。
3. **修坏命令与口径**（P1）：README 删 `--platform`；三份文档统一为 upload_asset 为唯一登记入口，register_asset 降为「登记外部现成链接」并在帮助里注明。验收：照 README 从零跑一遍闭环零报错。
4. **sync.py 不许假成功**（P0-3 的一半）：push 前发现未提交改动直接拒绝并提示先 commit；删除 push 内部的 build_index。验收：脏工作区跑 push 必须非零退出且不打印 pushed。

### 第二批 · 让状态机与校验名副其实（约一天量级※）

5. **fm.py 二选一（需拍板，见第三节）**（P0-2）：换 PyYAML 真解析，「零依赖」让位于正确性；同时 validate 在写回前先用真 YAML safe_load 过一遍 frontmatter，杜绝自引用盲区。note 等自由文本写入时统一 YAML 转义；history 改真追加并写进 SCHEMA。
6. **状态机补门禁**（P0-5）：archived 同样走合法校验且可恢复到 researching；set_status 只接受 topics/ 文件；推进规则加产物门禁——drafting 需至少 1 个信息源、imaged 需 assets 非空且已 uploaded、published 需合法 https URL 且无 staging/example 占位；状态流按 type 分流（article 可跳过 video 步，video 必须走全程）。
7. **validate 按 SCHEMA 补齐**（P0-6）：必填全集、枚举、日期格式、id 唯一且与文件名一致、文章 topic_id 存在性、信息源字段全集、manifest 双向对应与字段 schema 统一（register/upload 合并一套字段）；坏 JSON 报「文件:行号」；5MB 检查改为对 git 跟踪清单。
8. **加最小测试套件**：把本次 review 的实测用例（编号覆盖、块状 YAML、坏 note、空转 published、脏 push）直接转成 pytest 用例，改工具先跑测试。

### 第三批 · 协作与同步语义（约一天量级※）

9. **认领乐观锁**（P0-4）：set_status 增加 `--expect-owner`（与当前 owner 不符就停），认领规定为单独一次只改 owner/status 的提交；sync-repo 技能补 frontmatter 冲突的具体合并步骤；sync.py check 增加 fetch + ahead/behind 输出；API 型 Agent 的 sha 防覆盖写进一个 `tools/api_write.py` 或从技能中删去该承诺，二选一不许悬空。
10. **upload 真桶打通**（P0-7）：接一个真实桶（COS 或 R2）端到端实测并修正寻址风格与 endpoint scheme；content-type 按扩展名；补 HEAD 回读校验；config.yaml 与环境变量统一读取（env 优先）；大文件先定单文件上限并在超限时明确拒绝（分片作为后续项）；登记前校验 topic 存在、文件不存在时报错。验收：真图、真视频各传一个，浏览器可直接打开，manifest 与桶内对象 sha 一致。

### 第四批 · 补齐宣称的能力（按需排期）

11. **GitHub Actions**：push/PR 自动跑 validate + 重新生成 index 后 `git diff --exit-code index/` + gitleaks 扫描。
12. **脚本化镜像与恢复**：mirror_feishu.py（HTTP API 单向同步）、restore_check.py（clone 后按 manifest 抽查 sha256 并出演练报告）；publish 前链接可达性检查工具。
13. **content-dashboard 对接契约**：在本仓定一份只读接口说明（dashboard 读 index.json + topics/ 的字段约定），或把该宣称从 README 降格为「规划中」。

※ 工作量为单人+Agent 协作的粗估，不是承诺工期。

---

## 三、需要你拍板的三个点

1. **fm 解析**：换 PyYAML（多一个依赖、换正确性）还是维持零依赖但遇到复杂 YAML 直接报错拒绝？我推荐前者。
2. **状态流按类型分流**：article 跳过 video 步、图文走全程、video 必走全程——是否按这个口径定？
3. **第一个真桶**：腾讯 COS 还是 Cloudflare R2？定了我就按第三批第 10 项打通并实测。

## 四、明确不做的

- 不上数据库存正文（索引继续可重建）；不做多租户/权限系统（单人仓，靠 GitHub 仓库权限）；不自研锁服务（乐观锁+约定足够）；不在第一、二批里碰镜像与 dashboard（先把真源修结实）。
