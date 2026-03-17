import streamlit as st

from spatialworkbench.config import APP_SUBTITLE, APP_TITLE


def render_home():
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    c1, c2, c3 = st.columns(3)
    c1.metric("快速开始", "导入数据 → 选模板 → 导出")
    c2.metric("模板数量", "6")
    c3.metric("运行方式", "本地离线优先")

    st.markdown("""
<div class='card'>
<b>工作台入口建议</b>
<ul>
<li>数据中心：加载本地文件或在线抓取数据。</li>
<li>分析模板：土地变化、耦合分析、适宜性、驱动因子、情景模拟、叠加缓冲。</li>
<li>结果导出：PNG、CSV、GeoTIFF、GeoJSON、Markdown 摘要。</li>
</ul>
</div>
""", unsafe_allow_html=True)
