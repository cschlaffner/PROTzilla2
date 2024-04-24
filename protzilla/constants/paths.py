from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent
RUNS_PATH = Path(PROJECT_PATH, "user_data/runs")
WORKFLOWS_PATH = Path(PROJECT_PATH, "user_data/workflows")
EXTERNAL_DATA_PATH = Path(PROJECT_PATH, "user_data/external_data")
WORKFLOW_META_PATH = Path(PROJECT_PATH, "protzilla/constants/workflow_meta.json")
UI_PATH = Path(PROJECT_PATH, "ui")
UPLOAD_PATH = UI_PATH / "uploads"
TEST_DATA_PATH = Path(PROJECT_PATH, "tests/test_data")
