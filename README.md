# GCM

[![PyPI version](https://badge.fury.io/py/git-gcm.svg)](https://pypi.org/project/git-gcm/)

基于大模型的 Git Commit Message 生成，支持所有 OpenAI 协议兼容的大模型服务

## 安装

**方式一：pipx（推荐）**

pipx 在隔离环境安装命令行工具，不污染系统 Python，也避开 macOS 新版本 `externally-managed-environment` 报错。

```bash
# Mac 用户先装 pipx
brew install pipx && pipx ensurepath

# 安装
pipx install git-gcm
```

**方式二：pip**

```bash
pip install git-gcm
```

**从源码安装（尚未发布到 PyPI 时）**

```bash
pipx install git+https://github.com/falconluca/gcm.git
# 或
pip install git+https://github.com/falconluca/gcm.git
```

**升级到新版本**

```bash
pipx upgrade git-gcm     # pipx 用户
pip install -U git-gcm   # pip 用户
```

## 配置

设置环境变量：

```bash
export GCM_API_URL=https://api.openai.com/v1
export GCM_API_KEY=your-api-key
export GCM_MODEL=gpt-4o-mini
```

> 想让配置持久生效，把上面的 `export` 写进 `~/.zshrc`（Mac 默认 zsh）或 `~/.bashrc`，再执行 `source ~/.zshrc`。也支持智谱、DeepSeek 等 OpenAI 兼容服务，改 `GCM_API_URL` 和 `GCM_MODEL` 即可。

## 使用

```bash
git add .
gcm                # 生成 commit message 并进入交互菜单
gcm -v             # 生成详细 commit message 并进入交互菜单
gcm -f             # 提交时跳过 git hooks（等价 git commit --no-verify）
gcm --print-only   # 仅输出 message，不提交（用于脚本/管道）
```

运行 `gcm` 后会展示生成的 commit message，并用方向键导航的菜单让你选择：

- **提交此 message**：选中后按 Enter 直接执行 `git commit`
- **修改 message**：在预填的编辑框里直接微调（支持多行，兼容 `-v`），Alt+Enter 提交后回到菜单
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
