from protzilla.constants import paths


def get_available_workflow_names() -> list[str]:
    if not paths.WORKFLOWS_PATH.exists():
        return []
    return [
        file.stem
        for file in paths.WORKFLOWS_PATH.iterdir()
        if not file.name.startswith(".") and not file.suffix == ".json"
    ]
