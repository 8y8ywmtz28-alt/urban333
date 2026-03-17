from __future__ import annotations

from io import BytesIO
from pathlib import Path
import tempfile
import zipfile

import geopandas as gpd
import pandas as pd
import rasterio


def read_table(path_or_buffer, sheet_name=0, encoding="utf-8") -> pd.DataFrame:
    name = str(path_or_buffer)
    if name.lower().endswith(".csv"):
        try:
            return pd.read_csv(path_or_buffer, encoding=encoding)
        except UnicodeDecodeError:
            return pd.read_csv(path_or_buffer, encoding="gbk")
    return pd.read_excel(path_or_buffer, sheet_name=sheet_name)


def read_vector(path_or_buffer) -> gpd.GeoDataFrame:
    if isinstance(path_or_buffer, (str, Path)) and str(path_or_buffer).lower().endswith(".zip"):
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(path_or_buffer) as zf:
                zf.extractall(tmp)
            shp_list = list(Path(tmp).glob("**/*.shp"))
            if not shp_list:
                raise FileNotFoundError("ZIP 中未找到 shp 文件")
            return gpd.read_file(shp_list[0])
    return gpd.read_file(path_or_buffer)


def read_raster(path):
    return rasterio.open(path)


def save_upload_to_temp(uploaded_file) -> Path:
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return Path(tmp.name)


def bytes_to_file(data: bytes, suffix: str) -> Path:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        return Path(tmp.name)
