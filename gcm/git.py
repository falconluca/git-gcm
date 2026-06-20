"""Git 操作工具模块"""

import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path


@dataclass
class FileChange:
    """文件变更信息"""
    status: str  # A=新增, M=修改, D=删除, R=重命名
    old_path: Optional[str]  # 旧路径（重命名时使用）
    new_path: str  # 新路径


@dataclass
class StagedChanges:
    """暂存区变更信息"""
    files: List[FileChange]
    diff_content: str


def is_git_repo() -> bool:
    """检查当前目录是否在 git 仓库中"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except FileNotFoundError:
        return False


def get_staged_files() -> List[FileChange]:
    """获取暂存区的文件列表"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-status", "--diff-filter=ACDMRT"],
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        return []

    files = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue

        parts = line.split("\t")
        status = parts[0][0]  # 取状态首字母

        if status == "R":
            # 重命名: R\told_path\tnew_path
            files.append(FileChange(
                status=status,
                old_path=parts[1],
                new_path=parts[2]
            ))
        elif status == "C":
            # 复制: C\told_path\tnew_path
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


def get_staged_diff() -> str:
    """获取暂存区的详细差异"""
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        return ""

    return result.stdout


def get_staged_changes(max_diff_lines: int = 500) -> StagedChanges:
    """获取完整的暂存区变更信息

    Args:
        max_diff_lines: diff 内容最大行数限制，防止过长

    Returns:
        StagedChanges 对象
    """
    files = get_staged_files()
    diff = get_staged_diff()

    # 限制 diff 行数
    if diff:
        lines = diff.split("\n")
        if len(lines) > max_diff_lines:
            diff = "\n".join(lines[:max_diff_lines])
            diff += f"\n\n... (truncated, {len(lines) - max_diff_lines} more lines)"

    return StagedChanges(files=files, diff_content=diff)


def get_status_symbol(status: str) -> str:
    """获取状态对应的符号/描述"""
    symbols = {
        "A": "新增",
        "M": "修改",
        "D": "删除",
        "R": "重命名",
        "C": "复制",
        "T": "类型变更"
    }
    return symbols.get(status, status)


def commit_changes(message: str) -> Tuple[bool, str, str]:
    """执行 git commit

    Args:
        message: commit message

    Returns:
        (success, stdout, stderr)
    """
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
        check=False
    )
    return result.returncode == 0, result.stdout, result.stderr
