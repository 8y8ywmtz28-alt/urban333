from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd
import requests
import streamlit as st

from .config import DOWNLOAD_DIR, NETWORK_TIMEOUT


def ensure_directories() -> None:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _read_csv_with_fallback(raw: bytes) -> pd.DataFrame:
    for encoding in ["utf-8", "gbk", "utf-8-sig"]:
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=encoding)
        except Exception:
            continue
    raise ValueError("CSV 编码无法识别")


def read_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    raw = uploaded_file.getvalue()
    if suffix in [".csv"]:
        return "table", _read_csv_with_fallback(raw)
    if suffix in [".xlsx", ".xls"]:
        xls = pd.ExcelFile(io.BytesIO(raw))
        sheet = st.selectbox("选择工作表", xls.sheet_names, key=f"sheet_{uploaded_file.name}")
        return "table", pd.read_excel(xls, sheet_name=sheet)
    if suffix in [".geojson", ".shp"]:
        return "vector", gpd.read_file(io.BytesIO(raw) if suffix == ".geojson" else uploaded_file)
    if suffix in [".zip"]:
        zf = zipfile.ZipFile(io.BytesIO(raw))
        if any(name.lower().endswith(".shp") for name in zf.namelist()):
            temp_dir = DOWNLOAD_DIR / f"upload_{Path(uploaded_file.name).stem}"
            temp_dir.mkdir(exist_ok=True)
            zf.extractall(temp_dir)
            shp = next(temp_dir.glob("**/*.shp"))
            return "vector", gpd.read_file(shp)
        return "archive", zf.namelist()
    if suffix in [".tif", ".tiff"]:
        return "raster", raw
    raise ValueError(f"不支持的文件类型: {suffix}")


def download_public_data(url: str) -> Optional[Path]:
    ensure_directories()
    try:
        resp = requests.get(url, timeout=NETWORK_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"下载失败：{exc}")
        return None

    name = url.split("/")[-1] or "download.bin"
    out_path = DOWNLOAD_DIR / name
    out_path.write_bytes(resp.content)
    return out_path


def geocode_place(place_name: str) -> list[dict]:
    endpoint = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "json", "polygon_geojson": 1, "limit": 5}
    headers = {"User-Agent": "geoatelier-local-workbench"}
    try:
        resp = requests.get(endpoint, params=params, headers=headers, timeout=NETWORK_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return []


def fetch_osm_features(bbox: tuple[float, float, float, float], key: str = "highway") -> gpd.GeoDataFrame:
    overpass = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      way[\"{key}\"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      relation[\"{key}\"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
      node[\"{key}\"]({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]});
    );
    out body;
    >;
    out skel qt;
    """
    try:
        resp = requests.get(overpass, params={"data": query}, timeout=NETWORK_TIMEOUT)
        resp.raise_for_status()
        data = resp.json().get("elements", [])
    except requests.RequestException:
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

    points = []
    for item in data:
        if item.get("type") == "node" and "lat" in item and "lon" in item:
            points.append({"id": item.get("id"), "tag": key, "geometry": gpd.points_from_xy([item["lon"]], [item["lat"]])[0]})
    return gpd.GeoDataFrame(points, crs="EPSG:4326") if points else gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
