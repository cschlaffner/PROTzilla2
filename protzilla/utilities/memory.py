import os

import psutil


def get_memory_usage():
    memory_mb = psutil.Process(os.getpid()).memory_info().rss / 1024**2
    return f"{round(memory_mb,1)} MB"
