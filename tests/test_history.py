from internal.history import History
import pandas as pd


def test_history_memory():
    # TODO split in many tests
    hist = History("test_run", df_mode="memory")
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

    assert df1 is not df2

    # TODO might add plot
    plot1 = "plot"

    hist.add_step("section1", "step1", "method1", ["param1"], [plot1], df1, {})
    hist.add_step("section2", "step2", "method2", ["param2"], [plot1], df2, {})

    assert hist.get_df(0) is df1
    assert hist.name_to_indexes("step2") is [1]

    hist.set_df(1, df1)
    assert hist.get_df(1) is df1


def test_history_disk():
    assert True
