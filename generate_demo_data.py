from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Point, Polygon

root = Path(__file__).resolve().parent
demo = root / "data" / "demo"
demo.mkdir(parents=True, exist_ok=True)

np.random.seed(42)
size = 120
x, y = np.meshgrid(np.linspace(-1, 1, size), np.linspace(-1, 1, size))
center = np.exp(-(x**2 + y**2) * 3)
ring = np.exp(-((np.sqrt(x**2 + y**2) - 0.6) ** 2) * 30)

red1 = 0.3 + 0.2 * (1 - center) + 0.03 * np.random.randn(size, size)
nir1 = 0.5 + 0.3 * center + 0.03 * np.random.randn(size, size)
red2 = red1 + 0.12 * ring
nir2 = nir1 - 0.08 * ring

transform = from_origin(116.0, 40.5, 0.005, 0.005)
for name, red, nir in [("raster_t1.tif", red1, nir1), ("raster_t2.tif", red2, nir2)]:
    with rasterio.open(demo / name, "w", driver="GTiff", width=size, height=size, count=4, dtype="float32", crs="EPSG:4326", transform=transform) as dst:
        dst.write((red * 0.8).astype("float32"), 1)
        dst.write(red.astype("float32"), 2)
        dst.write(nir.astype("float32"), 3)
        dst.write((nir * 1.1).astype("float32"), 4)

poly = Polygon([(116.05, 39.95), (116.55, 39.95), (116.55, 40.35), (116.05, 40.35)])
gdf = gpd.GeoDataFrame({"name": ["study_area"]}, geometry=[poly], crs="EPSG:4326")
gdf.to_file(demo / "boundary.geojson", driver="GeoJSON")

regions = [f"区域{i}" for i in range(1, 11)]
eco_tour = pd.DataFrame(
    {
        "region": regions,
        "greening": np.linspace(0.4, 0.9, 10),
        "water_quality": np.linspace(0.5, 0.95, 10)[::-1],
        "scenic_score": np.linspace(0.3, 0.92, 10),
        "accessibility": np.linspace(0.2, 0.85, 10),
    }
)
eco_tour.to_csv(demo / "eco_tourism.csv", index=False, encoding="utf-8-sig")

suit = pd.DataFrame(
    {
        "region": regions,
        "slope": np.linspace(5, 35, 10),
        "distance_to_road": np.linspace(0.2, 4.0, 10),
        "eco_sensitivity": np.linspace(0.8, 0.2, 10),
        "service_density": np.linspace(0.2, 1.0, 10),
    }
)
suit.to_csv(demo / "suitability.csv", index=False, encoding="utf-8-sig")

driver = pd.DataFrame(
    {
        "dist_center": np.random.uniform(0.1, 15, 220),
        "dist_road": np.random.uniform(0.01, 8, 220),
        "elevation": np.random.uniform(20, 300, 220),
        "poi_density": np.random.uniform(0, 1, 220),
        "ndvi": np.random.uniform(0.1, 0.9, 220),
    }
)
driver["expansion"] = 0.4 * driver["poi_density"] - 0.3 * driver["dist_road"] + 0.2 * driver["ndvi"] + np.random.normal(0, 0.1, 220)
driver.to_csv(demo / "drivers.csv", index=False, encoding="utf-8-sig")

base_binary = ((center + 0.3 * np.random.rand(size, size)) > 0.7).astype(float)
suitability = np.clip(center + 0.5 * ring, 0, 1)
constraint = ((x < -0.3) & (y > 0.2)).astype(float)
np.save(demo / "base_binary.npy", base_binary)
np.save(demo / "suitability.npy", suitability)
np.save(demo / "constraint.npy", constraint)

poi = gpd.GeoDataFrame(
    {"name": ["核心景点", "次级景点", "保护站"]},
    geometry=[Point(116.22, 40.15), Point(116.36, 40.10), Point(116.42, 40.26)],
    crs="EPSG:4326",
)
poi.to_file(demo / "poi.geojson", driver="GeoJSON")

print(f"Demo data generated at: {demo}")
