from __future__ import annotations

import numpy as np
import pandas as pd


def minmax_scale(series: pd.Series, positive: bool = True) -> pd.Series:
    s = series.astype(float)
    if s.max() == s.min():
        return pd.Series(np.ones(len(s)), index=s.index)
    scaled = (s - s.min()) / (s.max() - s.min())
    return scaled if positive else 1 - scaled


def composite_index(df: pd.DataFrame, indicators: dict[str, bool], weights: dict[str, float] | None = None) -> pd.Series:
    scaled = pd.DataFrame({col: minmax_scale(df[col], pos) for col, pos in indicators.items()})
    if not weights:
        weights = {c: 1 / len(indicators) for c in indicators}
    w = pd.Series(weights)
    w = w / w.sum()
    return (scaled * w).sum(axis=1)


def coupling_coordination(eco: pd.Series, tour: pd.Series):
    c = 2 * np.sqrt(eco * tour) / (eco + tour + 1e-9)
    t = 0.5 * eco + 0.5 * tour
    d = np.sqrt(c * t)
    level = pd.cut(
        d,
        bins=[-0.001, 0.3, 0.5, 0.7, 0.85, 1.0],
        labels=["失调", "勉强协调", "初级协调", "良好协调", "优质协调"],
    )
    return c, d, level
