from pathlib import Path

PATH_TO_PROJECT = Path(__file__).resolve().parent.parent.parent
PATH_TO_RUNS = Path(f"{PATH_TO_PROJECT}/user_data/runs")
PATH_TO_WORKFLOWS = Path(f"{PATH_TO_PROJECT}/user_data/workflows")

# color schemes
PROTZILLA_DISCRETE_COLOR_SEQUENCE = [
    "#4A536A",
    "#87A8B9",
    "#CE5A5A",
    "#8E3325",
    "#E2A46D",
]
PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE = ["#4A536A", "#CE5A5A"]
