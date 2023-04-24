import gc
import sys
import time

import pandas as pd


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
        finally:
            return elements


class DebugInfo:
    print_elements = {}  # "name":{"time": , "memory": , "dfs": , "index", "time_next_step"}
    print_index = 0

    time_measurements = {}

    def __init__(self):
        self.run = None

    def print_element(self, name, index=None):
        if index is None:
            index = self.print_index
            self.print_index += 1
        if name not in self.print_elements:
            self.print_elements[name] = {"index": index}
        return self.print_elements[name]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
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
        self.print_element(name)["memory"] = f"{total_memory:.0f} MB"
        self.print_element(name)["dfs"] = str(
            [f"{sys.getsizeof(element) / (1024 ** 2):.2f} MB" for element in get_all_objects(pd.DataFrame)])

    def save_print_elements(self):
        with open(f"{self.run.run_path}/debug.txt", "w") as f:
            f.write(str(self))

    def __str__(self):
        string = ""
        # sort print_elements by index
        for name in sorted(self.print_elements, key=lambda x: self.print_elements[x]["index"]):
            string += f"{name}: {self.print_elements[name]}\n"
        return string
