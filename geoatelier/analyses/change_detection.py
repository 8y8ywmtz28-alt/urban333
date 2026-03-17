from __future__ import annotations

import numpy as np


def ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    den = np.where((nir + red) == 0, 1e-6, nir + red)
    return (nir - red) / den


def detect_change(arr1: np.ndarray, arr2: np.ndarray, threshold: float = 0.1) -> dict:
    diff = arr2 - arr1
    mask = np.abs(diff) >= threshold
    return {
        "difference": diff,
        "mask": mask.astype(np.uint8),
        "changed_pixels": int(mask.sum()),
        "changed_ratio": float(mask.mean()),
    }
