import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from joblib import dump, load
from sklearn.base import BaseEstimator

from .constants.paths import RUNS_PATH


class History:
    """
    This class has the responsibility to save what methods were previously executed
    in a Run. Each Run has one History. It is responsible for saving dataframes to
    disk.

    :param steps: is a list of the steps that have been executed, represented by
        ExecutedStep instances.
    :type steps: list[ExecutedStep]
    :param df_mode: determines if the dataframe of a completed step that is added to the
        history is saved to disk and not held im memory ("disk" mode), held in memory
        but not saved to disk ("memory" mode) or both ("disk_memory" mode).
    :type df_mode: str
    :param run_name: is the name of the run a history instance belongs to. It is used to
        save things at the correct disk location.
    :type run_name: str
    """

    @classmethod
    def from_disk(cls, run_name: str, df_mode: str):
        instance = cls(run_name, df_mode)
        with open(RUNS_PATH / run_name / "history.json", "r") as f:
            history_json = json.load(f, object_hook=load_objects)

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
                    messages=[],
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
        Path(f"{RUNS_PATH}/{run_name}").mkdir(exist_ok=True)

    def add_step(
        self,
        section: str,
        step: str,
        method: str,
        parameters: dict,
        dataframe: pd.DataFrame | None,
        outputs: dict,
        messages: list[dict] = [],
        plots: list = [],
        name: str | None = None,
    ):
        assert "dataframe" not in outputs, "output can not be named 'dataframe'"
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
            messages,
            plots,
        )
        self.steps.append(executed_step)
        self.step_names.append(None)
        self.name_step_in_history(-1, name)  # to have checks only in name_step
        self.save()

    def name_step_in_history(self, index, name):
        if not name or self.step_names[index] == name:
            return
        assert (
            self.step_names[index] is None
        ), f"step already has a name: {self.step_names[index]}"
        assert name not in self.step_names, f"name {name} is already taken"
        self.step_names[index] = name

    def output_keys_of_named_step(self, name):
        if not name or name == "None":
            return ["---"]
        for saved_name, step in zip(self.step_names, self.steps):
            if saved_name == name:
                options = list(step.outputs.keys())
                if step.has_dataframe:
                    options.insert(0, "dataframe")
                return options
        raise ValueError(f"no step named '{name}'")

    def output_of_named_step(self, name, output):
        if not name or name == "None":
            return ""
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
        self.save()
        return step, df

    def save(self):
        if (history_dfs_path := RUNS_PATH / self.run_name / "history_dfs").exists():
            shutil.rmtree(history_dfs_path)

        to_save = []
        for index, (name, step) in enumerate(zip(self.step_names, self.steps)):
            to_save.append(
                dict(
                    section=step.section,
                    step=step.step,
                    method=step.method,
                    name=name,
                    parameters=self.serialize(
                        step.parameters, index, step.section, step.step, step.method
                    ),
                    outputs=self.serialize(
                        step.outputs, index, step.section, step.step, step.method
                    ),
                )
            )
        history_json = json.dumps(to_save, indent=2)
        with open(RUNS_PATH / self.run_name / "history.json", "w") as f:
            f.write(history_json)

    def serialize(self, d, index, section, step, method):
        cleaned = {}
        for key, value in d.items():
            if isinstance(value, pd.DataFrame) or isinstance(value, pd.Series):
                filename = f"{index}-{section}-{step}-{method}-{key}.csv"

                path = RUNS_PATH / self.run_name / "history_dfs" / filename
                path.parent.mkdir(exist_ok=True)
                value.to_csv(path)
                cleaned[key] = {"__dataframe__": True, "path": str(path)}
            elif isinstance(value, BaseEstimator):
                filename = f"{index}-{section}-{step}-{method}-{key}.joblib"
                path = RUNS_PATH / self.run_name / "sklearn_estimators" / filename
                path.parent.mkdir(exist_ok=True)
                dump(value, path)
                cleaned[key] = {"__sklearn-estimator__": True, "path": str(path)}
            else:
                cleaned[key] = value
        return cleaned

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
    messages: list[dict]
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


def load_objects(dct):
    if dct.get("__dataframe__", False):
        return pd.read_csv(dct["path"], index_col=0)
    elif dct.get("__sklearn-estimator__", False):
        return load(dct["path"])
    else:
        return dct
