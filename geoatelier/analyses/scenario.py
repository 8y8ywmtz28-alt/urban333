from __future__ import annotations

import numpy as np


def _neighbor_ratio(grid: np.ndarray) -> np.ndarray:
    total = np.zeros_like(grid, dtype=float)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            total += np.roll(np.roll(grid, dx, axis=0), dy, axis=1)
    return total / 8.0


def simulate_ca(initial: np.ndarray, suitability: np.ndarray, constraint: np.ndarray, steps: int, params: dict):
    grid = initial.astype(float).copy()
    for _ in range(steps):
        neigh = _neighbor_ratio(grid)
        score = (
            params["neighbor_weight"] * neigh
            + params["suitability_weight"] * suitability
            + params["growth_rate"]
            - params["constraint_penalty"] * constraint
        )
        grow = score > np.quantile(score, 0.78)
        grid = np.where((grid < 1) & grow, 1, grid)
    return grid
