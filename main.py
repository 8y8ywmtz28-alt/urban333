from __future__ import annotations

from pathlib import Path

import numpy as np
import streamlit as st

from spatialworkbench.analysis.drivers import run_random_forest
from spatialworkbench.analysis.eco_tourism import composite_index, coupling_coordination
from spatialworkbench.analysis.land_change import compute_ndvi, detect_change, infer_red_nir_band_indexes
from spatialworkbench.analysis.overlay import buffer_and_overlay
from spatialworkbench.analysis.scenario import SCENARIOS, simulate_landscape
from spatialworkbench.analysis.suitability import weighted_suitability
from spatialworkbench.config import DEMO_DIR, EXPORT_DIR
from spatialworkbench.core.messages import show_exception, show_hint, show_success
from spatialworkbench.core.state import DataAsset, init_state, list_assets, register_asset, register_result
from spatialworkbench.data.catalog import infer_usable_templates, summarize_raster, summarize_table, summarize_vector
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
init_state()

font, _, font_msg = init_chinese_font()
if font:
    st.sidebar.success(font_msg)
else:
    st.sidebar.warning(font_msg)

st.sidebar.markdown("### 模块导航")
module = st.sidebar.radio(
    "选择模块",
    ["工作台首页", "数据中心", "土地变化检测", "生态-旅游耦合", "适宜性评价", "驱动因子分析", "情景模拟", "空间叠加与缓冲"],
)
st.sidebar.caption("缓存策略：地理编码与示例边界启用缓存。")

with st.sidebar.expander("已载入数据", expanded=True):
    assets = list_assets()
    if not assets:
        st.caption("暂无")
    else:
        for a in assets:
            st.markdown(f"- **{a.name}** · {a.kind}")


if module == "工作台首页":
    render_home()

elif module == "数据中心":
    st.header("数据中心")
    t1, t2, t3 = st.tabs(["本地导入", "在线数据", "示例模式"])

    with t1:
        uploaded = st.file_uploader("上传文件（GeoTIFF/GeoJSON/SHP-ZIP/CSV/Excel）", type=["tif", "tiff", "geojson", "json", "zip", "csv", "xlsx", "xls"])
        if uploaded:
            tmp = save_upload_to_temp(uploaded)
            ext = tmp.suffix.lower()
            try:
                if ext in [".tif", ".tiff"]:
                    summary = summarize_raster(tmp)
                    register_asset(DataAsset(uploaded.name, "raster", "local", str(tmp), summary, infer_usable_templates("raster")))
                elif ext in [".geojson", ".json", ".shp", ".zip"]:
                    gdf = read_vector(tmp)
                    summary = summarize_vector(gdf)
                    register_asset(DataAsset(uploaded.name, "vector", "local", gdf, summary, infer_usable_templates("vector")))
                else:
                    df = read_table(tmp)
                    summary = summarize_table(df)
                    register_asset(DataAsset(uploaded.name, "table", "local", df, summary, infer_usable_templates("table")))
                show_success("数据导入成功，已加入工作台数据清单。")
            except Exception as exc:
                show_exception("读取失败", exc)

        assets = list_assets()
        if assets:
            st.subheader("已载入数据清单")
            st.dataframe(
                [{"名称": a.name, "类型": a.kind, "来源": a.source, "可用模板": "、".join(a.usable_in), "摘要": a.summary} for a in assets],
                use_container_width=True,
            )

    with t2:
        url = st.text_input("URL 下载（GeoTIFF/GeoJSON/CSV/ZIP）")
        if st.button("下载并登记") and url:
            out = EXPORT_DIR / Path(url).name
            ok, msg = download_file(url, out)
            st.info(msg)
            if ok:
                show_hint(f"文件已保存到 {out}，可在本地导入页继续加载。")

        place = st.text_input("地名查询")
        if st.button("地理编码") and place:
            result = geocode_place(place)
            if result:
                st.dataframe(result[:5], use_container_width=True)
            else:
                st.warning("未查到结果，可能是网络波动或地名不明确。")

        bbox_text = st.text_input("OSM 抓取范围 south,west,north,east", value="39.8,116.2,40.0,116.5")
        feature_type = st.selectbox("OSM 要素", ["highway", "amenity", "waterway"])
        if st.button("抓取 OSM"):
            try:
                bbox = tuple(map(float, bbox_text.split(",")))
                gdf = fetch_osm_features(bbox, feature_type)
                if len(gdf) == 0:
                    st.warning("未获取到数据，请缩小范围或稍后重试。")
                else:
                    register_asset(DataAsset(f"osm_{feature_type}", "vector", "online", gdf, summarize_vector(gdf), ["空间叠加与缓冲"]))
                    show_success(f"抓取成功：{len(gdf)} 条")
            except Exception as exc:
                show_exception("OSM 抓取失败", exc)

    with t3:
        if st.button("加载世界边界示例"):
            gdf = load_world_boundaries()
            register_asset(DataAsset("world_boundaries", "vector", "demo", gdf, summarize_vector(gdf), ["空间叠加与缓冲", "生态-旅游耦合"]))
            show_success("示例边界已加载")
        show_hint("演示模式建议先运行 generate_demo_data.py，再在各模板使用 data/demo 数据。")

