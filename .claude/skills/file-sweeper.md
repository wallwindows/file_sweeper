---
name: file-sweeper-dev
description: 开发 FileSweeper 工具，强制 Git 和自动测试验证
tools: [Bash, Read, Write, Edit, Glob, Grep]
---

## 核心规则
1. 每次代码修改后自动运行 pytest tests/ -v。
2. 测试全部通过后自动执行 git add -A && git commit -m "<描述>"。
3. 测试失败则修复直至通过，禁止提交。
4. 使用 pathlib 处理路径，所有 I/O 捕获异常。
5. 函数必须有类型注解和 Google 风格 docstring。

## Git 规范
- 提交信息格式：<type>: <subject>（type: feat/fix/docs/test/refactor）
- 禁止 --no-verify 跳过测试
