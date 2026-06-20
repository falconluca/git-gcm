# GCM

[![PyPI version](https://badge.fury.io/py/git-gcm.svg)](https://pypi.org/project/git-gcm/)

基于大模型的 Git Commit Message 自动生成工具，支持所有 OpenAI 协议兼容的大模型服务

## 安装

```bash
pip install git-gcm
```

## 配置

设置环境变量：

```bash
export GCM_API_KEY="your-api-key"
export GCM_API_URL="https://api.openai.com/v1"
export GCM_MODEL="gpt-4o-mini"
```

## 使用

```bash
git add .
gcm                # 生成 commit message 并进入交互菜单
gcm -v             # 生成详细 commit message 并进入交互菜单
gcm --print-only   # 仅输出 message，不提交（用于脚本/管道）
```

运行 `gcm` 后会展示生成的 commit message，并用方向键导航的菜单让你选择（基于 [questionary](https://github.com/tmbo/questionary)）：

- **提交此 message**：选中后按 Enter 直接执行 `git commit`
- **修改 message**：输入新内容后回到菜单（可反复修改）
- **仅输出，不提交**：只打印 message

> ↑↓ 移动选择，Enter 确认，ESC / Ctrl-C 取消。在管道或非交互终端（如 `gcm | cat`）中，gcm 会自动仅输出 message，不弹交互。

## 示例

**精简模式：**

```
feat(auth): 添加用户登录功能
```

**详细模式 (`-v`)：**

```
feat(auth): 添加用户登录功能

- 实现 JWT token 认证
- 添加登录表单验证
- 集成第三方 OAuth 登录
```

MIT License
