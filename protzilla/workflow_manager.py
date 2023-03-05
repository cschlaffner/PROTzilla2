from .constants.constants import PATH_TO_WORKFLOWS


class WorkflowManager:
    def __init__(self):
        self.available_workflows = []
        self.workflows_path = PATH_TO_WORKFLOWS
        for p in self.workflows_path.iterdir():
            self.available_workflows.append(p.stem)
        # TODO check for new workflows
        # use classmethod
