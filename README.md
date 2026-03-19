# 空间数据分析与情景模拟工作台（Local Spatial Workbench）

一个面向课程项目、大创、科研预研与小型业务分析的本地 GIS 工作台。项目基于 Python 3.11 + Streamlit

## 1. 项目定位
- 定位：本地部署、轻量可扩展的空间分析应用。
- 目标用户：学生、教师、研究助理、初级分析师。
- 核心原则：数据链路完整（输入→处理→展示→导出）、界面克制、结果可复用。

## 2. 核心能力
1. 数据中心
   - 本地导入：GeoTIFF、GeoJSON、Shapefile/ZIP、CSV、Excel。
   - 在线数据：URL 下载、Nominatim 地理编码、Overpass OSM 抓取。
   - 数据清单：自动识别类型、记录摘要（CRS、范围、波段、字段等）、提示可用模板。
2. **分析模板**
   - 土地变化检测（NDVI / 普通差分）
   - 生态-旅游耦合分析
   - 适宜性评价
   - 驱动因子分析（随机森林）
   - 情景模拟（简化 CA）
   - 空间叠加与缓冲
3. 导出能力
   - PNG、CSV、GeoTIFF、GeoJSON、Markdown 摘要。

## 3. 适用场景
- 课程作业：选址分析、用地变化、生态协同等。
- 大创与预研：快速构建可展示、可迭代的分析流程。
- 教学演示：统一界面下串联数据导入、模型参数、图件输出。

## 4. 项目结构
```text
main.py
generate_demo_data.py
requirements.txt
spatialworkbench/
  core/                # 状态管理与统一提示
  data/                # I/O、在线获取、数据摘要
  analysis/            # 各类分析模板算法
  visualization/       # 统一图表绘制
  exporting/           # 导出接口
  reporting/           # Markdown 报告
  ui/                  # 首页与样式
  font_manager.py      # 中文字体初始化与降级
```

## 5. 安装与启动（Windows PowerShell）
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python generate_demo_data.py
streamlit run main.py
```

## 6. 演示模式与真实数据模式
- 演示模式：执行 `python generate_demo_data.py` 后，使用 `data/demo/` 下样例快速跑通。
- 真实数据模式：在“数据中心 > 本地导入”上传真实数据，模板页面按字段与参数运行。
- 在线拉取模式：在“数据中心 > 在线数据”进行 URL 下载、地名查询、OSM 抓取。

## 7. 各模板使用说明（简版）
### 7.1 土地变化检测
输入两期栅格，选择 NDVI 或普通差分，设置阈值后生成变化掩膜与统计；可导出 GeoTIFF/PNG/CSV/Markdown。

### 7.2 生态-旅游耦合
输入指标表，计算生态指数、旅游指数、耦合度、协调度与等级分布，并导出结果表与图。

### 7.3 适宜性评价
设置正负向指标与权重，输出综合得分与等级分区，适合选址与空间布局题目。

### 7.4 驱动因子分析
选择目标字段（回归/分类），输出模型基础指标与特征重要性排序。

### 7.5 情景模拟
输入基础状态、适宜性图、约束区，选择情景和参数，执行多步迭代并对比模拟前后变化。

### 7.6 空间叠加与缓冲
对点线面图层执行缓冲与叠加，输出交集结果统计和 GeoJSON 导出。

## 8. 导出说明
所有导出写入 `exports/`：
- 图件：PNG
- 表格：CSV
- 栅格：GeoTIFF
- 矢量：GeoJSON
- 文本：Markdown 摘要（可直接用于汇报材料）

## 9. 中文字体与图表说明
项目统一通过 `font_manager.py` 初始化中文字体，优先尝试：
- Microsoft YaHei
- SimHei
- Noto Sans CJK SC
- Source Han Sans SC
- Arial Unicode MS

若系统缺失上述字体，应用会在侧边栏提示并降级到 `DejaVu Sans`。同时已修复 matplotlib 负号显示问题。

## 10. 常见问题
1. 中文仍乱码：安装上述任一中文字体并重启应用。
2. OSM 无结果：缩小 bbox 范围，或稍后重试。
3. Shapefile 读取失败：确认 `.shp/.shx/.dbf/.prj` 文件齐全。
4. 模型报错：检查目标列是否为有效数值/类别，是否存在大量缺失值。

## 11. 如何替换成真实项目
1. 在数据中心建立你的数据清单（栅格/矢量/表格）。
2. 选择对应模板并保存关键参数。
3. 导出结果与 Markdown 摘要，形成阶段汇报版本。
4. 如需深度定制，可在 `analysis/` 新增模板并复用现有导入/导出/报告框架。

## 12. 后续扩展建议
- 接入多期时序栅格批处理。
- 在耦合与适宜性模块增加空间自相关检验。
- 增加任务记录与参数快照，实现可复现实验流程。
