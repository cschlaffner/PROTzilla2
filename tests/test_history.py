from protzilla.history import History
import pandas as pd



def test_history_memory():
    # TODO split in many tests
    hist = History("test_run", df_mode="memory")
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

    hist.add_step("section1", "step1", "method1", ["param1"], [], df1, {})
    hist.add_step("section2", "step2", "method2", ["param2"], [], df2, {})
    print(hist.steps)
    assert hist.get_df(0) is df1

    assert hist.get_df(1) is not df1
    hist.set_df(1, df1)
    assert hist.get_df(1) is df1


def test_history_disk():
    assert True


def test_name_to_index():
    hist = History("test_run", df_mode="memory")
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

    hist.add_step("section1", "step1", "method1", ["param1"], [], df1, {})
    hist.add_step("section2", "step2", "method2", ["param2"], [], df2, {})

    assert hist.name_to_indexes("step2") == [1]
