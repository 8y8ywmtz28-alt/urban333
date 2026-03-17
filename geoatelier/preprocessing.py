from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject


@dataclass
class RasterBundle:
    array: np.ndarray
    transform: any
    crs: any
    profile: dict


def read_raster(path: str) -> RasterBundle:
    with rasterio.open(path) as src:
        arr = src.read()
        return RasterBundle(arr, src.transform, src.crs, src.profile)


def align_rasters(base: RasterBundle, target: RasterBundle) -> RasterBundle:
    output = np.zeros((target.array.shape[0], base.profile["height"], base.profile["width"]), dtype=np.float32)
    for band in range(target.array.shape[0]):
        reproject(
            source=target.array[band],
            destination=output[band],
            src_transform=target.transform,
            src_crs=target.crs,
            dst_transform=base.transform,
            dst_crs=base.crs,
            resampling=Resampling.bilinear,
        )
    profile = dict(base.profile)
    profile.update(count=output.shape[0], dtype="float32")
    return RasterBundle(output, base.transform, base.crs, profile)


def normalize(values: np.ndarray, inverse: bool = False) -> np.ndarray:
    vmin, vmax = np.nanmin(values), np.nanmax(values)
    if np.isclose(vmin, vmax):
        scaled = np.zeros_like(values, dtype=float)
    else:
        scaled = (values - vmin) / (vmax - vmin)
    return 1 - scaled if inverse else scaled
