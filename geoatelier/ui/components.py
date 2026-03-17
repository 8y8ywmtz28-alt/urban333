from __future__ import annotations

import streamlit as st


def inject_style():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
        .stMetric {background:#f8fafc;border:1px solid #e2e8f0;padding:0.6rem;border-radius:10px;}
        .hero {padding:1rem 1.2rem;background:#f0f9ff;border-radius:12px;border:1px solid #bae6fd;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str):
    st.markdown(f"<div class='hero'><h2>{title}</h2><p>{subtitle}</p></div>", unsafe_allow_html=True)
