import pandas as pd

from protzilla.data_integration.database_query import uniprot_query_dataframe


def add_uniprot_data(dataframe, fields=None):
    if not fields:
        return {"result": dataframe}
    if isinstance(fields, str):
        fields = [fields]
    groups = dataframe["Protein ID"].tolist()
    # group size
    # [(1, 305), (2, 203), (3, 91), (4, 52), (5, 24), (7, 13), (6, 11), (8, 8), (9, 4), (10, 3), (15, 2), (16, 2), (17, 1), (23, 1), (13, 1), (18, 1), (31, 1), (21, 1)]
    # after processig
    # [(1, 597), (2, 85), (3, 24), (4, 9), (5, 3), (6, 1), (8, 1), (31, 1), (10, 1), (16, 1), (15, 1)]
    clean_groups = []
    all_proteins = set()

    # remove isoforms and variants from groups
    for group in groups:
        proteins = group.split(";")
        cleaned = set()
        for protein in proteins:
            if "-" in protein:
                protein = protein.split("-")[0]
            if protein.startswith("CON__") or protein.startswith("REV__"):
                protein = protein[5:]
            if "_VAR_" in protein:
                protein = protein.split("_VAR_")[0]
            cleaned.add(protein)
            all_proteins.add(protein)
        clean_groups.append(cleaned)
    res: pd.DataFrame = uniprot_query_dataframe(list(all_proteins), fields)

    new_columns = {k: [] for k in fields}  # data that will be added to input df
    for group in clean_groups:
        group_dict = {k: [] for k in fields}
        # data that different members of group have
        for member in group:
            if member not in res.index:
                continue
            result = res.loc[member]
            for col, val in result.to_dict().items():
                if "Gene Names" in col and not isinstance(val, float):
                    # to remove space seperated groupings
                    group_dict[col].append(val.split()[0])
                else:
                    group_dict[col].append(val)
        for field in fields:
            # add unique values to only, join if necessary
            new_columns[field].append(";".join(map(str, set(group_dict[field]))))

    # we can concat because clean groups has the same order as groups
    out = pd.concat([dataframe, pd.DataFrame(new_columns)], axis=1)
    return {"result": out}


if __name__ == "__main__":
    df = pd.read_csv(
        "/Users/fynnkroeger/Desktop/Studium/Bachelorprojekt/PROTzilla2/user_data/runs/adfg/history_dfs/8-data_analysis-differential_expression-t_test-log2_fold_change_df.csv",
        index_col=0,
    )
    from time import time

    t = time()
    add_uniprot_data(df, fields=["Gene Names", "Organism", "Length"])
    print(time() - t)
