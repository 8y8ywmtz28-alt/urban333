from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_raster(arr: np.ndarray, title: str, cmap: str = "viridis"):
    fig, ax = plt.subplots(figsize=(7, 5), dpi=120)
    im = ax.imshow(arr, cmap=cmap)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.colorbar(im, ax=ax, shrink=0.75)
    return fig


def plot_series_distribution(series: pd.Series, title: str):
    fig, ax = plt.subplots(figsize=(7, 4), dpi=120)
    series.value_counts().sort_index().plot(kind="bar", ax=ax, color="#4C78A8")
    ax.set_title(title)
    ax.set_ylabel("数量")
    ax.tick_params(axis="x", rotation=20)
    return fig


def plot_importance(importance: pd.Series, title: str = "特征重要性"):
    fig, ax = plt.subplots(figsize=(7, 4), dpi=120)
    importance.sort_values().plot(kind="barh", ax=ax, color="#72B7B2")
    ax.set_title(title)
    ax.set_xlabel("重要性")
    return fig
