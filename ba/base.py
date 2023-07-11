import pandas as pd
from protzilla.data_integration.database_query import uniprot_groups_to_genes

hf_df = pd.read_csv("/ba/data/hf_imported_bg.csv", header=0)
proteins = hf_df["Protein ID"].unique().tolist()
gene_to_groups, group_to_genes, filtered = uniprot_groups_to_genes(uniprot_groups=proteins, databases=["all_reviewed"], use_biomart=False)
genes = list(gene_to_groups.keys())

with open('../user_data/data/background_gene_symbols.txt', 'w') as file:
    # Write each string on a separate line
    for string in genes:
        file.write(string + '\n')

