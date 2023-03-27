import pandas as pd


def metadata_import_method(df, file, feature_orientation):
    meta_df = pd.read_csv(
        file,
        sep=",",
        low_memory=False,
        na_values=[""],
        keep_default_na=True,
    )
    # always return metadata in the same orientation (features as columns)
    if feature_orientation.startswith("Rows"):
        meta_df = meta_df.transpose()

    return df, {"metadata": meta_df}
