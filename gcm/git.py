"""Git 操作工具模块"""

import subprocess
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional


@dataclass
class FileChange:
    """文件变更信息"""
    status: str  # A=新增, M=修改, D=删除, R=重命名
    old_path: Optional[str]  # 旧路径（重命名时使用）
    new_path: str  # 新路径

    # 状态码 → 中文描述（类变量，非 dataclass 字段）
    _STATUS_SYMBOLS: ClassVar[Dict[str, str]] = {
        "A": "新增",
        "M": "修改",
        "D": "删除",
        "R": "重命名",
        "C": "复制",
        "T": "类型变更",
    }

    @property
    def symbol(self) -> str:
        """状态对应的中文描述"""
        return self._STATUS_SYMBOLS.get(self.status, self.status)

    @property
    def summary(self) -> str:
        """变更摘要行，如 '- [新增] path' 或 '- [重命名] old -> new'"""
        if self.status in ("R", "C") and self.old_path:
            return f"- [{self.symbol}] {self.old_path} -> {self.new_path}"
        return f"- [{self.symbol}] {self.new_path}"


@dataclass
class StagedChanges:
    """暂存区变更信息"""
    files: List[FileChange]
    diff_content: str


@dataclass
class CommitResult:
    """git commit 的执行结果"""
    success: bool
    stdout: str
    stderr: str


class GitRepo:
    """封装对 Git 仓库的子进程操作"""

    def __init__(self, path: str = "."):
        self.path = path

    def is_repo(self) -> bool:
        """检查是否在 git 仓库中"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                check=False,
                cwd=self.path,
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except FileNotFoundError:
            return False

    def get_staged_changes(self, max_diff_lines: int = 500) -> StagedChanges:
        """获取完整的暂存区变更信息

        Args:
            max_diff_lines: diff 内容最大行数限制，防止过长

        Returns:
            StagedChanges 对象
        """
        files = self._staged_files()
        diff = self._staged_diff()

        # 限制 diff 行数
        if diff:
            lines = diff.split("\n")
            if len(lines) > max_diff_lines:
                diff = "\n".join(lines[:max_diff_lines])
                diff += f"\n\n... (truncated, {len(lines) - max_diff_lines} more lines)"

        return StagedChanges(files=files, diff_content=diff)

    def commit(self, message: str) -> CommitResult:
        """执行 git commit

        Args:
            message: commit message

        Returns:
            CommitResult
        """
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=False,
            cwd=self.path,
        )
        return CommitResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    def _staged_files(self) -> List[FileChange]:
        """获取暂存区的文件列表"""
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status", "--diff-filter=ACDMRT"],
            capture_output=True,
            text=True,
            check=False,
            cwd=self.path,
        )

        if result.returncode != 0:
            return []

        files = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            status = parts[0][0]  # 取状态首字母

            if status in ("R", "C"):
                # 重命名/复制: status\told_path\tnew_path
                files.append(FileChange(
                    status=status,
                    old_path=parts[1],
                    new_path=parts[2]
                ))
            else:
                # 其他: A/M/D\tpath
                files.append(FileChange(
                    status=status,
                    old_path=None,
                    new_path=parts[1]
                ))

        return files

    def _staged_diff(self) -> str:
        """获取暂存区的详细差异"""
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=False,
            cwd=self.path,
        )

        if result.returncode != 0:
            return ""

        return result.stdout
