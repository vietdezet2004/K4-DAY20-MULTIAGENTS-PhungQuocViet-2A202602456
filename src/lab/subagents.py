"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when you need to inspect files, explore repository structure, analyze data schemas, "
                "or read documentation before making any modifications."
            ),
            "system_prompt": (
                "You are an exploratory engineering subagent. Your role is to examine the workspace, "
                "read relevant files and instructions, investigate schemas and error logs, and report facts accurately. "
                "Do not modify files or make code changes."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when you need to write code, edit scripts, modify datasets, and run commands or tests to resolve issues."
            ),
            "system_prompt": (
                "You are an implementation subagent. Your role is to edit and create files according to the task requirements, "
                "run tests or validation scripts in the workspace, and report the actions and test outcomes back clearly."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use when you need an independent verification of the changes, checking compliance with constraints and test suites."
            ),
            "system_prompt": (
                "You are a code and data review subagent. Your role is to review modified files, run test suites, "
                "verify edge cases and specific output conventions, and report any discrepancies without introducing new changes."
            ),
        },
    ]
