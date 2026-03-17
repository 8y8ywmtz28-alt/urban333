from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin


def export_csv(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False, encoding="utf-8-sig")


def export_geojson(gdf: gpd.GeoDataFrame, path: Path):
    gdf.to_file(path, driver="GeoJSON")


def export_png(fig, path: Path):
    fig.savefig(path, dpi=160, bbox_inches="tight")


def export_geotiff(arr: np.ndarray, path: Path, crs="EPSG:4326", transform=None):
    transform = transform or from_origin(0, 0, 1, 1)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=arr.shape[0],
        width=arr.shape[1],
        count=1,
        dtype=arr.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(arr, 1)
