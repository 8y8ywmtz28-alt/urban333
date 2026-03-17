from __future__ import annotations

import geopandas as gpd


def buffer_and_overlay(gdf: gpd.GeoDataFrame, distance: float, target: gpd.GeoDataFrame):
    buffered = gdf.copy()
    buffered["geometry"] = buffered.geometry.buffer(distance)
    inter = gpd.overlay(buffered, target, how="intersection")
    inter["overlay_area"] = inter.geometry.area
    return buffered, inter
