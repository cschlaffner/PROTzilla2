def filter_for_name(runs, search_string) -> list[dict[str, str | list[str]]]:
    return runs

def filter_for_steps(runs, search_steps) -> list[dict[str, str | list[str]]]:
    return runs

def filter_runs(runs, filters) -> list[dict[str, str | list[str]]]: #to be implemented
    runs = filter_for_name(runs, filters.name)
    runs = filter_for_steps(runs, filters.steps)
    return runs