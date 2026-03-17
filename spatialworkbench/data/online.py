from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import requests

from spatialworkbench.config import REQUEST_TIMEOUT
from spatialworkbench.data.io import read_vector

HEADERS = {"User-Agent": "spatial-workbench-local/0.1"}


def download_file(url: str, out_path: Path) -> tuple[bool, str]:
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        return True, f"下载成功: {out_path.name}"
    except requests.RequestException as exc:
        return False, f"下载失败: {exc}"


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
    [out:json][timeout:25];
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
    except requests.RequestException:
        return gpd.GeoDataFrame()

    features = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        if "lat" in el and "lon" in el:
            geom = {"type": "Point", "coordinates": [el["lon"], el["lat"]]}
            features.append({"geometry": geom, **tags})
        elif "geometry" in el:
            coords = [[g["lon"], g["lat"]] for g in el["geometry"]]
            geom_type = "LineString" if el.get("type") == "way" else "Polygon"
            geom = {"type": geom_type, "coordinates": coords if geom_type == "LineString" else [coords]}
            features.append({"geometry": geom, **tags})
    if not features:
        return gpd.GeoDataFrame()
    return gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")


def load_world_boundaries() -> gpd.GeoDataFrame:
    return gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
