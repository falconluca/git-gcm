"""命令行入口模块"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from gcm import __version__
from gcm.git import (
    is_git_repo,
    get_staged_changes,
    StagedChanges
)
from gcm.prompt import build_user_prompt, get_system_prompt
from gcm.llm import LLMClient, LLMConfig
from gcm.interactive import interactive_commit


def find_env_file() -> Optional[Path]:
    """查找 .env 文件

    查找顺序:
    1. 当前目录的 .env
    2. 父目录（向上查找直到 git 根目录）
    3. 用户主目录的 .env
    """
    # 当前目录
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        return env_path

    # 向上查找直到 git 根目录
    current = Path.cwd()
    while current != current.parent:
        current = current.parent
        env_path = current / ".env"
        if env_path.exists():
            return env_path
        # 如果找到 .git 目录就停止
        if (current / ".git").exists():
            break

    # 用户主目录
    env_path = Path.home() / ".env"
    if env_path.exists():
        return env_path

    return None


def load_env_files():
    """加载 .env 文件"""
    # 加载用户主目录的 .env（优先级较低）
    home_env = Path.home() / ".env"
    if home_env.exists():
        load_dotenv(home_env)

    # 加载项目目录的 .env（优先级较高）
    project_env = find_env_file()
    if project_env:
        load_dotenv(project_env)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog="gcm",
        description="自动生成 Git Commit Message"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="生成详细的 commit message"
    )

    parser.add_argument(
        "--api-base",
        type=str,
        help="API 基础 URL（覆盖 GCM_API_URL）"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="API Key（覆盖 GCM_API_KEY，不推荐在命令行中使用）"
    )

    parser.add_argument(
        "-m", "--model",
        type=str,
        help="使用的模型名称（覆盖 GCM_MODEL）"
    )

    parser.add_argument(
        "--print-only", "--no-commit",
        dest="print_only",
        action="store_true",
        help="仅输出 commit message，不进入交互提交（用于脚本/管道）"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser.parse_args()


def generate_commit_message(
    changes: StagedChanges,
    client: LLMClient,
    verbose: bool = False
) -> str:
    """生成 commit message

    Args:
        changes: 暂存区变更
        client: LLM 客户端
        verbose: 是否详细模式

    Returns:
        生成的 commit message
    """
    system_prompt = get_system_prompt()
    user_prompt = build_user_prompt(changes, verbose=verbose)

    return client.chat(system_prompt, user_prompt)


def main():
    """主入口函数"""
    # 加载 .env 文件
    load_env_files()

    args = parse_args()

    # 检查是否在 git 仓库中
    if not is_git_repo():
        print("错误: 当前目录不在 Git 仓库中", file=sys.stderr)
        sys.exit(1)

    # 获取暂存区变更
    changes = get_staged_changes()

    if not changes.files:
        print("暂存区没有变更。请先使用 'git add' 添加变更。", file=sys.stderr)
        sys.exit(1)

    # 创建配置（从环境变量加载）
    config = LLMConfig()

    # 命令行参数覆盖环境变量
    if args.api_base:
        config.api_base = args.api_base
    if args.api_key:
        config.api_key = args.api_key
    if args.model:
        config.model = args.model

    # 创建 LLM 客户端
    client = LLMClient(config)

    # 生成 commit message
    try:
        commit_msg = generate_commit_message(
            changes,
            client,
            verbose=args.verbose
        )
    except ValueError as e:
        print(f"配置错误: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"生成失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 仅输出模式（--print-only 或非交互终端）：保持旧行为，便于脚本/管道
    if args.print_only or not sys.stdin.isatty():
        print(commit_msg)
        return

    # 交互模式：菜单 → 修改/确认 → 提交
    interactive_commit(commit_msg)


if __name__ == "__main__":
    main()
