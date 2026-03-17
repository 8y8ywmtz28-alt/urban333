from __future__ import annotations

import streamlit as st


def show_exception(context: str, exc: Exception) -> None:
    st.error(f"{context}：{exc}")


def show_hint(text: str) -> None:
    st.caption(f"💡 {text}")


def show_success(text: str) -> None:
    st.success(text)
