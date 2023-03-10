from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .constants.constants import PATH_TO_RUNS


class History:
    """
    This class has the responsibility to save what methods were previously executed
    in a Run. Each Run has one History. It is responsible for saving dataframes to
    disk.
    :ivar steps is a list of the steps that have been executed, represented by
        ExecutedStep instances.
    :ivar df_mode determines if the dataframe of a completed step that is added to the
        history is saved to disk and not held im memory ("disk" mode), held in memory
        but not saved to disk ("memory" mode) or both ("disk_memory" mode).
    :ivar run_name is the name of the run a history instance belongs to. It is used to
        save things at the correct disk location.
    """

    def __init__(self, run_name: str, df_mode: str):  # remane to save_df?
        assert df_mode in ("disk", "memory", "disk_memory")

        self.df_mode = df_mode
        self.run_name = run_name
        self.steps: list[ExecutedStep] = []

    def add_step(
        self,
        section: str,
        step: str,
        method: str,
        parameters: dict,
        dataframe: pd.DataFrame,
        outputs: dict,
        plots: list,
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

    def remove_step(self):
        step = self.steps.pop()
        if "disk" in self.df_mode:
            step.dataframe_path.unlink()

    def df_path(self, index: int):
        return PATH_TO_RUNS / self.run_name / f"df_{index}.csv"


@dataclass
class ExecutedStep:
    """
    This class represents a step that was executed in a run. It holds the outputs of
    that step. Instances of this class are not supposed to change.
    """

    section: str
    step: str
    method: str
    parameters: dict
    _dataframe: pd.DataFrame | None
    dataframe_path: Path | None
    outputs: dict
    plots: list

    @property
    def dataframe(self) -> pd.DataFrame | None:
        """
        :return: The dataframe that was the output of this step. Loads from disk if
        necessary.
        """
        if self._dataframe is not None:
            return self._dataframe
        if self.dataframe_path is not None:
            return pd.read_csv(self.dataframe_path)
        return None
