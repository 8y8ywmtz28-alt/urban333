from __future__ import annotations

import numpy as np


def compute_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    denom = np.where((nir + red) == 0, np.nan, nir + red)
    return (nir - red) / denom


def detect_change(arr1: np.ndarray, arr2: np.ndarray, threshold: float = 0.1):
    diff = arr2 - arr1
    intensity = np.abs(diff)
    mask = intensity >= threshold
    total = np.isfinite(intensity).sum()
    changed = mask.sum()
    area_ratio = float(changed / total) if total else 0.0
    return {
        "diff": diff,
        "intensity": intensity,
        "mask": mask.astype("uint8"),
        "changed_pixels": int(changed),
        "changed_ratio": area_ratio,
    }


def infer_red_nir_band_indexes(count: int) -> tuple[int, int] | None:
    if count >= 4:
        return 3, 4
    if count == 2:
        return 1, 2
    return None
