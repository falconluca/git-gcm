# GCM

[![PyPI version](https://badge.fury.io/py/git-gcm.svg)](https://pypi.org/project/git-gcm/)

基于大模型的 Git Commit Message 生成，支持所有 OpenAI 协议兼容的服务。

## 安装

```bash
# Mac 用户先装 pipx
brew install pipx && pipx ensurepath

pipx install git-gcm
```

升级：`pipx upgrade git-gcm`

## 配置

```bash
export GCM_API_URL=https://api.openai.com/v1
export GCM_API_KEY=your-api-key
export GCM_MODEL=gpt-4o-mini
```

持久化写入 `~/.zshrc` / `~/.bashrc` 后 `source` 一下。

## 使用

```bash
git add .
gcm              # 生成 commit message 并进入交互菜单
gcm -v           # 详细模式
gcm -f           # 跳过 git hooks（等价 --no-verify）
gcm --print-only # 仅输出，不提交
```

生成后进入交互菜单（↑↓ 选择，Enter 确认）：

- **提交** — 直接 `git commit`
- **编辑** — 微调 message，Alt/⌥+Enter 保存
- **仅输出** — 只打印不提交

> 非交互终端（如 `gcm | cat`）自动跳过菜单，直接输出。

## 示例

精简模式：

```
feat(auth): 添加用户登录功能
```

详细模式（`-v`）：

```
feat(auth): 添加用户登录功能

- 实现 JWT token 认证
- 添加登录表单验证
- 集成第三方 OAuth 登录
```

MIT License
