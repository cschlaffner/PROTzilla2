import pandas as pd


def metadata_import_method(df, file, feature_orientation):
    meta_df = pd.read_csv(
        file,
        sep=",",
        low_memory=False,
        na_values=[""],
        keep_default_na=True,
        skipinitialspace=True,
    )
    # always return metadata in the same orientation (features as columns)
    if feature_orientation.startswith("Rows"):
        meta_df = meta_df.transpose()
        meta_df.reset_index(inplace=True)
        meta_df.rename(columns=meta_df.iloc[0], inplace=True)
        meta_df.drop(index=0, inplace=True)
        meta_df.index = meta_df.index - 1
        for columns in meta_df:
            try:
                meta_df["Age"] = meta_df["Age"].astype("int64")
            except:
                pass
    return df, {"metadata": meta_df}
