from __future__ import annotations

import numpy as np
import pandas as pd

from ..preprocessing import normalize


def weighted_index(df: pd.DataFrame, fields: list[str], weights: list[float], inverse_flags: list[bool]):
    mat = []
    for fld, inv in zip(fields, inverse_flags):
        mat.append(normalize(df[fld].to_numpy(dtype=float), inverse=inv))
    matrix = np.vstack(mat).T
    w = np.array(weights, dtype=float)
    w = w / w.sum()
    return matrix @ w


def coupling_degree(eco_idx: np.ndarray, tour_idx: np.ndarray):
    c = 2 * np.sqrt(eco_idx * tour_idx) / (eco_idx + tour_idx + 1e-6)
    t = 0.5 * eco_idx + 0.5 * tour_idx
    d = np.sqrt(c * t)
    level = pd.cut(d, bins=[-0.01, 0.3, 0.5, 0.7, 1.0], labels=["失调", "勉强协调", "中度协调", "高质量协调"])
    return c, d, level
