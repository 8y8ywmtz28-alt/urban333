from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st


@dataclass
class DataAsset:
    name: str
    kind: str
    source: str
    payload: Any
    summary: dict[str, Any]
    usable_in: list[str]


def init_state() -> None:
    st.session_state.setdefault("assets", {})
    st.session_state.setdefault("results", {})


def register_asset(asset: DataAsset) -> None:
    st.session_state["assets"][asset.name] = asset


def register_result(name: str, payload: Any) -> None:
    st.session_state["results"][name] = payload


def get_asset(name: str) -> DataAsset | None:
    return st.session_state["assets"].get(name)


def list_assets() -> list[DataAsset]:
    return list(st.session_state["assets"].values())
