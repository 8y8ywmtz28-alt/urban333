from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def apply_axes_style(ax, title: str = ""):
    ax.set_title(title, pad=10, fontsize=12)
    ax.tick_params(labelsize=9)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)


def plot_raster(arr: np.ndarray, title: str, cmap: str = "viridis"):
    fig, ax = plt.subplots(figsize=(7.6, 4.8), dpi=130, constrained_layout=True)
    im = ax.imshow(arr, cmap=cmap)
    apply_axes_style(ax, title)
    ax.set_xticks([])
    ax.set_yticks([])
    cbar = fig.colorbar(im, ax=ax, fraction=0.042, pad=0.02)
    cbar.ax.tick_params(labelsize=8)
    return fig


def plot_series_distribution(series: pd.Series, title: str):
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=130, constrained_layout=True)
    series.astype(str).value_counts().sort_index().plot(kind="bar", ax=ax, color="#4C78A8")
    apply_axes_style(ax, title)
    ax.set_ylabel("数量", fontsize=10)
    ax.tick_params(axis="x", rotation=25)
    return fig


def plot_importance(importance: pd.Series, title: str = "特征重要性"):
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=130, constrained_layout=True)
    importance.sort_values().plot(kind="barh", ax=ax, color="#5AA5A5")
    apply_axes_style(ax, title)
    ax.set_xlabel("重要性", fontsize=10)
    return fig
