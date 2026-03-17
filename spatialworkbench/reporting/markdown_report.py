from __future__ import annotations

from datetime import datetime


def build_markdown_report(name: str, inputs: str, methods: str, params: dict, key_results: str, conclusion: str) -> str:
    param_lines = "\n".join([f"- **{k}**: {v}" for k, v in params.items()])
    return f"""# {name} 分析摘要

- 生成时间：{datetime.now():%Y-%m-%d %H:%M}

## 输入说明
{inputs}

## 方法说明
{methods}

## 参数设置
{param_lines}

## 关键结果
{key_results}

## 简短结论
{conclusion}
"""
