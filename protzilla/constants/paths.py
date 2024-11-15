from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent
USER_DATA_PATH = Path(PROJECT_PATH, "user_data")
RUNS_PATH = USER_DATA_PATH / "runs"
WORKFLOWS_PATH = USER_DATA_PATH / "workflows"
EXTERNAL_DATA_PATH = Path(PROJECT_PATH, "user_data/external_data")
WORKFLOW_META_PATH = Path(PROJECT_PATH, "protzilla/constants/workflow_meta.json")
UI_PATH = Path(PROJECT_PATH, "ui")
UPLOAD_PATH = UI_PATH / "uploads"
TEST_DATA_PATH = Path(PROJECT_PATH, "tests/test_data")
