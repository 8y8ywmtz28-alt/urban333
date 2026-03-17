# 空间数据分析与情景模拟工作台（本地版）

这是一个基于 **Python 3.11 + Streamlit** 的本地空间分析平台，面向课程项目、大创项目、阶段汇报和答辩展示。项目强调“能真正干活”，支持本地数据导入、公开网络数据获取、通用分析模板、情景模拟和多格式导出。

## 适用场景
- 城市规划、地理信息、生态环境、旅游管理等课程实践。
- 学生选址分析、空间格局分析、驱动因子筛选。
- 教师验收、课题阶段汇报、答辩演示。

## 核心能力
- **数据中心**：本地导入（GeoTIFF、GeoJSON、SHP-ZIP、CSV、Excel）与在线拉取（URL 下载、地名地理编码、OSM 抓取）。
- **分析模板**：
  1. 土地变化检测（NDVI 差分 + 普通差分）
  2. 生态与旅游耦合分析
  3. 适宜性评价（多指标加权）
  4. 驱动因子分析（随机森林）
  5. 情景模拟（简化 CA，含邻域/适宜性/约束/多情景）
  6. 空间叠加与缓冲分析
- **导出**：PNG、CSV、GeoTIFF、GeoJSON、Markdown 摘要。
- **可视化优化**：统一中文字体初始化，负号显示修复，图件布局更稳定。

## 项目结构
```text
main.py
generate_demo_data.py
requirements.txt
spatialworkbench/
  analysis/
  data/
  exporting/
  reporting/
  ui/
  visualization/
```

## 安装与运行（Windows PowerShell）
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python generate_demo_data.py
streamlit run main.py
```

## 本地文件导入说明
在“数据中心 > 本地导入”上传文件即可。若遇到 CSV 编码问题，系统会优先尝试 UTF-8，再降级到 GBK。

## 在线数据说明
- URL 下载：输入公开数据链接，自动下载到 `exports/`。
- 地名查询：调用 Nominatim 获取坐标与边界候选。
- OSM 抓取：输入 bbox 与要素类型（道路、POI、水系）获取矢量结果。

> 若在线接口暂时不可用，页面会提示失败原因，并可继续使用本地数据。

## 模板使用建议
- 快速演示：先运行 `generate_demo_data.py`，然后按模板逐个加载 `data/demo/` 下样例。
- 自定义数据：建议先在数据中心完成质量检查，再进入模板分析。

## 导出说明
每个模板都可以导出核心结果；推荐同时导出 Markdown 摘要，便于直接改写为汇报材料。

## 常见问题
1. **中文乱码/方块字**：请安装 `Microsoft YaHei` 或 `SimHei`，并重启应用。
2. **GeoPandas 读取失败**：检查是否缺失 `.shx/.dbf/.prj` 等 Shapefile 伴随文件。
3. **OSM 超时**：减小 bbox 范围，或稍后重试。

## 如何替换成自己的数据
1. 在数据中心上传你的栅格、矢量或表格。
2. 在模板中指定字段和参数。
3. 校验结果后导出 PNG/CSV/GeoJSON/GeoTIFF/Markdown。
