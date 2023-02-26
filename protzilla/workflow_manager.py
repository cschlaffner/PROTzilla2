from pathlib import Path


class WorkflowManager:
    def __init__(self):
        self.available_workflows = []
        workflows_path = Path("user_data/workflows")
        for p in workflows_path.iterdir():
            self.available_workflows.append(p.stem)
        # TODO check for new workflows
