from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from .font_manager import create_figure


def plot_raster(data: np.ndarray, title: str, cmap: str = "viridis"):
    fig, ax = create_figure((7.5, 5.2))
    im = ax.imshow(data, cmap=cmap)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    cbar = fig.colorbar(im, ax=ax, shrink=0.82)
    cbar.ax.tick_params(labelsize=8)
    return fig


def plot_bar(labels, values, title: str):
    fig, ax = create_figure((7.2, 4.5))
    ax.bar(labels, values, color="#2a9d8f")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=25)
    return fig


def plot_two_maps(left: np.ndarray, right: np.ndarray, titles: tuple[str, str]):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=120)
    for ax, data, title in zip(axes, [left, right], titles):
        m = ax.imshow(data, cmap="YlGn")
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(m, ax=ax, shrink=0.75)
    fig.tight_layout()
    return fig
