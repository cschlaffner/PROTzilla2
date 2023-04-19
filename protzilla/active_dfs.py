import gc
import sys

import pandas as pd


def get_all_active_dfs(t):
    # Get all active objects tracked by the garbage collector
    objects = gc.get_objects()

    # Filter the list to only include objects of type 'DataFrame'
    lists = [obj for obj in objects if isinstance(obj, t)]

    # Calculate the total memory usage of all active lists
    total_memory = sum(sys.getsizeof(lst) for lst in lists)

    # Print the number of active lists and their memory addresses
    print(f"Number of active pd.DataFrame: {len(lists)}")
    for lst in lists:
        print(hex(id(lst)))

    # Print the total memory usage in bytes and in a human-readable format
    print(f"Total memory usage of active dataframes: {total_memory} bytes")
    print(
        f"Total memory usage of active dataframes: {total_memory / (1024 ** 2):.2f} MB"
    )
    return lists, total_memory

def get_debugging_info():
    lists, memory = get_all_active_dfs(pd.DataFrame)
    _, total_memory = get_all_active_dfs(object)
    return f"Active dataframes: {len(lists)} memory: {memory / (1024 ** 2):.2f} MB, total: {total_memory / (1024 ** 2):.2f} MB"
