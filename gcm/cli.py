"""命令行入口模块"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from gcm import __version__
from gcm.git import GitRepo
from gcm.prompt import PromptBuilder
from gcm.llm import LLMClient, LLMConfig
from gcm.interactive import InteractiveCommitter


class GCMApp:
    """GCM 应用主控：加载配置、解析参数、编排「生成→交互→提交」流程"""

    def __init__(self):
        self.repo = GitRepo()
        self.args: Optional[argparse.Namespace] = None

    def run(self) -> None:
        """主流程入口"""
        self._load_env()
        self.args = self._parse_args()

        # 检查是否在 git 仓库中
        if not self.repo.is_repo():
            print("错误: 当前目录不在 Git 仓库中", file=sys.stderr)
            sys.exit(1)

        # 获取暂存区变更
        changes = self.repo.get_staged_changes()
        if not changes.files:
            print("暂存区没有变更。请先使用 'git add' 添加变更。", file=sys.stderr)
            sys.exit(1)

        # 生成 commit message
        try:
            config = self._build_config()
            client = LLMClient(config)
            builder = PromptBuilder(verbose=self.args.verbose)
            commit_msg = client.chat(
                builder.system_prompt(),
                builder.user_prompt(changes),
            )
        except ValueError as e:
            print(f"配置错误: {e}", file=sys.stderr)
            sys.exit(1)
        except RuntimeError as e:
            print(f"生成失败: {e}", file=sys.stderr)
            sys.exit(1)

        # 仅输出模式（--print-only 或非交互终端）：保持旧行为，便于脚本/管道
        if self.args.print_only or not sys.stdin.isatty():
            print(commit_msg)
            return

        # 交互模式：菜单 → 修改/确认 → 提交
        InteractiveCommitter(self.repo).run(commit_msg)

    def _load_env(self) -> None:
        """加载 .env 文件"""
        # 加载用户主目录的 .env（优先级较低）
        home_env = Path.home() / ".env"
        if home_env.exists():
            load_dotenv(home_env)

        # 加载项目目录的 .env（优先级较高）
        project_env = self._find_env_file()
        if project_env:
            load_dotenv(project_env)

    def _find_env_file(self) -> Optional[Path]:
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

    def _parse_args(self) -> argparse.Namespace:
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

    def _build_config(self) -> LLMConfig:
        """构建 LLM 配置（环境变量 + 命令行覆盖）"""
        config = LLMConfig()

        # 命令行参数覆盖环境变量
        if self.args.api_base:
            config.api_base = self.args.api_base
        if self.args.api_key:
            config.api_key = self.args.api_key
        if self.args.model:
            config.model = self.args.model

        return config


def main():
    """主入口函数"""
    GCMApp().run()


if __name__ == "__main__":
    main()
