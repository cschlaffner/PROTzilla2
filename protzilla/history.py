from pathlib import Path
from typing import List, Any

import pandas as pd

# TODO put constants in constants-file
PATH_TO_RUNS = "user_data/runs/"


class History:

    def __init__(self, run_name, df_mode="disk"):
        assert df_mode in ("disk", "memory")

        self.df_mode = df_mode
        self.run_name = run_name
        # list of dicts
        self.steps: list[dict] = []
        pass

    def get_df(self, index):
        if self.df_mode == "disk":
            return pd.read_csv(self.df_path(index))
        if self.df_mode == "memory":
            return self.steps[index]["output"]["df"]

    def set_df(self, index, df):
        if self.df_mode == "disk":
            df.to_csv(self.df_path(index))
        if self.df_mode == "memory":
            self.steps[index]["output"]["df"] = df

    def add_step(self, section_name, step_name, method_name, params: list, plots: list, output_df: pd.DataFrame,
                 output_dict: dict):

        step_dict = {
            "section": section_name,
            "step": step_name,
            "method": method_name,
            "params": params,
            "plots": plots,
            "outputs": {
                "df": None,
                "dict": output_dict
            }
        }

        index = len(self.steps)
        if self.df_mode == "disk":
            output_df.to_csv(self.df_path(index))
        if self.df_mode == "memory":
            step_dict["outputs"]["df"] = output_df

        self.steps.append(step_dict)

    def df_path(self, index):
        return Path(PATH_TO_RUNS + self.run_name + "/df_" + index + ".csv")

    def name_to_indexes(self, name):
        return [self.steps.index(step) for step in self.steps if step["step"] is name]
