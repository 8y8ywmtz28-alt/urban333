from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import streamlit as st

from spatialworkbench.analysis.drivers import run_random_forest
from spatialworkbench.analysis.eco_tourism import composite_index, coupling_coordination
from spatialworkbench.analysis.land_change import compute_ndvi, detect_change, infer_red_nir_band_indexes
from spatialworkbench.analysis.overlay import buffer_and_overlay
from spatialworkbench.analysis.scenario import SCENARIOS, simulate_landscape
from spatialworkbench.analysis.suitability import weighted_suitability
from spatialworkbench.config import DEMO_DIR, EXPORT_DIR
from spatialworkbench.data.io import read_table, read_vector, save_upload_to_temp
from spatialworkbench.data.online import download_file, fetch_osm_features, geocode_place, load_world_boundaries
from spatialworkbench.exporting.exporters import export_csv, export_geojson, export_geotiff, export_png
from spatialworkbench.font_manager import init_chinese_font
from spatialworkbench.reporting.markdown_report import build_markdown_report
from spatialworkbench.ui.home import render_home
from spatialworkbench.ui.styles import BASE_STYLE
from spatialworkbench.visualization.plotting import plot_importance, plot_raster, plot_series_distribution

st.set_page_config(page_title="空间工作台", layout="wide")
st.markdown(BASE_STYLE, unsafe_allow_html=True)
font, all_cn = init_chinese_font()
if font:
    st.sidebar.success(f"已启用中文字体: {font}")
else:
    st.sidebar.warning("未检测到常用中文字体，将使用降级字体显示。")

st.sidebar.title("导航")
module = st.sidebar.radio(
    "选择模块",
    ["工作台首页", "数据中心", "土地变化检测", "生态-旅游耦合", "适宜性评价", "驱动因子分析", "情景模拟", "空间叠加与缓冲"],
)

state = st.session_state
state.setdefault("loaded", {})

if module == "工作台首页":
    render_home()

elif module == "数据中心":
    st.header("数据中心")
    t1, t2, t3 = st.tabs(["本地导入", "在线数据", "示例数据"])

    with t1:
        uploaded = st.file_uploader("上传文件（GeoTIFF/GeoJSON/SHP-ZIP/CSV/Excel）", type=["tif", "tiff", "geojson", "json", "zip", "csv", "xlsx", "xls"])
        if uploaded:
            tmp = save_upload_to_temp(uploaded)
            ext = tmp.suffix.lower()
            try:
                if ext in [".tif", ".tiff"]:
                    state["loaded"]["raster"] = str(tmp)
                    st.success("栅格已加载")
                elif ext in [".geojson", ".json", ".shp", ".zip"]:
                    gdf = read_vector(tmp)
                    state["loaded"]["vector"] = gdf
                    st.success(f"矢量已加载，共 {len(gdf)} 条")
                    st.dataframe(gdf.head())
                else:
                    df = read_table(tmp)
                    state["loaded"]["table"] = df
                    st.success(f"表格已加载，共 {len(df)} 行")
                    st.dataframe(df.head())
            except Exception as e:
                st.error(f"读取失败：{e}")

    with t2:
        url = st.text_input("输入数据 URL（GeoTIFF/GeoJSON/CSV/ZIP）")
        if st.button("下载到本地") and url:
            out = EXPORT_DIR / Path(url).name
            ok, msg = download_file(url, out)
            st.info(msg)
            if ok:
                st.code(str(out))

        place = st.text_input("输入地名进行地理编码")
        if st.button("查询地名") and place:
            result = geocode_place(place)
            if result:
                st.json(result[:2])
            else:
                st.warning("地理编码失败，请检查网络或换地名。")

        bbox_text = st.text_input("OSM 抓取范围 south,west,north,east", value="39.8,116.2,40.0,116.5")
        feature_type = st.selectbox("OSM 要素", ["highway", "amenity", "waterway"])
        if st.button("抓取 OSM"):
            try:
                bbox = tuple(map(float, bbox_text.split(",")))
                gdf = fetch_osm_features(bbox, feature_type)
                if len(gdf) == 0:
                    st.warning("未获取到要素，建议缩小范围或稍后重试。")
                else:
                    state["loaded"]["vector"] = gdf
                    st.success(f"抓取成功，共 {len(gdf)} 条")
                    st.dataframe(gdf.head())
            except Exception as e:
                st.error(f"抓取失败：{e}")

    with t3:
        if st.button("加载世界边界示例"):
            gdf = load_world_boundaries()
            state["loaded"]["vector"] = gdf
            st.success("示例边界已加载")
            st.dataframe(gdf.head())
        st.info(f"推荐先运行 generate_demo_data.py，示例目录：{DEMO_DIR}")

