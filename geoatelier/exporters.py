from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio


def export_csv(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def export_geojson(gdf: gpd.GeoDataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, driver="GeoJSON")
    return path


def export_geotiff(array: np.ndarray, profile: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    new_profile = dict(profile)
    if array.ndim == 2:
        array = array[np.newaxis, ...]
    new_profile.update(count=array.shape[0], dtype=str(array.dtype))
    with rasterio.open(path, "w", **new_profile) as dst:
        dst.write(array)
    return path
