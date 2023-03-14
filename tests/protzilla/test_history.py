from random import choices
from shutil import rmtree
from string import ascii_letters

import pandas as pd

from protzilla.constants.constants import PATH_TO_RUNS
from protzilla.history import History


def random_string():
    return "".join(choices(ascii_letters, k=32))


def test_history_memory_identity():
    name = "test_memory_identity" + random_string()
    history = History(name, df_mode="memory")
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    history.add_step(
        "section1", "step1", "method1", {"param1": 3}, df1, outputs={}, plots=[]
    )
    history.add_step(
        "section2", "step2", "method2", {"param1": 5}, df2, outputs={}, plots=[]
    )
    assert history.steps[0].dataframe is df1
    assert history.steps[0].dataframe is not df2
    assert history.steps[1].dataframe is df2
    assert history.steps[1].dataframe is not df1
    rmtree(PATH_TO_RUNS / name)


def test_history_disk():
    name = "test_disk" + random_string()
    history = History(name, df_mode="disk")
    df1 = pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
    history.add_step(
        "section1", "step1", "method1", {"param1": 3}, df1, outputs={}, plots=[]
    )
    # the history should not contain a dataframe in memory when using disk mode
    assert history.steps[0]._dataframe is None
    # the dataframe should be loaded from disk correctly when using .dataframe
    assert history.steps[0].dataframe.equals(df1)
    rmtree(PATH_TO_RUNS / name)


def test_history_disk_delete():
    name = "test_disk_delete" + random_string()
    history = History(name, df_mode="disk")
    df1 = pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
    history.add_step(
        "section1", "step1", "method1", {"param1": 3}, df1, outputs={}, plots=[]
    )
    assert history.df_path(0).exists()
    history.remove_step()
    assert not history.df_path(0).exists()
    rmtree(PATH_TO_RUNS / name)


def test_history_save():
    name = "test_history_save" + random_string()
    history = History(name, df_mode="disk")
    df1 = pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
    history.add_step(
        "section1", "step1", "method1", {"param1": 3}, df1, outputs={}, plots=[]
    )
    df2 = pd.DataFrame(data={"hellocol": [2, 2], "col2": [4, 4]})
    history.add_step(
        "section2",
        "step2",
        "method2",
        {"param3": 3, "other": "no"},
        df2,
        outputs={"out": 5},
        plots=[],
    )
    history.save()
    steps = history.steps
    del history
    history2 = History.from_disk(name, df_mode="disk")
    assert steps[0].dataframe.equals(history2.steps[0].dataframe)
    assert history2.steps[0]._dataframe is None
    assert steps[1].dataframe.equals(history2.steps[1].dataframe)
    assert history2.steps[1]._dataframe is None
    rmtree(PATH_TO_RUNS / name)
