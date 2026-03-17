from __future__ import annotations

import geopandas as gpd


def buffer_and_intersect(base: gpd.GeoDataFrame, targets: gpd.GeoDataFrame, distance: float):
    buffered = base.copy()
    buffered["geometry"] = buffered.geometry.buffer(distance)
    inter = gpd.overlay(buffered, targets, how="intersection")
    inter["area"] = inter.geometry.area
    return buffered, inter
