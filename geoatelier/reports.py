from __future__ import annotations

from datetime import datetime
from pathlib import Path


def build_markdown_report(title: str, inputs: str, method: str, params: str, results: str, conclusion: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# {title}\n\n- 生成时间：{now}\n\n## 输入说明\n{inputs}\n\n## 方法\n{method}\n\n## 参数设置\n{params}\n\n## 关键结果\n{results}\n\n## 结论\n{conclusion}\n"""


def save_markdown(text: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
