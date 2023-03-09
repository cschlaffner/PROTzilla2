from pathlib import Path

PATH_TO_PROJECT = Path(__file__).resolve().parent.parent.parent
PATH_TO_RUNS = Path(f"{PATH_TO_PROJECT}/user_data/runs")
PATH_TO_WORKFLOWS = Path(f"{PATH_TO_PROJECT}/user_data/workflows")
