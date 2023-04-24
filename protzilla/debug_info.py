import gc
import sys
import time
from pathlib import Path

import pandas as pd

from prettytable import PrettyTable

from protzilla.constants.paths import PROJECT_PATH


def get_memory_usage(type):
    elements = get_all_objects(type)
    memory = sum(sys.getsizeof(element) for element in elements)
    return memory, len(elements)


def get_all_objects(type):
    objects = gc.get_objects()
    elements = []
    for element in objects:
        try:
            if isinstance(element, type):
                elements.append(element)
        except Exception:
            pass
    return elements


class DebugInfo:
    instance = None
    print_elements = {}  # "name":{"time": , "total_memory": , "dfs": , "index", "time_next_step"}
    print_index = 0

    time_measurements = {}

    def print_element(self, name, index=None):
        if index is None:
            index = self.print_index
            self.print_index += 1
        if name not in self.print_elements:
            self.print_elements[name] = {"index": index}
        return self.print_elements[name]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance') or cls.instance is None:
            cls.instance = super(DebugInfo, cls).__new__(cls)
        return cls.instance

    def measure_start(self, name, index=None):
        if index is not None:
            self.print_element(name, index)
        self.time_measurements[name] = time.time()

    def measure_end(self, name):
        self.time_measurements[name] = (time.time() - self.time_measurements[name])
        self.print_element(name)["time"] = f"{(self.time_measurements[name] * 1000):.0f} ms"

    def measure_continue(self, name, index=None):
        if name not in self.time_measurements.keys():
            return self.measure_start(name, index)
        self.time_measurements[name] = (time.time() - self.time_measurements[name])

    def measure_memory(self, name):
        memory_df, df_count = get_memory_usage(pd.DataFrame)
        total_memory, _ = get_memory_usage(object)
        self.print_element(name)["total_memory"] = f"{total_memory/ (1024 ** 2):.2f} MB"
        self.print_element(name)["dfs"] = str(
            [f"{sys.getsizeof(element) / (1024 ** 2):.2f} MB" for element in get_all_objects(pd.DataFrame)])

    def save_print_elements(self):
        path = Path(f"{PROJECT_PATH}/user_data/debug/{self.run_name}.txt")
        with open(path, "w") as f:
            f.write(str(self))

    def __str__(self):
        t = PrettyTable(["name", "time", "total_memory", "dfs"])
        # sort print_elements by index
        for name in sorted(self.print_elements, key=lambda x: self.print_elements[x]["index"]):
            t.add_row([name, self.print_elements[name].get("time", ""), self.print_elements[name].get("total_memory", ""),
                          self.print_elements[name].get("dfs", "")])
        return str(t)
