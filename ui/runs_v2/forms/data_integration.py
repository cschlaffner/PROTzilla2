from enum import Enum

from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomFileField, CustomChoiceField, CustomFloatField, CustomDecimalField, CustomCharField, \
    CustomMultipleChoiceField, CustomBooleanField


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


class GroupingField(Enum):
    group1 = "Group 1"
    group2 = "Group 2"


class PermutationTypeField(Enum):
    phenotype = "Phenotype"
    gene_set = "Gene Set"


class RankingMethodField(Enum):
    log2_ratio_of_classes = "Log2 Ratio of classes",
    signal_to_noise = "Signal to noise",
    t_test = "t-Test",
    ratio_of_classes = "Ratio of classes",
    diff_of_classes = "Difference of classes"


class RankingDirectionField(Enum):
    ascending = "ascending"
    descending = "descending"


class GOAnalysisWithEnrichrBackgroundField(Enum):
    upload_a_file = "Upload a file (recommended)"
    choose_biomart_dataset = "Choose Biomart dataset"
    number_of_expressed_genes = "Specify number of expressed genes (not recommended)"
    all_genes = "Use all genes in the gene set"


class EnrichmentAnalysisGOAnalysisWithStringForm(MethodForm):
    # Todo: protein_df
    # Todo: differential_expression_col
    differential_expression_threshold = CustomDecimalField(
        label="Threshold for differential expression: Proteins with values > threshold are upregulated, proteins "
              "values < threshold downregulated. If \"log\" is in the name of differential_expression_col, "
              "threshold is applied symmetrically: e.g. log2_fold_change > threshold is upregulated, "
              "if log2_fold_change < -threshold downregulated",
        min_value=0,
        max_value=4294967295,
        default=0
    )
    # Todo: gene_sets_restring
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
    # Todo: protein_df
    # Todo: differential_expression_col
    differential_expression_threshold = CustomDecimalField(
        label="Threshold for differential expression: Proteins with values > threshold are upregulated, proteins "
              "values < threshold downregulated. If \"log\" is in the name of differential_expression_col, "
              "threshold is applied symmetrically: e.g. log2_fold_change > threshold is upregulated, "
              "if log2_fold_change < -threshold downregulated",
        min_value=0,
        max_value=4294967295,
        default=0
    )
    # Todo: gene_mapping
    gene_sets_field = CustomChoiceField(
        choices=GeneSetField,
        label="Gene sets",
        default="Choose from Enrichr options"
        # Todo: Dynamic parameters
    )
    # Todo: gene_sets_enrichr
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
        # Todo: Dynamic parameters
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
        # Todo: biomart_datasets
    )


class EnrichmentAnalysisGOAnalysisOfflineForm(MethodForm):
    # Todo: protein_df
    # Todo: differential_expression_col
    differential_expression_threshold = CustomDecimalField(
        label="Threshold for differential expression: proteins with values > threshold are upregulated, proteins "
              "values < threshold downregulated. If \"log\" is in the name of differential_expression_col, "
              "threshold is applied symmetrically: e.g. log2_fold_change > threshold is upregulated, "
              "if log2_fold_change < -threshold downregulated",
        min_value=0,
        max_value=4294967295,
        default=0
    )
    # Todo: gene_mapping
    gene_sets_path = CustomFileField(label="Upload gene sets with uppercase gene symbols (any of the following file "
                                           "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                                           "followed by tab-separated list of proteins | .csv (one set per line): "
                                           "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                                           "SetName2: [Gene2, Gene3, ...]})",
                                     default=None
                                     )
    direction = CustomChoiceField(
        choices=Direction,
        label="Direction of the analysis",
        default="Both"
    )
    background_field = CustomChoiceField(
        choices=GOAnalysisWithEnrichrBackgroundField,
        label="How do you want to provide the background set? This parameter works only for uploaded gene sets and "
              "will otherwise be ignored!",
        default="Upload a file (recommended)"
        # Todo: Dynamic parameters
    )
    background_path = CustomFileField(
        label="Background set with uppercase gene symbols (one protein per line, csv or txt)",
        default=None,
    )
    background_number = CustomDecimalField(
        label="Number of expressed genes",
        min_value=1,
        max_value=4294967295,
        step_size=1,
        default=None
    )


