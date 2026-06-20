"""交互式提交模块（基于 questionary 的 TUI 交互）。

负责在生成 commit message 后与用户交互：方向键导航的菜单、修改、提交。
与 CLI 入口（cli.py）解耦，便于单独维护与复用。

入口函数：interactive_commit(commit_msg)
"""

import sys

import questionary
from questionary import Style

from gcm.git import commit_changes


# 自定义 TUI 配色：箭头与当前高亮项统一为青色
_STYLE = Style([
    ("qmark", "fg:#5fd7ff bold"),
    ("pointer", "fg:#5fd7ff bold"),
    ("highlighted", "fg:#5fd7ff bold"),
    ("selected", "fg:#5fd7ff"),
    ("answer", "fg:#5fd7ff bold"),
    ("instruction", "fg:#808080"),
])

# 菜单选项
_CHOICE_COMMIT = "提交此 message"
_CHOICE_EDIT = "修改 message"
_CHOICE_PRINT = "仅输出，不提交"


def interactive_commit(commit_msg: str) -> None:
    """生成 commit message 后的 TUI 交互入口。

    每轮循环清屏后重新渲染 message 与菜单，避免修改时历史输出堆积。

    Args:
        commit_msg: 生成的初始 commit message
    """
    current = commit_msg
    while True:
        _clear_screen()
        _show_message(current)

        choice = questionary.select(
            "请选择操作",
            choices=[_CHOICE_COMMIT, _CHOICE_EDIT, _CHOICE_PRINT],
            qmark="✨",
            pointer="❯",
            style=_STYLE,
            instruction="(↑↓ 选择, Enter 确认)",
        ).ask()

        # ESC / Ctrl-C → 取消
        if choice is None:
            _clear_screen()
            print("已取消。")
            return

        if choice == _CHOICE_PRINT:
            _clear_screen()
            print(current)
            return

        if choice == _CHOICE_EDIT:
            new_msg = questionary.text(
                "输入新的 commit message（留空保留原文）",
                style=_STYLE,
            ).ask()
            if new_msg is not None and new_msg.strip():
                current = new_msg.strip()
            continue

        # _CHOICE_COMMIT：清屏后干净展示最终 message 并提交（无二次确认）
        _clear_screen()
        _show_message(current)
        _run_commit(current)
        return


def _clear_screen() -> None:
    """清屏并将光标移到左上角（ANSI 转义，现代终端通用）。"""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def _show_message(commit_msg: str) -> None:
    """展示当前的 commit message"""
    print("✨ 生成的 commit message：")
    print("-" * 40)
    print(commit_msg)
    print("-" * 40)


def _run_commit(commit_msg: str) -> None:
    """执行 git commit 并打印结果。

    提交失败时将 git 的错误信息输出到 stderr 并以非零状态码退出。
    """
    success, stdout, stderr = commit_changes(commit_msg)

    if success:
        if stdout:
            print(stdout)
        print("✓ 提交成功")
    else:
        print("提交失败：", file=sys.stderr)
        if stderr:
            print(stderr, file=sys.stderr)
        sys.exit(1)
