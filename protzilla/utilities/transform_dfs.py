import pandas as pd


def long_to_wide(intensity_df: pd.DataFrame):
    # df = pd.pivot(df, index='team', columns='player', values='points')
    values_name = intensity_df.columns[3]
    return pd.pivot(
        intensity_df, index="Sample", columns="Protein ID", values=values_name
    )
