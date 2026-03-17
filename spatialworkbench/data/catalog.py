from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterio


def summarize_table(df: pd.DataFrame) -> dict:
    return {
        "行数": len(df),
        "列数": len(df.columns),
        "字段": ",".join(df.columns[:6]),
    }


def summarize_vector(gdf: gpd.GeoDataFrame) -> dict:
    bounds = gdf.total_bounds if len(gdf) else [None, None, None, None]
    return {
        "要素数": len(gdf),
        "坐标系": str(gdf.crs),
        "范围": f"{bounds[0]:.4f},{bounds[1]:.4f},{bounds[2]:.4f},{bounds[3]:.4f}" if len(gdf) else "空",
    }


def summarize_raster(path: str | Path) -> dict:
    with rasterio.open(path) as src:
        return {
            "波段数": src.count,
            "分辨率": f"{src.res[0]:.5f},{src.res[1]:.5f}",
            "坐标系": str(src.crs),
            "宽高": f"{src.width}x{src.height}",
        }


def infer_usable_templates(kind: str) -> list[str]:
    mapping = {
        "raster": ["土地变化检测", "情景模拟"],
        "vector": ["空间叠加与缓冲", "生态-旅游耦合"],
        "table": ["生态-旅游耦合", "适宜性评价", "驱动因子分析"],
    }
    return mapping.get(kind, [])
