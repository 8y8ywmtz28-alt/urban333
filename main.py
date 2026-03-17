from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import streamlit as st

from geoatelier.analyses.change_detection import detect_change, ndvi
from geoatelier.analyses.coupling import coupling_degree, weighted_index
from geoatelier.analyses.drivers import run_driver_model
from geoatelier.analyses.overlay import buffer_and_intersect
from geoatelier.analyses.scenario import simulate_ca
from geoatelier.analyses.suitability import weighted_suitability
from geoatelier.config import APP_TAGLINE, APP_TITLE, DEFAULT_SCENARIOS, DEMO_DIR, OUTPUT_DIR
from geoatelier.datahub import download_public_data, fetch_osm_features, geocode_place, read_uploaded_file
from geoatelier.exporters import export_csv, export_geotiff
from geoatelier.font_manager import initialize_matplotlib_fonts
from geoatelier.reports import build_markdown_report, save_markdown
from geoatelier.ui.components import hero, inject_style
from geoatelier.visualization import plot_bar, plot_raster, plot_two_maps

st.set_page_config(page_title=APP_TITLE, layout="wide")
inject_style()
font_status = initialize_matplotlib_fonts()
if font_status.warning:
    st.warning(font_status.warning)


@st.cache_data
def load_demo_table(name: str):
    return pd.read_csv(DEMO_DIR / name)


def app_home():
    hero(APP_TITLE, APP_TAGLINE)
    c1, c2, c3 = st.columns(3)
    c1.info("快速开始：先点‘数据中心’，导入或生成示例数据。")
    c2.info("模板入口：依次体验变化检测、耦合分析、适宜性、驱动因子与情景模拟。")
    c3.info("结果导出：支持 PNG、CSV、GeoTIFF、GeoJSON、Markdown 摘要。")


def tab_data_center():
    st.subheader("数据中心")
    local_tab, net_tab = st.tabs(["本地文件导入", "在线数据获取"])
    with local_tab:
        uploads = st.file_uploader("上传数据（可多选）", accept_multiple_files=True)
        if uploads:
            for up in uploads:
                try:
                    kind, data = read_uploaded_file(up)
                    st.success(f"{up.name} 导入成功，类型：{kind}")
                    if kind == "table":
                        st.dataframe(data.head())
                    elif kind == "vector":
                        st.write(data.head())
                except Exception as exc:
                    st.error(f"{up.name} 导入失败：{exc}")

    with net_tab:
        url = st.text_input("URL 直连下载（GeoJSON/CSV/ZIP/TIFF）")
        if st.button("下载公开数据") and url:
            path = download_public_data(url)
            if path:
                st.success(f"下载完成：{path}")

        place = st.text_input("地名检索（Nominatim）")
        if st.button("查询地理编码") and place:
            rs = geocode_place(place)
            if rs:
                st.json(rs[0])
            else:
                st.warning("地理编码服务暂不可用，可改用本地数据继续。")

        st.caption("OSM 抓取示例（WGS84）")
        bbox = st.text_input("bbox(minx,miny,maxx,maxy)", value="116.2,39.8,116.6,40.1")
        if st.button("抓取道路点样本"):
            try:
                b = tuple(map(float, bbox.split(",")))
                gdf = fetch_osm_features(b, key="highway")
                st.write(gdf.head())
            except Exception as exc:
                st.error(f"抓取失败：{exc}")


def tab_change_detection():
    st.subheader("模板一：土地变化检测")
    p1 = st.text_input("时期1栅格路径", str(DEMO_DIR / "land_2020.tif"))
    p2 = st.text_input("时期2栅格路径", str(DEMO_DIR / "land_2024.tif"))
    threshold = st.slider("变化阈值", 0.01, 0.5, 0.12, 0.01)
    if st.button("运行变化检测"):
        with rasterio.open(p1) as r1, rasterio.open(p2) as r2:
            a1 = r1.read(1).astype(float)
            a2 = r2.read(1).astype(float)
            result = detect_change(a1, a2, threshold)
            st.pyplot(plot_two_maps(a1, a2, ("时期1", "时期2")))
            st.pyplot(plot_raster(result["difference"], "变化强度", cmap="coolwarm"))
            c1, c2 = st.columns(2)
            c1.metric("变化像元", result["changed_pixels"])
            c2.metric("变化占比", f"{result['changed_ratio']:.2%}")
            out = OUTPUT_DIR / "change_mask.tif"
            export_geotiff(result["mask"].astype("uint8"), r1.profile, out)
            st.success(f"变化掩膜已导出：{out}")


def tab_coupling():
    st.subheader("模板二：生态与旅游耦合分析")
    df = load_demo_table("eco_tourism.csv")
    st.dataframe(df.head())
    numeric = [c for c in df.columns if c not in ["region", "geometry"] and np.issubdtype(df[c].dtype, np.number)]
    eco_fields = st.multiselect("生态指标", numeric, default=numeric[:2])
    tou_fields = st.multiselect("旅游指标", numeric, default=numeric[2:4])
    if st.button("计算耦合协调") and eco_fields and tou_fields:
        eco = weighted_index(df, eco_fields, [1] * len(eco_fields), [False] * len(eco_fields))
        tou = weighted_index(df, tou_fields, [1] * len(tou_fields), [False] * len(tou_fields))
        c, d, lv = coupling_degree(eco, tou)
        out = df.copy()
        out["eco_index"], out["tour_index"], out["coupling"], out["coordination"], out["level"] = eco, tou, c, d, lv.astype(str)
        st.dataframe(out[["region", "eco_index", "tour_index", "coordination", "level"]])
        st.pyplot(plot_bar(out["region"], out["coordination"], "耦合协调度"))


