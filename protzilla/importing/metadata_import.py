import pandas as pd


def metadata_import_method(_, file, feature_orientation):
    df = pd.read_csv(
        file,
        sep=",",
        low_memory=False,
        na_values=[""],
        keep_default_na=True,
    )
    # always return metadata in the same orientation (features as columns)
    if feature_orientation.startswith("Rows"):
        df = df.transpose()

    return _, {"metadata": df}
