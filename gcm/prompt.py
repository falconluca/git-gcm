"""提示词模板模块"""

from gcm.git import StagedChanges


class PromptBuilder:
    """构建发送给大模型的系统/用户提示词"""

    SYSTEM_PROMPT = """你是一位专业的 Git 提交信息生成助手。你的任务是根据代码变更生成清晰、准确、符合规范的 commit message。

## 输出规则

1. 必须直接输出 commit message，不要有任何前言或解释
2. commit message 应该使用中文（除非用户指定英文）
3. 遵循 Conventional Commits 规范

## Commit Message 格式

### 精简模式
一行简洁的描述，格式：<type>(<scope>): <description>

### 详细模式
第一行：<type>(<scope>): <description>
（空行）
（body，详细描述变更内容和原因）
（空行）
（footer，可选，如 Breaking Changes 等）

## Type 类型说明
- feat: 新功能
- fix: 修复 bug
- docs: 文档变更
- style: 代码格式（不影响代码运行的变动）
- refactor: 重构（既不是新增功能，也不是修复 bug）
- perf: 性能优化
- test: 增加测试
- chore: 构建过程或辅助工具的变动
- revert: 回滚
- ci: CI 配置文件和脚本的变动
- build: 影响构建系统或外部依赖的变更

## 要求
- 准确描述变更内容，不要臆测
- 使用动词原形开头（如：添加、修复、更新、优化）
- 简洁明了，避免冗余"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def system_prompt(self) -> str:
        """系统提示词"""
        return self.SYSTEM_PROMPT

    def user_prompt(self, changes: StagedChanges) -> str:
        """根据暂存区变更构建用户提示词

        Args:
            changes: 暂存区变更信息

        Returns:
            用户提示词字符串
        """
        if not changes.files:
            return "暂存区没有任何变更。"

        # 构建文件变更摘要
        file_summary = [file.summary for file in changes.files]

        # 构建提示词
        mode = "详细" if self.verbose else "精简"
        return f"""请根据以下暂存区变更生成{mode}的 commit message。

## 变更文件
{chr(10).join(file_summary)}

## 详细变更内容（diff）
```
{changes.diff_content}
```

请生成{mode}的 commit message："""
