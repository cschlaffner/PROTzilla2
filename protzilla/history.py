import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .constants.paths import RUNS_PATH
from .utilities.random import random_string


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
            history_json = json.load(f, object_hook=load_dataframes)
        for index, step in enumerate(history_json):
            df_path = instance.df_path(index)
            if df_path.exists() and "memory" in instance.df_mode:
                df = pd.read_csv(df_path)
            else:
                df = None
            instance.step_names.append(step["name"])
            instance.steps.append(
                ExecutedStep(
                    step["section"],
                    step["step"],
                    step["method"],
                    step["parameters"],
                    _dataframe=df,
                    dataframe_path=df_path if df_path.exists() else None,
                    outputs=step["outputs"],
                    plots=[],
                )
            )
        return instance

    def __init__(self, run_name: str, df_mode: str):
        assert df_mode in ("disk", "memory", "disk_memory")

        self.df_mode = df_mode
        self.run_name = run_name
        self.steps: list[ExecutedStep] = []
        self.step_names = []
        (RUNS_PATH / run_name).mkdir(exist_ok=True)

    def add_step(
        self,
        section: str,
        step: str,
        method: str,
        parameters: dict,
        dataframe: pd.DataFrame | None,
        outputs: dict,
        plots: list,
        name: str | None = None,
    ):
        assert "dataframe" not in outputs
        df_path = None
        df = None
        if "disk" in self.df_mode and dataframe is not None:
            index = len(self.steps)
            df_path = self.df_path(index)
            df_path.parent.mkdir(parents=True, exist_ok=True)
            dataframe.to_csv(df_path, index=False)
        if "memory" in self.df_mode:
            df = dataframe
        executed_step = ExecutedStep(
            section,
            step,
            method,
            parameters,
            df,
            df_path,
            outputs,
            plots,
        )
        self.steps.append(executed_step)
        self.step_names.append(None)
        self.name_step(-1, name)  # to have checks only in name_step
        if not name:  # not saved in name_step
            self.save()

    def name_step(self, index, name):
        if not name:
            return
        assert self.step_names[index] is None
        assert name not in self.step_names
        self.step_names[index] = name
        self.save()

    def output_keys_of_named_step(self, name):
        if not name:
            return []
        for saved_name, step in zip(self.step_names, self.steps):
            if saved_name == name:
                options = list(step.outputs.keys())
                if step.has_dataframe:
                    options.insert(0, "dataframe")
                return options
        raise ValueError(f"no step named '{name}'")

    def output_of_named_step(self, name, output):
        for saved_name, step in zip(self.step_names, self.steps):
            if saved_name == name:
                if output == "dataframe":
                    return step.dataframe
                return step.outputs[output]
        raise ValueError(f"no step named '{name}'")

    def pop_step(self):
        self.step_names.pop()
        step = self.steps.pop()
        df = step.dataframe
        if "disk" in self.df_mode and step.dataframe_path:
            step.dataframe_path.unlink()
        return step, df

    def save(self):
        # this assumes that parameters and outpus are json serializable
        # e.g. dict/list/number/str or a nesting of these
        to_save = [
            dict(
                section=step.section,
                step=step.step,
                method=step.method,
                name=name,
                parameters=step.parameters,
                outputs=step.outputs,
            )
            for name, step in zip(self.step_names, self.steps)
        ]
        history_json = CustomJSONEncoder(self.run_name, indent=2).encode(to_save)
        with open(RUNS_PATH / self.run_name / "history.json", "w") as f:
            f.write(history_json)

    def df_path(self, index: int):
        return RUNS_PATH / self.run_name / f"dataframes/df_{index}.csv"

    def number_of_steps_in_section(self, section):
        return len(list(filter(lambda step: step.section == section, self.steps)))


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
    def has_dataframe(self) -> bool:
        return self._dataframe is not None or self.dataframe_path is not None

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


class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, run_name, **kw):
        self.run_name = run_name
        super().__init__(**kw)

    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            path = RUNS_PATH / self.run_name / f"history_dfs/{random_string()}.csv"
            path.parent.mkdir(exist_ok=True)
            obj.to_csv(path, index=False)
            return {"__dataframe__": True, "path": str(path)}
        return json.JSONEncoder.default(self, obj)


def load_dataframes(dct):
    if dct.get("__dataframe__", False):
        return pd.read_csv(dct["path"])
    return dct
