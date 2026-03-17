from __future__ import annotations

import numpy as np
from scipy.signal import convolve2d

SCENARIOS = {
    "生态保护优先": {"neighborhood": 0.4, "suitability": 0.3, "constraint": 0.9, "threshold": 0.65},
    "均衡发展": {"neighborhood": 0.5, "suitability": 0.5, "constraint": 0.7, "threshold": 0.55},
    "开发优先": {"neighborhood": 0.6, "suitability": 0.7, "constraint": 0.4, "threshold": 0.5},
}


def _neighbor_density(binary: np.ndarray) -> np.ndarray:
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=float)
    return convolve2d(binary, kernel, mode="same", boundary="symm") / 8.0


def simulate_landscape(base: np.ndarray, suitability: np.ndarray, constraint: np.ndarray, params: dict, steps: int = 8):
    current = base.copy().astype(float)
    for _ in range(steps):
        neigh = _neighbor_density(current)
        score = params["neighborhood"] * neigh + params["suitability"] * suitability
        score = score * (1 - params["constraint"] * constraint)
        growth = (score > params["threshold"]).astype(float)
        current = np.where(current > 0, current, growth)
    change = current - base
    return current, change
