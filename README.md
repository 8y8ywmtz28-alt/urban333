# GeoAtelier：空间数据分析与情景模拟工作台（本地版）

GeoAtelier 是一个面向教学项目、课程设计、大创阶段汇报与答辩展示的本地 GIS 工作台。它不是单一演示脚本，而是围绕“数据导入—分析模板—情景模拟—成果导出”构建的完整应用。

## 适用场景
- 本科/研究生课程项目（空间分析、旅游地理、生态规划等）
- 大创或科研助理阶段成果演示
- 老师验收与答辩 PPT 截图素材生成
- 后续扩展开发的基础框架

## 核心能力
- 数据中心：本地文件导入（GeoTIFF/GeoJSON/Shapefile ZIP/CSV/Excel）+ 在线数据获取（URL 下载、Nominatim 地理编码、OSM 数据抓取）
- 分析模板：
  1. 土地变化检测（栅格差分、变化掩膜、面积占比）
  2. 生态—旅游耦合分析（标准化、耦合协调度、等级）
  3. 适宜性评价（正负向指标、权重叠加、等级分区）
  4. 驱动因子分析（随机森林分类/回归、特征重要性）
  5. 情景模拟（简化元胞自动机，支持多情景参数）
- 扩展工具：空间叠加与缓冲分析
- 导出能力：CSV、GeoTIFF、GeoJSON、Markdown 摘要

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
