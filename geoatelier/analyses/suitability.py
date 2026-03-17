from __future__ import annotations

import numpy as np
import pandas as pd

from ..preprocessing import normalize


def weighted_suitability(df: pd.DataFrame, indicators: list[str], weights: list[float], inverse_flags: list[bool]):
    values = []
    for fld, inv in zip(indicators, inverse_flags):
        values.append(normalize(df[fld].to_numpy(dtype=float), inverse=inv))
    matrix = np.vstack(values).T
    w = np.array(weights, dtype=float)
    w = w / w.sum()
    score = matrix @ w
    bins = np.quantile(score, [0, 0.2, 0.4, 0.6, 0.8, 1])
    level = pd.cut(score, bins=np.unique(bins), include_lowest=True, labels=["低", "较低", "中", "较高", "高"][: len(np.unique(bins)) - 1])
    return score, level
