import pandas as pd
from protzilla.utilities.utilities import clean_uniprot_id
from protzilla.data_integration.enrichment_analysis_helper import map_to_string_ids

from protzilla.data_integration.database_query import uniprot_groups_to_genes

# hf_df = pd.read_csv("data/hf_imported_df.csv", header=0)
# proteins = hf_df["Protein ID"].unique().tolist()
# print("proteins", len(proteins))
# # gene_to_groups, group_to_genes, filtered = uniprot_groups_to_genes(uniprot_groups=proteins, databases=["all_reviewed", "uniprot_human"], use_biomart=False)
# # genes = list(gene_to_groups.keys())
# # print("genes", len(genes))
# # print("filtered", len(filtered))
#
# # proteins 3799
# # genes 5034
# # filtered 126
#
# # print(hf_df["Protein ID"].str.split(";").apply(len).mean())  # 10.037904711766254
#
# statistical_background = proteins
# background_ids = set()
# split = dict()
# for protein_group in statistical_background:
#     for p in protein_group.split(";"):
#         p = clean_uniprot_id(p)
#         split[p] = protein_group
#     background_ids.update(map(clean_uniprot_id, protein_group.split(";")))
#
# statistical_background = list(background_ids)
# statistical_background, groups = map_to_string_ids(statistical_background, "human", split)
#
# print("number of mapped background ids", len(statistical_background))
# print("number of groups", len(set(groups)))
# print("not found groups", len(set(proteins).difference(set(groups))))




# with open('background_gene_symbols_new.txt', 'w') as file:
#     # Write each string on a separate line
#     for string in genes:
#         file.write(string + '\n')


# enrichr_df = pd.read_csv("enr_data/Enrichr_df.csv", index_col=0)
# offline_df = pd.read_csv("enr_data/offline_df.csv", index_col=0)
# string_df = pd.read_csv("enr_data/string_df.csv", index_col=0)
# overlap_df = pd.read_csv("enr_data/overlap_df.csv", index_col=0)
#
# overlap_dict = dict(zip(overlap_df["Term"], overlap_df.index))
#
# # make lists of list into one big list
# enrichr_list = [item for sublist in enrichr_df["Genes"].tolist() for item in sublist]


# set index of a dataframe from 0 to 1