elif module == "土地变化检测":
    st.header("土地变化检测")
    p1 = st.text_input("一期栅格", str(DEMO_DIR / "raster_t1.tif"))
    p2 = st.text_input("二期栅格", str(DEMO_DIR / "raster_t2.tif"))
    mode = st.radio("变化模式", ["自动 NDVI 差分", "普通栅格差分"])
    threshold = st.slider("变化阈值", 0.01, 0.9, 0.15, 0.01)

    if st.button("运行变化检测"):
        import rasterio

        with st.spinner("计算中..."):
            with rasterio.open(p1) as r1, rasterio.open(p2) as r2:
                if mode == "自动 NDVI 差分":
                    idx = infer_red_nir_band_indexes(r1.count)
                    if not idx:
                        st.warning("未识别到红光/NIR，请手动选择普通差分。")
                        a1, a2 = r1.read(1).astype(float), r2.read(1).astype(float)
                    else:
                        a1 = compute_ndvi(r1.read(idx[0]).astype(float), r1.read(idx[1]).astype(float))
                        a2 = compute_ndvi(r2.read(idx[0]).astype(float), r2.read(idx[1]).astype(float))
                else:
                    a1, a2 = r1.read(1).astype(float), r2.read(1).astype(float)
                result = detect_change(a1, a2, threshold)
        register_result("land_change", result)

        c1, c2 = st.columns(2)
        f1 = plot_raster(result["diff"], "变化强度")
        f2 = plot_raster(result["mask"], "变化掩膜", "Reds")
        c1.pyplot(f1)
        c2.pyplot(f2)
        st.metric("变化像元占比", f"{result['changed_ratio']:.2%}")
        st.info(f"关键结论：变化主要集中在高差值区域，阈值 {threshold:.2f} 下识别出 {result['changed_pixels']} 个变化像元。")

        if st.button("导出本模板结果"):
            export_geotiff(result["mask"].astype("uint8"), EXPORT_DIR / "land_change_mask.tif")
            export_png(f1, EXPORT_DIR / "land_change_diff.png")
            export_csv(
                __import__("pandas").DataFrame([{"changed_pixels": result["changed_pixels"], "changed_ratio": result["changed_ratio"]}]),
                EXPORT_DIR / "land_change_stats.csv",
            )
            (EXPORT_DIR / "land_change_report.md").write_text(
                build_markdown_report("土地变化检测", f"{p1}, {p2}", mode, {"threshold": threshold}, "输出掩膜/统计/图件", "变化区可作为后续管控与核查范围。"),
                encoding="utf-8",
            )
            show_success("已导出 GeoTIFF、PNG、CSV、Markdown")

elif module == "生态-旅游耦合":
    st.header("生态与旅游耦合")
    path = st.text_input("指标表路径", str(DEMO_DIR / "eco_tourism.csv"))
    if st.button("加载并计算"):
        df = read_table(path)
        cols = [c for c in df.columns if c not in ["region", "id", "geometry"]]
        eco_cols, tour_cols = cols[:2], cols[2:4] if len(cols) >= 4 else cols[:1]
        eco = composite_index(df, {c: True for c in eco_cols})
        tour = composite_index(df, {c: True for c in tour_cols})
        c, d, level = coupling_coordination(eco, tour)
        df = df.copy()
        df["eco_idx"], df["tour_idx"], df["coupling"], df["coordination"], df["level"] = eco, tour, c, d, level
        register_result("eco_tourism", df)
        st.dataframe(df, use_container_width=True)
        fig = plot_series_distribution(df["level"], "协调等级分布")
        st.pyplot(fig)
        st.info(f"结果解读：平均协调度 {df['coordination'].mean():.3f}，主导等级为“{df['level'].mode().iloc[0]}”。")
        if st.button("导出耦合结果"):
            export_csv(df, EXPORT_DIR / "eco_tourism_result.csv")
            export_png(fig, EXPORT_DIR / "eco_tourism_level.png")
            (EXPORT_DIR / "eco_tourism_report.md").write_text(build_markdown_report("生态-旅游耦合", path, "归一化+耦合协调", {}, "导出结果表与分布图", "可用于区域协同发展对比。"), encoding="utf-8")
            show_success("导出完成")

