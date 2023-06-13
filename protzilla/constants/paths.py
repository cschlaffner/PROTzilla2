from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent
RUNS_PATH = Path(PROJECT_PATH, "user_data/runs")
WORKFLOWS_PATH = Path(PROJECT_PATH, "user_data/workflows")
WORKFLOW_META_PATH = Path(PROJECT_PATH, "protzilla/constants/workflow_meta.json")
DATABASES_PATH = Path(PROJECT_PATH, "protzilla/data_integration/databases")
UI_PATH = Path(PROJECT_PATH, "ui")
TEST_DATA_PATH = Path(PROJECT_PATH, "tests/test_data")
