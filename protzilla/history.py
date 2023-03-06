from pathlib import Path
from dataclasses import dataclass
import pandas as pd
from .constants.constants import PATH_TO_RUNS


class History:
    def __init__(self, run_name, df_mode):  # remane to save_df?
        assert df_mode in ("disk", "memory", "disk_memory")

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
        df_path = None
        df = None
        if "disk" in self.df_mode:
            index = len(self.steps)
            (PATH_TO_RUNS / self.run_name).mkdir(parents=True, exist_ok=True)
            dataframe.to_csv(self.df_path(index), index=False)
            df_path = self.df_path(index)
        if "memory" in self.df_mode:
            df = dataframe
        executed_step = ExecutedStep(
            section, step, method, parameters, df, df_path, outputs, plots
        )
        self.steps.append(executed_step)
        # save steps to disk?

    def back_step(self):
        step = self.steps.pop()
        if "disk" in self.df_mode:
            step.dataframe_path.unlink()

    def df_path(self, index):
        return PATH_TO_RUNS / self.run_name / f"df_{index}.csv"


@dataclass
class ExecutedStep:
    section: str
    step: str
    method: str
    parameters: dict
    _dataframe: pd.DataFrame | None
    dataframe_path: Path | None
    outputs: dict
    plots: list

    @property
    def dataframe(self):
        if self._dataframe is not None:
            return self._dataframe
        if self.dataframe_path is not None:
            return pd.read_csv(self.dataframe_path)
        return None
