def filter_for_name(runs, search_string) -> list[dict[str, str | list[str]]]:
    return [run for run in runs if search_string in run["run_name"]]

def filter_for_steps(runs, search_steps) -> list[dict[str, str | list[str]]]:
    return [run for run in runs if all(step in run["run_steps"] for step in search_steps)]

def filter_for_tags(runs, search_tags) -> list[dict[str, str | list[str]]]:
    return [run for run in runs if all(tag in run["run_tags"] for tag in search_tags)]

def filter_for_memory_mode(runs, memory_mode) -> list[dict[str, str | list[str]]]:
    return [run for run in runs if run["memory_mode"] == memory_mode]

def filter_runs(runs, filters) -> list[dict[str, str | list[str]]]: #to be implemented
    if filters["name"]:
        runs = filter_for_name(runs, filters["name"])
    if filters["steps"]:
        runs = filter_for_steps(runs, filters["steps"])
    if filters["tags"]:
        runs = filter_for_tags(runs, filters["tags"])

    runs = filter_for_memory_mode(runs, filters["memory_mode"])
    return runs