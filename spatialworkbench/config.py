from pathlib import Path

APP_TITLE = "空间数据分析与情景模拟工作台（本地版）"
APP_SUBTITLE = "面向课程项目、大创和答辩展示的本地空间分析平台"

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DEMO_DIR = DATA_DIR / "demo"
EXPORT_DIR = ROOT_DIR / "exports"
ARTIFACT_DIR = ROOT_DIR / "artifacts"

REQUEST_TIMEOUT = 20
DEFAULT_CRS = "EPSG:4326"
SUPPORTED_VECTOR = [".geojson", ".json", ".shp", ".zip"]
SUPPORTED_TABLE = [".csv", ".xlsx", ".xls"]
SUPPORTED_RASTER = [".tif", ".tiff"]

for d in [DATA_DIR, EXPORT_DIR, ARTIFACT_DIR]:
    d.mkdir(parents=True, exist_ok=True)
