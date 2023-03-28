import pandas as pd

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities.random import random_string


def metadata_import_method(df, file, feature_orientation):
    if file.endswith(".csv"):
        print("\nfile", file)
        meta_df = pd.read_csv(
            file,
            sep=",",
            low_memory=False,
            na_values=[""],
            keep_default_na=True,
            skipinitialspace=True,
        )
    elif file.endswith(".xlsx"):
        meta_df = pd.read_excel(file)
    elif file.endswith(".psv"):
        meta_df = pd.read_csv(file, sep="|", low_memory=False)
    elif file.endswith(".tsv"):
        meta_df = pd.read_csv(file, sep="\t", low_memory=False)
    else:
        raise TypeError(
            "File format not supported. \
        Supported file formats are csv, xlsx, psv or tsv"
        )

    print("\n post read, file:", file)
    print("meta info", meta_df.info())

    # always return metadata in the same orientation (features as columns)
    if feature_orientation.startswith("Rows"):
        print("file in ROWS", file)
        print("\npre")
        print("\nmeta rows\n", meta_df)
        print("meta rows info ^^", meta_df.info())

        meta_df = meta_df.transpose()
        meta_df.reset_index(inplace=True)
        meta_df.rename(columns=meta_df.iloc[0], inplace=True)
        meta_df.drop(index=0, inplace=True)
        meta_df.index = meta_df.index - 1

        print("\n\npost")
        print("\nmeta rows\n", meta_df)
        print("meta rows info", meta_df.info(), "\n")

        file_path = f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_{random_string()}.csv"
        print(file_path)
        meta_df.to_csv(file_path, index=False)
        return metadata_import_method(df, file_path, "Columns")

    elif file.startswith(f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_"):
        # os.remove(file)
        print("skipped ROWS for file ", file)
    else:
        print("skipped ROWS for file ", file)

    print("\n\n end of import\n\n")
    return df, {"metadata": meta_df}
