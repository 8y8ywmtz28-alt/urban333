from pathlib import Path

APP_TITLE = "空间数据分析与情景模拟工作台（本地版）"
APP_TAGLINE = "面向课程项目与汇报展示的本地 GIS 分析平台"

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DEMO_DIR = DATA_DIR / "demo"
OUTPUT_DIR = DATA_DIR / "output"
DOWNLOAD_DIR = DATA_DIR / "downloads"

SUPPORTED_LOCAL_TYPES = ["tif", "tiff", "geojson", "zip", "shp", "csv", "xlsx", "xls"]
NETWORK_TIMEOUT = 18

DEFAULT_SCENARIOS = {
    "生态保护优先": {"neighbor_weight": 0.35, "suitability_weight": 0.45, "constraint_penalty": 0.9, "growth_rate": 0.05},
    "均衡发展": {"neighbor_weight": 0.4, "suitability_weight": 0.4, "constraint_penalty": 0.7, "growth_rate": 0.08},
    "开发优先": {"neighbor_weight": 0.45, "suitability_weight": 0.3, "constraint_penalty": 0.45, "growth_rate": 0.12},
}
