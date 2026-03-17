from __future__ import annotations

import pandas as pd

from spatialworkbench.analysis.eco_tourism import minmax_scale


def weighted_suitability(df: pd.DataFrame, indicators: dict[str, bool], weights: dict[str, float]):
    normalized = pd.DataFrame({k: minmax_scale(df[k], v) for k, v in indicators.items()})
    w = pd.Series(weights)
    w = w / w.sum()
    score = (normalized * w).sum(axis=1)
    level = pd.qcut(score.rank(method="first"), q=4, labels=["低", "中", "较高", "高"])
    return score, level
