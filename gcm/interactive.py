"""交互式提交模块（基于 questionary 的 TUI 交互）。

封装生成 commit message 后的方向键菜单交互与提交。
"""

import sys

import questionary
from questionary import Style

from gcm.git import GitRepo


class InteractiveCommitter:
    """生成 commit message 后的 TUI 交互与提交"""

    # 自定义 TUI 配色：箭头与当前高亮项统一为青色
    _STYLE = Style([
        ("qmark", "fg:#5fd7ff bold"),
        ("pointer", "fg:#5fd7ff bold"),
        ("highlighted", "fg:#5fd7ff bold"),
        ("selected", "fg:#5fd7ff"),
        ("answer", "fg:#5fd7ff bold"),
        ("instruction", "fg:#808080"),
    ])

    _CHOICE_COMMIT = "提交此 message"
    _CHOICE_EDIT = "修改 message"
    _CHOICE_PRINT = "仅输出，不提交"

    def __init__(self, repo: GitRepo):
        self.repo = repo

    def run(self, commit_msg: str) -> None:
        """展示菜单，允许直接提交、修改后提交或仅输出。

        每轮循环清屏后重新渲染 message 与菜单，避免修改时历史输出堆积。

        Args:
            commit_msg: 生成的初始 commit message
        """
        current = commit_msg
        while True:
            self._clear_screen()
            self._show_message(current)

            choice = questionary.select(
                "请选择操作",
                choices=[self._CHOICE_COMMIT, self._CHOICE_EDIT, self._CHOICE_PRINT],
                qmark="✨",
                pointer="❯",
                style=self._STYLE,
                instruction="(↑↓ 选择, Enter 确认)",
            ).ask()

            # ESC / Ctrl-C → 取消
            if choice is None:
                self._clear_screen()
                print("已取消。")
                return

            if choice == self._CHOICE_PRINT:
                self._clear_screen()
                print(current)
                return

            if choice == self._CHOICE_EDIT:
                new_msg = questionary.text(
                    "输入新的 commit message（留空保留原文）",
                    style=self._STYLE,
                ).ask()
                if new_msg is not None and new_msg.strip():
                    current = new_msg.strip()
                continue

            # _CHOICE_COMMIT：清屏后干净展示最终 message 并提交（无二次确认）
            self._clear_screen()
            self._show_message(current)
            self._commit(current)
            return

    def _clear_screen(self) -> None:
        """清屏并将光标移到左上角（ANSI 转义，现代终端通用）。"""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def _show_message(self, commit_msg: str) -> None:
        """展示当前的 commit message"""
        print("✨ 生成的 commit message：")
        print("-" * 40)
        print(commit_msg)
        print("-" * 40)

    def _commit(self, commit_msg: str) -> None:
        """执行 git commit 并打印结果。

        提交失败时将 git 的错误信息输出到 stderr 并以非零状态码退出。
        """
        result = self.repo.commit(commit_msg)

        if result.success:
            if result.stdout:
                print(result.stdout)
            print("✓ 提交成功")
        else:
            print("提交失败：", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(1)
