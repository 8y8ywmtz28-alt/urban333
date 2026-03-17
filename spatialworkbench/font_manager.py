from __future__ import annotations

import matplotlib
import matplotlib.font_manager as fm

CANDIDATE_FONTS = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Arial Unicode MS",
]


def init_chinese_font() -> tuple[str | None, list[str], str]:
    available = {f.name for f in fm.fontManager.ttflist}
    matched = [name for name in CANDIDATE_FONTS if name in available]
    chosen = matched[0] if matched else None

    if chosen:
        matplotlib.rcParams["font.family"] = "sans-serif"
        matplotlib.rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"]
        message = f"已启用中文字体：{chosen}"
    else:
        matplotlib.rcParams["font.family"] = "sans-serif"
        matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans"]
        message = "未找到常用中文字体，已降级为 DejaVu Sans，中文可能显示不全。"

    matplotlib.rcParams["axes.unicode_minus"] = False
    matplotlib.rcParams["figure.autolayout"] = True
    return chosen, matched, message