elif module == "适宜性评价":
    st.header("适宜性评价")
    path = st.text_input("输入表路径", str(DEMO_DIR / "suitability.csv"))
    df = None
    try:
        df = read_table(path)
    except Exception:
        pass
    if df is not None:
        cols = [c for c in df.columns if c not in ["region", "id", "geometry"]]
        selected = st.multiselect("指标字段", cols, default=cols[: min(4, len(cols))])
        show_hint("正向：越大越好；负向：越小越好。")
        if selected:
            directions = {c: st.selectbox(f"{c}方向", ["正向", "负向"], key=f"d_{c}") == "正向" for c in selected}
            weights = {c: st.slider(f"{c}权重", 0.0, 1.0, 1 / len(selected), 0.05) for c in selected}
            if st.button("运行适宜性分析"):
                score, level = weighted_suitability(df, directions, weights)
                out = df.copy()
                out["suit_score"], out["suit_level"] = score, level
                register_result("suitability", out)
                st.dataframe(out, use_container_width=True)
                st.pyplot(plot_series_distribution(out["suit_level"], "等级统计"))

elif module == "驱动因子分析":
    st.header("驱动因子分析")
    path = st.text_input("样本表", str(DEMO_DIR / "drivers.csv"))
    df = None
    try:
        df = read_table(path)
    except Exception:
        pass
    if df is not None:
        target = st.selectbox("目标字段", df.columns)
        task = st.radio("任务类型", ["regression", "classification"])
        if st.button("执行建模"):
            if len(df) < 30:
                st.warning("样本量偏小，模型稳定性可能不足。")
            clean = df.dropna()
            if len(clean) != len(df):
                st.info(f"已自动移除缺失值样本 {len(df)-len(clean)} 行")
            _, metrics, imp = run_random_forest(clean, target, task)
            st.json(metrics)
            fig = plot_importance(imp)
            st.pyplot(fig)
            st.info(f"结论：主要驱动因子为 {', '.join(imp.index[:3])}。")

elif module == "情景模拟":
    st.header("情景模拟")
    base_path = st.text_input("基础状态图", str(DEMO_DIR / "base_binary.npy"))
    suit_path = st.text_input("适宜性图", str(DEMO_DIR / "suitability.npy"))
    cons_path = st.text_input("约束区", str(DEMO_DIR / "constraint.npy"))
    sname = st.selectbox("情景", list(SCENARIOS))
    steps = st.slider("迭代步数", 1, 30, 10)
    params = SCENARIOS[sname].copy()
    for k in params:
        params[k] = st.slider(k, 0.0, 1.0, float(params[k]), 0.05)
    if st.button("运行模拟"):
        base, suit, cons = np.load(base_path), np.load(suit_path), np.load(cons_path)
        after, change = simulate_landscape(base, suit, cons, params, steps)
        c1, c2 = st.columns(2)
        c1.pyplot(plot_raster(base, "模拟前", "Greens"))
        c2.pyplot(plot_raster(after, "模拟后", "Greens"))
        st.pyplot(plot_raster(change, "变化方向", "RdBu"))
        inc = int((change > 0).sum())
        st.metric("新增面积像元", inc)
        st.info(f"摘要：在“{sname}”情景下，新增开发像元 {inc}，约束区抑制强度 {params['constraint']:.2f}。")

elif module == "空间叠加与缓冲":
    st.header("空间叠加与缓冲")
    p1 = st.text_input("主体图层", str(DEMO_DIR / "poi.geojson"))
    p2 = st.text_input("目标图层", str(DEMO_DIR / "boundary.geojson"))
    dist = st.number_input("缓冲距离", value=0.1, min_value=0.01)
    if st.button("执行"):
        a, b = read_vector(p1), read_vector(p2)
        if a.crs != b.crs:
            b = b.to_crs(a.crs)
        buffered, inter = buffer_and_overlay(a, dist, b)
        st.dataframe(inter.head(), use_container_width=True)
        st.metric("叠加结果数", len(inter))
        if st.button("导出叠加结果"):
            export_geojson(inter, EXPORT_DIR / "overlay_result.geojson")
            export_geojson(buffered, EXPORT_DIR / "buffer_result.geojson")
            show_success("已导出 GeoJSON")
