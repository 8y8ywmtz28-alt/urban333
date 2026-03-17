from __future__ import annotations

import streamlit as st

from spatialworkbench.config import APP_SUBTITLE, APP_TITLE
from spatialworkbench.core.state import list_assets


def render_home() -> None:
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    assets = list_assets()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("已载入数据", len(assets))
    c2.metric("模板数量", 6)
    c3.metric("运行模式", "本地优先")
    c4.metric("导出目录", "exports/")

    st.markdown("<div class='section-title'>工作入口</div>", unsafe_allow_html=True)
    x1, x2, x3 = st.columns(3)
    x1.markdown("<div class='card fade-in'><span class='badge'>1</span><b>数据中心</b><br/>导入本地数据、在线拉取、查看数据摘要。</div>", unsafe_allow_html=True)
    x2.markdown("<div class='card fade-in'><span class='badge'>2</span><b>分析模板</b><br/>按目标选择模板并进行参数化分析。</div>", unsafe_allow_html=True)
    x3.markdown("<div class='card fade-in'><span class='badge'>3</span><b>结果导出</b><br/>输出图件、表格、栅格和 Markdown 报告。</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>当前数据概览</div>", unsafe_allow_html=True)
    if not assets:
        st.info("当前未载入数据。可前往“数据中心”导入本地文件，或加载示例数据。")
        return

    rows = []
    for a in assets:
        rows.append(
            {
                "名称": a.name,
                "类型": a.kind,
                "来源": a.source,
                "可用于": "、".join(a.usable_in),
                "摘要": "；".join([f"{k}:{v}" for k, v in a.summary.items()][:3]),
            }
        )
    st.dataframe(rows, use_container_width=True)
