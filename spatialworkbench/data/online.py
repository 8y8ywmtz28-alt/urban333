from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import geopandas as gpd
import requests
from shapely.geometry import LineString, Point, Polygon

from spatialworkbench.config import REQUEST_TIMEOUT

HEADERS = {"User-Agent": "spatial-workbench-local/0.2"}


def download_file(url: str, out_path: Path) -> tuple[bool, str]:
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        return True, f"下载成功: {out_path.name}"
    except requests.Timeout:
        return False, "下载超时，请稍后重试或改用本地文件。"
    except requests.RequestException as exc:
        return False, f"下载失败: {exc}"


@lru_cache(maxsize=32)
def geocode_place(place_name: str) -> list[dict[str, Any]]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "jsonv2", "polygon_geojson": 1, "limit": 5}
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return []


def fetch_osm_features(bbox: tuple[float, float, float, float], feature_type: str = "highway") -> gpd.GeoDataFrame:
    south, west, north, east = bbox
    query = f"""
    [out:json][timeout:20];
    (
      way["{feature_type}"]({south},{west},{north},{east});
      relation["{feature_type}"]({south},{west},{north},{east});
      node["{feature_type}"]({south},{west},{north},{east});
    );
    out geom;
    """
    try:
        resp = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.Timeout:
        return gpd.GeoDataFrame()
    except requests.RequestException:
        return gpd.GeoDataFrame()

    geoms: list = []
    attrs: list[dict[str, Any]] = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        if "lat" in el and "lon" in el:
            geoms.append(Point(el["lon"], el["lat"]))
            attrs.append(tags)
        elif "geometry" in el:
            coords = [(g["lon"], g["lat"]) for g in el["geometry"]]
            if len(coords) < 2:
                continue
            if el.get("type") == "way":
                geoms.append(LineString(coords))
            else:
                geoms.append(Polygon(coords))
            attrs.append(tags)
    if not geoms:
        return gpd.GeoDataFrame()
    return gpd.GeoDataFrame(attrs, geometry=geoms, crs="EPSG:4326")


@lru_cache(maxsize=1)
def load_world_boundaries() -> gpd.GeoDataFrame:
    return gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
