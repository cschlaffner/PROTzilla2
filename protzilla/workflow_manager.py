import os
from pathlib import Path

from ui.main.settings import BASE_DIR


class WorkflowManager:
    def __init__(self):
        print("workflow")
        print(os.getcwd())

        self.available_workflows = []
        workflows_path = Path(f"{BASE_DIR}/protzilla/user_data/workflows")
        for p in workflows_path.iterdir():
            self.available_workflows.append(p.stem)
        # TODO check for new workflows
