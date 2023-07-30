import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

df_20 = pd.read_csv(
    "./user_data/runs/ba39_HC/history_dfs/7-data_analysis-model_selection-cluster_multiple_sample_sizes_and_k-20.csv",
    sep=",",
)
df_40 = pd.read_csv(
    "./user_data/runs/ba39_HC/history_dfs/7-data_analysis-model_selection-cluster_multiple_sample_sizes_and_k-40.csv",
    sep=",",
)
df_60 = pd.read_csv(
    "./user_data/runs/ba39_HC/history_dfs/7-data_analysis-model_selection-cluster_multiple_sample_sizes_and_k-60.csv",
    sep=",",
)
df_80 = pd.read_csv(
    "./user_data/runs/ba39_HC/history_dfs/7-data_analysis-model_selection-cluster_multiple_sample_sizes_and_k-80.csv",
    sep=",",
)
df_100 = pd.read_csv(
    "./user_data/runs/ba39_HC/history_dfs/7-data_analysis-model_selection-cluster_multiple_sample_sizes_and_k-100.csv",
    sep=",",
)
df_139 = pd.read_csv(
    "./user_data/runs/ba39_HC/history_dfs/7-data_analysis-model_selection-cluster_multiple_sample_sizes_and_k-139.csv",
    sep=",",
)
all_df = [df_20, df_40, df_60, df_80, df_100, df_139]
sample_sizes = [20, 40, 60, 80, 100, 139]
braak_df = pd.read_csv("BA39_braak_stages.csv", sep=";")


def extract_substring_before_underscore(s):
    return s.split("_")[0]


order = ["0", "NA", "I", "II", "III-IV", "IV-V", "V", "V-VI", "VI"]
# Replace "NA" with np.nan in the 'Braak' column
braak_df["Braak"] = braak_df["Braak"].replace(np.nan, "NA")
print(braak_df)
# Convert 'Braak' column to categorical type with specified order
braak_df["Braak"] = pd.Categorical(braak_df["Braak"], categories=order, ordered=True)
figs = []

for sample_size, df in zip(sample_sizes, all_df):
    df.reset_index(inplace=True)
    df = df[["Sample"]]
    df = df["Sample"].apply(extract_substring_before_underscore)
    df = pd.merge(df, braak_df, on="Sample", how="inner")
    braak_hist = df[["Braak"]]

    # Count the occurrences of each label and reindex with the specified order
    braak_hist_counts = braak_hist["Braak"].value_counts().reindex(order, fill_value=0)

    # Plot the bar chart
    plt.figure()
    braak_hist_counts.plot(kind="bar")
    plt.xlabel("Braak Stage")
    plt.ylabel("Count")
    plt.title(f"Braak Stages - Sample Size {sample_size}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.ylim(0.0, 36)
    # Optionally, you can save the figure to a file or display it using plt.show()
    plt.savefig(f"braak/braak_{sample_size}.png")
    figs.append(plt)
