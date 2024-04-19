from enum import Enum

from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomFileField, CustomChoiceField, CustomFloatField, CustomDecimalField, CustomCharField, CustomMultipleChoiceField


class Direction(Enum):
    up = "Up"
    down = "Down"
    both = "Both"

class GeneSetField(Enum):
    upload_a_file = "Upload a file"
    choose_from_enrichr_options = "Choose from Enrichr options"

class Organism(Enum):
    human = "Human"
    mouse = "Mouse"
    rat = "Rat"
    yeast = "Yeast"
    fly = "Fly"
    fish = "Fish"
    worm = "Worm"

class GOAnalysisWithEnrichrBackgroundField(Enum):
    upload_a_file = "Upload a file (recommended)"
    choose_biomart_dataset = "Choose Biomart dataset"
    number_of_expressed_genes = "Specify number of expressed genes (not recommended)"
    all_genes = "Use all genes in the gene set"


class EnrichmentAnalysisGOAnalysisWithStringForm(MethodForm):
    #Todo: protein_df
    #Todo: differential_expression_col
    differential_expression_threshold = CustomDecimalField(
        label="Threshold for differential expression: Proteins with values > threshold are upregulated, proteins values < threshold downregulated. If \"log\" is in the name of differential_expression_col, threshold is applied symmetrically: e.g. log2_fold_change > threshold is upregulated, if log2_fold_change < -threshold downregulated",
        min_value=0,
        max_value=4294967295,
        default=0
    )
    #Todo: gene_sets_restring
    organism = CustomDecimalField(
        label="Organism / NCBI taxon identifiers (e.g. Human is 9606)",
        default=9606
    )
    direction = CustomChoiceField(
        choices=Direction,
        label="Direction of the analysis",
        default="Both"
    )
    background_path = CustomFileField(
        label="Background set (no upload = entire proteome), UniProt IDs (one per line, txt or csv)",
        default=None,
    )


class EnrichmentAnalysisGOAnalysisWithEnrichrForm(MethodForm):
    #Todo: protein_df
    #Todo: differential_expression_col
    differential_expression_threshold = CustomDecimalField(
        label="Threshold for differential expression: Proteins with values > threshold are upregulated, proteins values < threshold downregulated. If \"log\" is in the name of differential_expression_col, threshold is applied symmetrically: e.g. log2_fold_change > threshold is upregulated, if log2_fold_change < -threshold downregulated",
        min_value=0,
        max_value=4294967295,
        default=0
    )
    #Todo: gene_mapping
    gene_sets_field = CustomChoiceField(
        choices=GeneSetField,
        label="Gene sets",
        default="Choose from Enrichr options"
        #Todo: Dynamic parameters
    )
    #Todo: gene_sets_enrichr
    direction = CustomChoiceField(
        choices=Direction,
        label="Direction of the analysis",
        default="Both"
    )
    organism = CustomChoiceField(
        choices=Organism,
        label="Organism",
        default="Human"
    )
    background_field = CustomChoiceField(
        choices=GOAnalysisWithEnrichrBackgroundField,
        label="Background",
        default="Upload a file (recommended)"
        #Todo: Dynamic parameters
    )
    background_path = CustomFileField(
        label="Background set with uppercase gene symbols (one gene per line, csv or txt)",
        default=None,
    )
    background_number = CustomDecimalField(
        label="Number of expressed genes in the background",
        min_value=1,
        max_value=4294967295,
        step_size=1,
        default=None
    )
    background_bio_mart = CustomChoiceField(
        #Todo: biomart_datasets
    )