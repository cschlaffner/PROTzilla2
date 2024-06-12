import logging

import pandas as pd


def filter_peptides_of_protein(
        peptide_df: pd.DataFrame, protein_ids: list[str],
) -> dict:
    """
    This function filters out all peptides with a PEP value (assigned to all samples
    together for each peptide) below a certain threshold.

    :param peptide_df: the pandas dataframe containing the peptide information
    :param protein_ids: the protein ID to filter the corresponding peptides for

    :return: dict of the filtered peptide dataframe
    """

    filtered_peptide_dfs = [pd.DataFrame] * len(protein_ids)
    for i, protein_id in enumerate(protein_ids):
        filtered_peptide_dfs[i] = peptide_df[peptide_df["Protein ID"].str.contains(protein_id)]
    filtered_peptides = pd.concat(filtered_peptide_dfs)

    return dict(
        peptide_df=filtered_peptides,
        messages=[{
            "level": logging.INFO if len(filtered_peptides) > 0 else logging.WARNING,
            "msg": f"Selected {len(filtered_peptides)} entry's from the peptide dataframe."
        }],
    )


def ptms_per_sampel(peptide_df: pd.DataFrame) -> dict:
    """
    This function calculates the amount of every PTMs per sample.

    :param peptide_df: the pandas dataframe containing the peptide information

    :return: dict containing a dataframe one row per sample and one column per PTM that occurs in the peptide_df,
    with the cells containing the amount of the PTM in the sample
    """

    modifications = pd.Series(sum(peptide_df["Modifications"].str.split(","), [])).unique()
    sampels = peptide_df["Sample"].unique()

    all_mod_counts = pd.DataFrame(sampels).rename(columns={0: "Sample"})

    for mod in modifications:
        filtered = peptide_df[peptide_df["Modifications"].str.contains(re.escape(mod))]

        mod_counts_without_zero = filtered.groupby('Sample')["Modifications"].size()
        mod_counts = mod_counts_without_zero.reindex(sampels).fillna(0)

        all_mod_counts[mod] = mod_counts.values

    return dict(ptm_df=all_mod_counts)


def ptms_per_protein_and_sampel(peptide_df: pd.DataFrame) -> dict:
    """
    This function calculates the amount of every PTM per sample and protein.

    :param peptide_df: the pandas dataframe containing the peptide information

    :return: dict containing a dataframe one row per sample and one column per protein,
    with the cells containing a list of PTMs that occur in the peptide_df for the protein and sample and
    their amount in the protein and sample
    """

    proteins = peptide_df["Protein ID"].unique()
    samples = peptide_df["Sample"].unique()

    ptm_df = pd.DataFrame(samples).rename(columns={0: "Sample"})
    ptm_df = ptm_df.assign(**{protein: None for protein in proteins})

    for j, protein in enumerate(proteins):
        filtered = peptide_df[peptide_df["Protein ID"].str.contains(re.escape(protein))]

        for i, sample in enumerate(samples):
            filtered_sample = filtered[filtered["Sample"] == sample]

            modifications = pd.Series(sum(filtered_sample["Modifications"].str.split(","), [])).unique()

            modifications_str = ""

            for mod in modifications:
                filtered_mod = filtered_sample[filtered_sample["Modifications"].str.contains(re.escape(mod))]

                mod_counts = filtered_mod.groupby('Sample')["Modifications"].size()
                mod_counts = mod_counts.reindex(samples).fillna(0)

                modifications_str += f"{int(mod_counts[sample])} {mod}, \n"

            ptm_df[f"{protein}"][i] = modifications_str

        print(f"analyzed protein  {protein} ({j}/{len(proteins)})")

    return dict(ptm_df=ptm_df)
