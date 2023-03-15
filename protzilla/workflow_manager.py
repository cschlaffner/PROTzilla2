from .constants.paths import WORKFLOWS_PATH


class WorkflowManager:
    def __init__(self):
        self.available_workflows = []
        self.workflows_path = WORKFLOWS_PATH
        for p in self.workflows_path.iterdir():
            self.available_workflows.append(p.stem)
        # TODO check for new workflows
