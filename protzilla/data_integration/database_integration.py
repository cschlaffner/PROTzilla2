import pandas as pd
from itertools import groupby
import operator

from protzilla.data_integration.database_query import uniprot_query_dataframe
from protzilla.importing.ms_data_import import normalize_uniprot_id


# recipie from https://docs.python.org/3/library/itertools.html
def unique_justseen(iterable, key=None):
    """List unique elements, preserving order. Remember only the element just seen."""
    # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    # unique_justseen('ABBcCAD', str.lower) --> A B c A D
    return map(next, map(operator.itemgetter(1), groupby(iterable, key)))


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
        cleaned = []
        for protein in proteins:
            normalized = normalize_uniprot_id(protein)
            cleaned.append(normalized)
            all_proteins.add(normalized)
        # this can be done because we make isoforms appear together
        clean_groups.append(list(unique_justseen(cleaned)))
    res: pd.DataFrame = uniprot_query_dataframe(list(all_proteins), fields)

    new_columns = {k: [] for k in fields}  # data that will be added to input df
    # is it better to have a for loop for columns and retrive each protein multiple times from res?

    for group in clean_groups:
        group_dict = {k: [] for k in fields}
        # data that different members of group have
        for member in group:
            if member not in res.index:
                result = {k: None for k in fields}
            else:
                result = res.loc[member].to_dict()
            for col, val in result.items():
                if "Gene Names" in col and isinstance(val, str):
                    # to remove space seperated groupings
                    group_dict[col].append(val.split()[0])
                else:
                    group_dict[col].append(val)
        for field in fields:
            # add unique values to only, join if necessary
            if len(set(group_dict[field])) == 1:
                new_columns[field].append(group_dict[field][0])
            else:
                new_columns[field].append(";".join(map(str, group_dict[field])))

    # we can concat because clean groups has the same order as groups
    out = pd.concat([dataframe, pd.DataFrame(new_columns)], axis=1)
    return {"result": out}


if __name__ == "__main__":
    df = pd.read_csv(
        "/Users/fynnkroeger/Desktop/Studium/Bachelorprojekt/PROTzilla2/user_data/runs/with_id_sorting/history_dfs/8-data_analysis-differential_expression-t_test-log2_fold_change_df.csv",
        index_col=0,
    )
    from time import time

    t = time()
    a = add_uniprot_data(df, fields=["Gene Names (primary)", "Organism", "Length"])
    a["result"].to_csv("result.csv")
    print(time() - t)
