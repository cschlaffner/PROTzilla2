from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent
RUNS_PATH = Path(f"{PROJECT_PATH}/user_data/runs")
WORKFLOWS_PATH = Path(f"{PROJECT_PATH}/user_data/workflows")
WORKFLOW_META_PATH = Path(f"{PROJECT_PATH}/protzilla/constants/workflow_meta.json")
UI_PATH = Path(f"{PROJECT_PATH}/ui")
TEST_DATA_PATH = Path(f"{PROJECT_PATH}/tests/test_data")
