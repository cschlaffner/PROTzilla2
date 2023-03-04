from pathlib import Path
from dataclasses import dataclass
import pandas as pd
from .constants.constants import PATH_TO_RUNS


class History:
    def __init__(self, run_name, df_mode):
        assert df_mode in ("disk", "memory")

        self.df_mode = df_mode
        self.run_name = run_name
        self.steps: list[ExecutedStep] = []

    def add_step(
        self,
        section,
        step,
        method,
        parameters,
        dataframe: pd.DataFrame,
        outputs: dict,
        plots,
    ):
        if self.df_mode == "disk":
            index = len(self.steps)
            (PATH_TO_RUNS / self.run_name).mkdir(parents=True, exist_ok=True)
            dataframe.to_csv(self.df_path(index), index=False)
            path_or_df = self.df_path(index)
        else:
            path_or_df = dataframe
        executed_step = ExecutedStep(
            section, step, method, parameters, path_or_df, outputs, plots
        )
        self.steps.append(executed_step)
        # save steps to disk?

    def df_path(self, index):
        return PATH_TO_RUNS / self.run_name / f"df_{index}.csv"


@dataclass
class ExecutedStep:
    section: str
    step: str
    method: str
    parameters: dict
    _dataframe: pd.DataFrame | Path
    outputs: dict
    plots: list

    @property
    def dataframe(self):
        if isinstance(self._dataframe, Path):
            return pd.read_csv(self._dataframe)
        return self._dataframe
