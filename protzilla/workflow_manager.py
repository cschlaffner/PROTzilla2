from pathlib import Path

from .constants.constants import PATH_TO_PROJECT


class WorkflowManager:
    def __init__(self):
        self.available_workflows = []
        workflows_path = Path(f"{PATH_TO_PROJECT}/user_data/workflows")
        for p in workflows_path.iterdir():
            self.available_workflows.append(p.stem)
        # TODO check for new workflows