class EnrichmentAnalysisWithGSEAForm(MethodForm):
    # Todo: protein_df
    # Todo: gene_mapping
    gene_sets_field = CustomChoiceField(
        choices=GeneSetField,
        label="How do you want to provide the gene sets? (reselect to show dynamic fields)",
        default="Choose from Enrichr options"
        # Todo: Dynamic parameters
    )
    gene_sets_path = CustomFileField(label="Upload gene sets with uppercase gene symbols (any of the following file "
                                           "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                                           "followed by tab-separated list of proteins | .csv (one set per line): "
                                           "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                                           "SetName2: [Gene2, Gene3, ...]})",
                                     default=None
                                     )
    # Todo: gene_sets_enrichr
    grouping = CustomChoiceField(
        choices=GroupingField,
        label="Grouping from metadata",
        default=None
        # Todo: Dynamic parameters
    )
    # Todo: add dynamic filling to group1, group2
    group1 = CustomChoiceField(choices=[],
                               label="Group1",
                               default=None)

    group2 = CustomChoiceField(choices=[],
                               label="Group2",
                               default=None)

    min_size = CustomDecimalField(label="Minimum number of genes from gene set also in data",
                                  default=15)

    max_size = CustomDecimalField(label="Maximum number of genes from gene set also in data",
                                  default=500)

    number_of_permutations = CustomDecimalField(label="number_of_permutations",
                                                default=1000)

    permutation_type = CustomChoiceField(choices=PermutationTypeField,
                                         label="Permutation type (if samples >=15 set to phenotype)",
                                         default="phenotype")

    ranking_method = CustomChoiceField(choices=RankingMethodField,
                                       label="Method to calculate correlation or ranking",
                                       default="signal_to_noise")

    weighted_score = CustomFloatField(label="Weighted score for the enrichment score calculation, recommended values: "
                                            "0, 1, 1.5 or 2",
                                      default=1)
    # Todo: metadata_df


class EnrichmentAnalysisWithPrerankedGSEAForm(MethodForm):
    # Todo: protein_df
    # Todo: ranking_column
    ranking_direction = CustomChoiceField(choices=RankingDirectionField,
                                          label="Sort the ranking column (ascending - smaller values are better, "
                                                "descending - larger values are better)",
                                          default="ascending")
    # Todo: gene_mapping
    gene_sets_field = CustomChoiceField(
        choices=GeneSetField,
        label="How do you want to provide the gene sets? (reselect to show dynamic fields)",
        default="Choose from Enrichr options"
        # Todo: Dynamic parameters
    )
    gene_sets_path = CustomFileField(label="Upload gene sets with uppercase gene symbols (any of the following file "
                                           "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                                           "followed by tab-separated list of proteins | .csv (one set per line): "
                                           "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                                           "SetName2: [Gene2, Gene3, ...]})",
                                     default=None
                                     )
    # Todo: gene_sets_enrichr
    min_size = CustomDecimalField(label="Minimum number of genes from gene set also in data",
                                  default=15)

    max_size = CustomDecimalField(label="Maximum number of genes from gene set also in data",
                                  default=500)

    number_of_permutations = CustomDecimalField(label="number_of_permutations",
                                                default=1000)

    permutation_type = CustomChoiceField(choices=PermutationTypeField,
                                         label="Permutation type (if samples >=15 set to phenotype)",
                                         default="phenotype")

    ranking_method = CustomChoiceField(choices=RankingMethodField,
                                       label="Method to calculate correlation or ranking",
                                       default="signal_to_noise")

    weighted_score = CustomFloatField(label="Weighted score for the enrichment score calculation, recommended values: "
                                            "0, 1, 1.5 or 2",
                                      default=1)


class DatabaseIntegrationByGeneMappingForm(MethodForm):
    # Todo: gene_mapping
    # Todo: Add dynamic fill for database name
    database_name = CustomMultipleChoiceField(choices=[],
                                              label="Uniprot databases (offline)",
                                              )
    use_biomart = CustomBooleanField(label="Use Biomart after Uniprot databases (online)",
                                     default=False)


class DatabaseIntegrationByUniprotForm(MethodForm):
    # Todo: uniprot
    # Todo: Add dynamic fill for database name and fields
    database_name = CustomChoiceField(choices=[],
                                      label="Uniprot databases (offline)",
                                      )
    fields = CustomMultipleChoiceField(choices=[],
                                       label="Fields"
                                       )