def tab_suitability():
    st.subheader("模板三：适宜性评价")
    df = load_demo_table("suitability_samples.csv")
    cols = [c for c in df.columns if c not in ["id", "x", "y"]]
    picks = st.multiselect("指标选择", cols, default=cols[:3])
    if picks:
        inv = [st.checkbox(f"{c} 为负向指标", value=False, key=f"inv_{c}") for c in picks]
        ws = [st.number_input(f"{c} 权重", min_value=0.0, max_value=1.0, value=1 / len(picks), key=f"w_{c}") for c in picks]
        if st.button("运行适宜性评价"):
            score, level = weighted_suitability(df, picks, ws, inv)
            out = df.copy()
            out["score"], out["level"] = score, level.astype(str)
            st.dataframe(out.head())
            st.pyplot(plot_bar(out["level"].value_counts().index, out["level"].value_counts().values, "适宜性等级分布"))


def tab_drivers():
    st.subheader("模板四：驱动因子分析")
    df = load_demo_table("driver_samples.csv")
    target = st.selectbox("目标字段", df.columns, index=len(df.columns) - 1)
    feats = st.multiselect("特征字段", [c for c in df.columns if c != target], default=[c for c in df.columns if c != target][:4])
    mode = st.radio("模型类型", ["classification", "regression"], horizontal=True)
    if st.button("运行随机森林") and feats:
        metric, imp = run_driver_model(df, target, feats, mode)
        st.json(metric)
        st.dataframe(imp)
        st.pyplot(plot_bar(imp["feature"], imp["importance"], "特征重要性"))


def tab_scenario():
    st.subheader("模板五：情景模拟（简化 CA）")
    scenario_name = st.selectbox("预设情景", list(DEFAULT_SCENARIOS.keys()))
    params = DEFAULT_SCENARIOS[scenario_name].copy()
    for k in list(params.keys()):
        params[k] = st.slider(k, 0.0, 1.0, float(params[k]), 0.01)
    steps = st.slider("迭代步数", 3, 40, 12)
    if st.button("运行情景模拟"):
        rng = np.random.default_rng(42)
        initial = (rng.random((120, 120)) > 0.82).astype(float)
        suitability = np.clip(rng.normal(0.5, 0.2, (120, 120)), 0, 1)
        constraint = (rng.random((120, 120)) > 0.9).astype(float)
        after = simulate_ca(initial, suitability, constraint, steps, params)
        st.pyplot(plot_two_maps(initial, after, ("模拟前", "模拟后")))
        st.metric("新增建设面积（像元）", int((after > initial).sum()))


def tab_overlay_tool():
    st.subheader("扩展工具：空间叠加与缓冲分析")
    boundary_path = DEMO_DIR / "boundary.geojson"
    poi_path = DEMO_DIR / "poi.geojson"
    if boundary_path.exists() and poi_path.exists():
        boundary = gpd.read_file(boundary_path)
        poi = gpd.read_file(poi_path)
        dist = st.number_input("缓冲距离（投影单位）", value=1000.0)
        if st.button("执行缓冲叠加"):
            buf, inter = buffer_and_intersect(boundary.to_crs(3857), poi.to_crs(3857), dist)
            st.write(inter.head())
            if len(inter):
                st.metric("缓冲区内目标数量", len(inter))
                csv_path = export_csv(inter.drop(columns="geometry"), OUTPUT_DIR / "overlay_result.csv")
                st.success(f"结果已导出：{csv_path}")


def tab_export_reports():
    st.subheader("结果导出与摘要")
    name = st.text_input("分析名称", "阶段汇报示例")
    md = build_markdown_report(
        title=name,
        inputs="- 示例数据与本地导入数据混合",
        method="- 指标标准化 + 权重叠加 + 随机场景模拟",
        params="- 默认参数并按研究区微调",
        results="- 生成变化图、耦合结果、适宜性等级与驱动因子重要性",
        conclusion="系统可稳定支撑课程项目展示，并可继续接入更复杂模型。",
    )
    st.code(md, language="markdown")
    if st.button("保存 Markdown 摘要"):
        out = save_markdown(md, OUTPUT_DIR / "summary.md")
        st.success(f"已保存：{out}")


app_home()
with st.sidebar:
    st.markdown("### 快速入口")
    st.caption("建议先生成示例数据，再进入各模板。")

sections = st.tabs([
    "数据中心",
    "变化检测",
    "耦合分析",
    "适宜性",
    "驱动因子",
    "情景模拟",
    "叠加缓冲",
    "结果导出",
])

with sections[0]:
    tab_data_center()
with sections[1]:
    tab_change_detection()
with sections[2]:
    tab_coupling()
with sections[3]:
    tab_suitability()
with sections[4]:
    tab_drivers()
with sections[5]:
    tab_scenario()
with sections[6]:
    tab_overlay_tool()
with sections[7]:
    tab_export_reports()