elif module == "土地变化检测":
    st.header("土地变化检测")
    p1 = st.text_input("一期栅格路径", str(DEMO_DIR / "raster_t1.tif"))
    p2 = st.text_input("二期栅格路径", str(DEMO_DIR / "raster_t2.tif"))
    threshold = st.slider("变化阈值", 0.01, 0.8, 0.15, 0.01)
    mode = st.radio("模式", ["自动 NDVI 差分", "普通栅格差分"])

    if st.button("执行变化检测"):
        import rasterio
        with rasterio.open(p1) as r1, rasterio.open(p2) as r2:
            if mode == "自动 NDVI 差分":
                idx = infer_red_nir_band_indexes(r1.count)
                if not idx:
                    st.warning("无法识别红光/近红外，已切换为普通差分。")
                    a1, a2 = r1.read(1), r2.read(1)
                else:
                    a1 = compute_ndvi(r1.read(idx[0]).astype(float), r1.read(idx[1]).astype(float))
                    a2 = compute_ndvi(r2.read(idx[0]).astype(float), r2.read(idx[1]).astype(float))
            else:
                a1, a2 = r1.read(1).astype(float), r2.read(1).astype(float)
            res = detect_change(a1, a2, threshold)

        c1, c2 = st.columns(2)
        c1.pyplot(plot_raster(res["diff"], "差分图", "RdBu"))
        c2.pyplot(plot_raster(res["mask"], "变化掩膜", "Reds"))
        st.metric("变化像元占比", f"{res['changed_ratio']:.2%}")

        if st.button("导出变化结果"):
            export_geotiff(res["mask"].astype("uint8"), EXPORT_DIR / "change_mask.tif")
            st.success(f"已导出: {EXPORT_DIR / 'change_mask.tif'}")

elif module == "生态-旅游耦合":
    st.header("生态与旅游耦合分析")
    table_path = st.text_input("指标表路径（CSV/Excel）", str(DEMO_DIR / "eco_tourism.csv"))
    if st.button("加载指标表"):
        df = read_table(table_path)
        state["eco"] = df
    df = state.get("eco")
    if df is not None:
        st.dataframe(df.head())
        cols = [c for c in df.columns if c not in ["region", "geometry", "id"]]
        eco_cols = st.multiselect("生态指标", cols, default=cols[:2])
        tour_cols = st.multiselect("旅游指标", cols, default=cols[2:4])
        if eco_cols and tour_cols and st.button("计算耦合协调"):
            eco = composite_index(df, {c: True for c in eco_cols})
            tour = composite_index(df, {c: True for c in tour_cols})
            c, d, level = coupling_coordination(eco, tour)
            out = df.copy()
            out["eco_idx"], out["tour_idx"], out["coupling"], out["coordination"], out["level"] = eco, tour, c, d, level
            state["eco_result"] = out
            st.dataframe(out[["region", "eco_idx", "tour_idx", "coordination", "level"]].head())
            st.pyplot(plot_series_distribution(out["level"], "耦合协调等级分布"))
            st.success(f"自动结论：平均协调度为 {out['coordination'].mean():.3f}，整体处于“{out['level'].mode()[0]}”。")

        if "eco_result" in state and st.button("导出耦合结果"):
            out = state["eco_result"]
            export_csv(out, EXPORT_DIR / "eco_tourism_result.csv")
            md = build_markdown_report("生态旅游耦合", "生态+旅游指标表", "归一化 + 加权 + 耦合协调模型", {}, "已导出 CSV", "可用于阶段汇报。")
            (EXPORT_DIR / "eco_tourism_report.md").write_text(md, encoding="utf-8")
            st.success("已导出 CSV 与 Markdown")

