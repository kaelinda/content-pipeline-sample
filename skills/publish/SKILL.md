---
name: publish
description: 把成稿发布到目标平台并回填台账。
---
1. 发布前最后跑一次 validate；确认 assets 里的链接都能打开。
2. 发布动作由人确认或由明确授权的发布流程执行；发布后拿到公开链接。
3. `python3 tools/set_status.py topics/<id>.md published --url <公开链接>` 回填，禁止只在聊天里说发了。
