from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams


PREFERRED_FONTS = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Arial Unicode MS",
]


@dataclass
class FontSetupResult:
    font_name: Optional[str]
    warning: Optional[str]


def initialize_matplotlib_fonts() -> FontSetupResult:
    available = {f.name for f in font_manager.fontManager.ttflist}
    selected = next((name for name in PREFERRED_FONTS if name in available), None)

    if selected:
        rcParams["font.sans-serif"] = [selected]
        rcParams["axes.unicode_minus"] = False
        rcParams["figure.autolayout"] = True
        return FontSetupResult(font_name=selected, warning=None)

    rcParams["axes.unicode_minus"] = False
    rcParams["figure.autolayout"] = True
    return FontSetupResult(
        font_name=None,
        warning="系统未找到常见中文字体，将使用默认字体。中文可能显示为方块，请安装微软雅黑或思源黑体。",
    )


def create_figure(figsize=(8, 5)):
    fig, ax = plt.subplots(figsize=figsize, dpi=120)
    return fig, ax
