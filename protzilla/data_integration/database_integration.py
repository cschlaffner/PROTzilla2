import pandas as pd
from itertools import groupby
import operator
from django.contrib import messages

from protzilla.data_integration.database_query import uniprot_query_dataframe
from protzilla.importing.ms_data_import import clean_uniprot_id


# recipie from https://docs.python.org/3/library/itertools.html
def unique_justseen(iterable, key=None):
    """List unique elements, preserving order. Remember only the element just seen."""
    # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    # unique_justseen('ABBcCAD', str.lower) --> A B c A D
    return map(next, map(operator.itemgetter(1), groupby(iterable, key)))


def add_uniprot_data(dataframe, fields=None):
    if not fields:
        msg = "No fields that should be added specified."
        return dict(
            result=dataframe,
            messages=[dict(level=messages.INFO, msg=msg)],
        )
    if isinstance(fields, str):
        fields = [fields]
    groups = dataframe["Protein ID"].tolist()
    clean_groups = []
    all_proteins = set()

    # remove isoforms and variants from groups
    for group in groups:
        proteins = group.split(";")
        cleaned = []
        for protein in proteins:
            clean = clean_uniprot_id(protein)
            cleaned.append(clean)
            all_proteins.add(clean)
        # this can be done because we make isoforms appear together
        clean_groups.append(list(unique_justseen(cleaned)))

    # add links
    if "Links" in fields:
        links = []
        for group in clean_groups:
            group_links = [
                f"https://uniprot.org/uniprotkb/{protein}" for protein in group
            ]
            links.append(" ".join(group_links))
        dataframe["Links"] = links
    database_fields = [field for field in fields if field != "Links"]
    if not database_fields:
        return {"result": dataframe}
    res: pd.DataFrame = uniprot_query_dataframe(list(all_proteins), database_fields)

    # data that will be added to input df
    new_columns = {k: [] for k in fields if k != "Links"}

    # @REVIEWER is it better to have a for loop for columns and retrive each protein multiple times from res?

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
        for field in database_fields:
            # add unique values to only, join if necessary
            if len(set(group_dict[field])) == 1:
                new_columns[field].append(group_dict[field][0])
            else:
                new_columns[field].append(";".join(map(str, group_dict[field])))

    # we can concat because clean groups has the same order as groups
    out = pd.concat([dataframe, pd.DataFrame(new_columns)], axis=1)
    return {"result": out}
