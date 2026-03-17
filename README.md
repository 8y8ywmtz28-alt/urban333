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
geoatelier/
  analyses/
  ui/
  config.py
  datahub.py
  preprocessing.py
  visualization.py
  exporters.py
  reports.py
  font_manager.py
data/
  demo/
```

## Windows + PowerShell 运行
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
python .\generate_demo_data.py
streamlit run .\main.py
```

## 本地文件导入说明
1. 进入“数据中心 > 本地文件导入”。
2. 可直接拖入 CSV/Excel/GeoJSON/TIFF 或 ZIP 版 Shapefile。
3. Excel 支持选择工作表；CSV 支持常见编码回退。

## 在线数据获取说明
- URL 直连：输入公开下载链接后直接保存到 `data/downloads/`
- 地理编码：输入地名，调用 Nominatim 获取坐标候选
- OSM 抓取：给定 bbox，抓取道路/POI 等样本
- 网络失败时会显示错误提示，且不阻塞本地分析流程

## 各模板使用建议
- 首次演示建议使用 `generate_demo_data.py` 生成样例。
- 按“变化检测→耦合分析→适宜性→驱动因子→情景模拟”顺序展示全流程。
- 情景模拟建议对比“生态保护优先”和“开发优先”两组参数截图。

## 导出与汇报
“结果导出”页可生成 Markdown 摘要，包含方法、参数、关键结果与结论，方便直接改写为阶段报告。

## 常见问题
- **中文乱码**：系统没有中文字体时会自动提示，建议安装 Microsoft YaHei 或思源黑体。
- **在线接口失败**：可能是网络限制或服务波动，可切换到本地文件继续分析。
- **GeoPandas 依赖安装慢**：建议在网络稳定环境下安装，必要时使用国内镜像。

## 如何替换为自己的数据
1. 栅格模板：替换路径为自己的 GeoTIFF。
2. 指标模板：将字段名映射到业务指标并设置正负向与权重。
3. 驱动因子：指定目标字段与特征字段。
4. 情景模拟：使用自己的初始格局、适宜性和约束栅格（可按模块扩展接入）。

相较于普通课堂脚本，GeoAtelier 提供统一字体与图形风格、容错型数据导入、在线数据入口、完整模板链路与导出闭环，更适合作为真实项目底座持续迭代。
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