elif module == "适宜性评价":
    st.header("适宜性评价")
    path = st.text_input("样本表路径", str(DEMO_DIR / "suitability.csv"))
    if st.button("加载适宜性数据"):
        state["suit"] = read_table(path)
    df = state.get("suit")
    if df is not None:
        st.dataframe(df.head())
        cols = [c for c in df.columns if c not in ["region", "id", "geometry"]]
        selected = st.multiselect("选择指标", cols, default=cols[: min(4, len(cols))])
        if selected:
            weights = {}
            directions = {}
            for c in selected:
                weights[c] = st.slider(f"{c} 权重", 0.0, 1.0, 1 / len(selected), 0.05)
                directions[c] = st.selectbox(f"{c} 指标方向", ["正向", "负向"], key=f"dir_{c}") == "正向"
            if st.button("运行适宜性评价"):
                score, level = weighted_suitability(df, directions, weights)
                out = df.copy()
                out["suitability_score"] = score
                out["suitability_level"] = level
                state["suit_result"] = out
                st.dataframe(out[["region", "suitability_score", "suitability_level"]].head())
                st.pyplot(plot_series_distribution(out["suitability_level"], "适宜性等级统计"))

elif module == "驱动因子分析":
    st.header("驱动因子分析")
    path = st.text_input("样本路径", str(DEMO_DIR / "drivers.csv"))
    if st.button("加载驱动样本"):
        state["driver"] = read_table(path)
    df = state.get("driver")
    if df is not None:
        st.dataframe(df.head())
        target = st.selectbox("目标字段", df.columns)
        task = st.radio("任务类型", ["regression", "classification"])
        if st.button("训练随机森林"):
            model, metrics, importance = run_random_forest(df, target, task)
            st.json(metrics)
            st.pyplot(plot_importance(importance))

elif module == "情景模拟":
    st.header("情景模拟（简化 CA）")
    base_path = st.text_input("基础土地栅格（0/1）", str(DEMO_DIR / "base_binary.npy"))
    suit_path = st.text_input("适宜性栅格", str(DEMO_DIR / "suitability.npy"))
    cons_path = st.text_input("约束区栅格", str(DEMO_DIR / "constraint.npy"))
    scenario_name = st.selectbox("情景类型", list(SCENARIOS))
    steps = st.slider("迭代步数", 1, 30, 8)
    custom = SCENARIOS[scenario_name].copy()
    custom["neighborhood"] = st.slider("邻域效应", 0.0, 1.0, float(custom["neighborhood"]), 0.05)
    custom["suitability"] = st.slider("适宜性权重", 0.0, 1.0, float(custom["suitability"]), 0.05)
    custom["constraint"] = st.slider("约束强度", 0.0, 1.0, float(custom["constraint"]), 0.05)
    custom["threshold"] = st.slider("开发阈值", 0.1, 0.95, float(custom["threshold"]), 0.01)

    if st.button("运行情景模拟"):
        base = np.load(base_path)
        suit = np.load(suit_path)
        cons = np.load(cons_path)
        after, change = simulate_landscape(base, suit, cons, custom, steps)
        c1, c2 = st.columns(2)
        c1.pyplot(plot_raster(base, "模拟前", "Greens"))
        c2.pyplot(plot_raster(after, "模拟后", "Greens"))
        st.pyplot(plot_raster(change, "变化方向", "RdBu"))
        st.metric("变化面积像元", int((change > 0).sum()))

elif module == "空间叠加与缓冲":
    st.header("空间叠加与缓冲分析")
    p1 = st.text_input("主体矢量", str(DEMO_DIR / "poi.geojson"))
    p2 = st.text_input("目标矢量", str(DEMO_DIR / "boundary.geojson"))
    dist = st.number_input("缓冲距离（投影坐标单位）", value=0.1, min_value=0.01)
    if st.button("执行缓冲叠加"):
        a = read_vector(p1)
        b = read_vector(p2)
        if a.crs != b.crs:
            b = b.to_crs(a.crs)
        buffered, inter = buffer_and_overlay(a, dist, b)
        st.write(f"叠加结果数量：{len(inter)}")
        st.dataframe(inter.head())
        if st.button("导出 GeoJSON"):
            export_geojson(inter, EXPORT_DIR / "buffer_overlay.geojson")
            st.success("导出完成")
