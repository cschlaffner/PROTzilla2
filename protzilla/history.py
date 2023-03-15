import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .constants.paths import RUNS_PATH


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

    @classmethod
    def from_disk(cls, run_name: str, df_mode: str):
        instance = cls(run_name, df_mode)
        with open(RUNS_PATH / run_name / "history.json", "r") as f:
            history_json = json.load(f)
        for index, step in enumerate(history_json):
            df_path = instance.df_path(index)
            if df_path.exists() and "memory" in instance.df_mode:
                df = pd.read_csv(df_path)
            else:
                df = None
            instance.steps.append(
                ExecutedStep(
                    step["section"],
                    step["step"],
                    step["method"],
                    step["parameters"],
                    df,
                    df_path if df_path.exists() else None,
                    step["outputs"],
                    plots=[],
                )
            )
        return instance

    def __init__(self, run_name: str, df_mode: str):
        assert df_mode in ("disk", "memory", "disk_memory")

        self.df_mode = df_mode
        self.run_name = run_name
        self.steps: list[ExecutedStep] = []
        (RUNS_PATH / run_name).mkdir(exist_ok=True)

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
            (RUNS_PATH / self.run_name).mkdir(parents=True, exist_ok=True)
            dataframe.to_csv(self.df_path(index), index=False)
            df_path = self.df_path(index)
        if "memory" in self.df_mode:
            df = dataframe
        executed_step = ExecutedStep(
            section, step, method, parameters, df, df_path, outputs, plots
        )
        self.steps.append(executed_step)
        self.save()

    def remove_step(self):
        step = self.steps.pop()
        if "disk" in self.df_mode:
            step.dataframe_path.unlink()

    def save(self):
        # this assumes that parameters and outpus are json serializable
        # e.g. dict/list/number/str or a nesting of these
        to_save = [
            dict(
                section=step.section,
                step=step.step,
                method=step.method,
                parameters=step.parameters,
                outputs=step.outputs,
            )
            for step in self.steps
        ]
        with open(RUNS_PATH / self.run_name / "history.json", "w") as f:
            json.dump(to_save, f, indent=2)

    def df_path(self, index: int):
        return RUNS_PATH / self.run_name / f"df_{index}.csv"


@dataclass(frozen=True)
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
