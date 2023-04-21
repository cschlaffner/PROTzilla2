import gc
import sys

import pandas as pd


class Debug_info:
    debug_elements = {}

    def get_all_active_dfs(self, t):
        # Get all active objects tracked by the garbage collector
        objects = gc.get_objects()

        # Filter the element to only include objects of type 'DataFrame'
        elements = []
        for element in objects:
            try:
                if isinstance(element, t):
                    elements.append(element)
            except:
                pass


        # Calculate the total memory usage of all active elements
        total_memory = sum(sys.getsizeof(element) for element in elements)

        # Print the number of active elements and their memory addresses
        # print(f"Number of active {t}: {len(elements)}")
        # if len(elements) > 0:
        #    print("first element: ", elements[0], "type: ", type(elements[0]))
        # Print the total memory usage in bytes and in a human-readable format
        # print(f"Total memory usage of active dataframes: {total_memory} bytes")
        # print(
        #    f"Total memory usage of active dataframes: {total_memory / (1024 ** 2):.2f} MB"
        # )
        return elements, total_memory

    def __str__(self):
        lists, memory = self.get_all_active_dfs(pd.DataFrame)
        _, total_memory = self.get_all_active_dfs(object)
        return f"Active dataframes: {len(lists)} memory: {memory / (1024 ** 2):.2f} MB, total: {total_memory / (1024 ** 2):.2f} MB {' '.join(self.debug_elements.values())}"
