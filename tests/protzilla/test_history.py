from protzilla.history import History
import pandas as pd


def test_history_memory_identity():
    history = History("test_memory_identity", df_mode="memory")
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


def test_history_disk():
    history = History("test_disk", df_mode="disk")
    df1 = pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
    history.add_step(
        "section1", "step1", "method1", {"param1": 3}, df1, outputs={}, plots=[]
    )
    assert not isinstance(history.steps[0]._dataframe, pd.DataFrame)
    assert history.steps[0].dataframe.equals(df1)


def test_history_disk_delete():
    history = History("test_disk_delete", df_mode="disk")
    df1 = pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
    history.add_step(
        "section1", "step1", "method1", {"param1": 3}, df1, outputs={}, plots=[]
    )
    assert history.df_path(0).exists()
    history.pop_step()
    assert not history.df_path(0).exists()
