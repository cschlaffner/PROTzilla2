from .run import Run
from .utilities.random import random_string


class Runner:
    def __init__(self, args):
        try:
            run_name = args.name
        except AttributeError:
            run_name = f"runner_{random_string()}"
        try:
            df_mode = args.df_mode
        except AttributeError:
            df_mode = "disk"

        run = Run.create(
            run_name=run_name,
            workflow_config_name=args.workflow,
            df_mode=df_mode,
        )

        print(run.workflow_config)
