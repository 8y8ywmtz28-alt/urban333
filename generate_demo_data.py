from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Point, Polygon

ROOT = Path(__file__).resolve().parent
DEMO = ROOT / "data" / "demo"


def write_raster(path: Path, arr: np.ndarray):
    transform = from_origin(500000, 4500000, 30, 30)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=arr.shape[0],
        width=arr.shape[1],
        count=1,
        dtype=arr.dtype,
        crs="EPSG:3857",
        transform=transform,
    ) as dst:
        dst.write(arr, 1)


def main():
    DEMO.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2024)
    h, w = 160, 160
    yy, xx = np.mgrid[0:h, 0:w]

    core = np.exp(-(((xx - 75) ** 2 + (yy - 85) ** 2) / 2200))
    protect = (xx < 45) & (yy < 60)
    expand = (xx > 90) & (yy > 80)

    land_2020 = np.clip(core + 0.1 * rng.normal(size=(h, w)), 0, 1).astype("float32")
    land_2024 = np.clip(land_2020 + expand * 0.24 - protect * 0.1 + 0.05 * rng.normal(size=(h, w)), 0, 1).astype("float32")
    write_raster(DEMO / "land_2020.tif", land_2020)
    write_raster(DEMO / "land_2024.tif", land_2024)

    boundary = gpd.GeoDataFrame(
        {"name": ["研究区"]},
        geometry=[Polygon([(500000, 4495200), (504800, 4495200), (504800, 4500000), (500000, 4500000)])],
        crs="EPSG:3857",
    )
    boundary.to_file(DEMO / "boundary.geojson", driver="GeoJSON")

    poi_points = [Point(500600 + i * 450, 4496000 + (i % 5) * 420) for i in range(20)]
    poi = gpd.GeoDataFrame({"poi_type": ["景点"] * 20}, geometry=poi_points, crs="EPSG:3857")
    poi.to_file(DEMO / "poi.geojson", driver="GeoJSON")

    regions = [f"区域{i}" for i in range(1, 11)]
    eco_tour = pd.DataFrame(
        {
            "region": regions,
            "green_rate": np.linspace(0.35, 0.82, 10),
            "water_quality": np.linspace(0.4, 0.88, 10)[::-1],
            "traffic_access": np.linspace(0.3, 0.92, 10),
            "service_density": np.linspace(0.25, 0.85, 10) + rng.normal(0, 0.03, 10),
        }
    )
    eco_tour.to_csv(DEMO / "eco_tourism.csv", index=False, encoding="utf-8-sig")

    suit = pd.DataFrame(
        {
            "id": np.arange(1, 151),
            "x": rng.uniform(0, 100, 150),
            "y": rng.uniform(0, 100, 150),
            "slope": rng.uniform(2, 26, 150),
            "distance_road": rng.uniform(50, 3000, 150),
            "distance_water": rng.uniform(20, 2000, 150),
            "landscape_score": rng.uniform(0.2, 0.95, 150),
        }
    )
    suit.to_csv(DEMO / "suitability_samples.csv", index=False, encoding="utf-8-sig")

    drivers = pd.DataFrame(
        {
            "road_density": rng.uniform(0, 1, 260),
            "poi_density": rng.uniform(0, 1, 260),
            "elevation": rng.uniform(10, 400, 260),
            "policy_support": rng.uniform(0, 1, 260),
            "expansion_class": rng.integers(0, 2, 260),
        }
    )
    drivers.to_csv(DEMO / "driver_samples.csv", index=False, encoding="utf-8-sig")
    print(f"示例数据已生成：{DEMO}")


if __name__ == "__main__":
    main()
