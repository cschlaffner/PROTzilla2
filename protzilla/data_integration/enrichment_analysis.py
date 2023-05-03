from restring import restring
import gseapy as gp

def go_analysis_offline(proteins, protein_sets, background, cutoff):
    ''' dev notes
    proteins: could be list of somewhere filtered proteins, could be dataframe with multiple columns and we just want to use first,
    protein_sets: make upload?
    background:
    cutoff: cutoff for p-value
    '''

    enr = gp.enrich(gene_list=proteins,
                 gene_sets=protein_sets,
                 background=background, #"hsapiens_gene_ensembl",
                 outdir=None,
                 verbose=True)
    df = enr.results
    return {}

def go_analysis_with_enrichr(proteins, protein_sets, organism, background, cutoff):
    return {}

def go_analysis_with_STRING(proteins, protein_sets, organism, background):
    return {}