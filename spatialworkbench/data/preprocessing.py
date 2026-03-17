from __future__ import annotations

from typing import Optional

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject


def ensure_vector_crs(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        gdf = gdf.set_crs(target_crs)
    if str(gdf.crs) != str(target_crs):
        gdf = gdf.to_crs(target_crs)
    return gdf


def align_raster_to_reference(src: rasterio.DatasetReader, ref: rasterio.DatasetReader, band: int = 1) -> np.ndarray:
    dst = np.empty((ref.height, ref.width), dtype=np.float32)
    reproject(
        source=rasterio.band(src, band),
        destination=dst,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=ref.transform,
        dst_crs=ref.crs,
        resampling=Resampling.bilinear,
    )
    return dst


def clip_raster_by_vector(src: rasterio.DatasetReader, gdf: gpd.GeoDataFrame, crop: bool = True):
    gdf = ensure_vector_crs(gdf, src.crs)
    out_image, out_transform = mask(src, gdf.geometry, crop=crop)
    return out_image, out_transform


def overlap_window_stats(src1: rasterio.DatasetReader, src2: rasterio.DatasetReader) -> dict:
    bounds1 = src1.bounds
    bounds2 = src2.bounds
    overlap = (
        max(bounds1.left, bounds2.left),
        max(bounds1.bottom, bounds2.bottom),
        min(bounds1.right, bounds2.right),
        min(bounds1.top, bounds2.top),
    )
    valid = overlap[0] < overlap[2] and overlap[1] < overlap[3]
    return {
        "valid_overlap": valid,
        "overlap_bounds": overlap,
        "res1": src1.res,
        "res2": src2.res,
    }
