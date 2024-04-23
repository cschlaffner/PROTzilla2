from __future__ import annotations

from protzilla.data_integration import enrichment_analysis, database_integration
from protzilla.data_integration.enrichment_analysis
from protzilla.steps import Step, StepManager

class DataIntegrationStep(Step):
    section = "data_integration"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs
class EnrichmentAnalysisGOAnalysisWithString(DataIntegrationStep):
    display_name = "GO analysis with STRING"
    operation = "enrichment_analysis"
    method_description = (
        "Online GO analysis using STRING API"
    )

    input_keys = ["proteins_df",
                  "differential_expression_col",
                  "differential_expression_threshold",
                  "gene_sets_restring",
                  "organism",
                  "direction",
                  "background_path",
    ]
    output_keys = ["enrichment_df"]
    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.GO_analysis_with_STRING(**inputs)


class EnrichmentAnalysisGOAnalysisWithEnrichr(DataIntegrationStep):
    display_name = "GO analysis with Enrichr"
    operation = "enrichment_analysis"
    method_description = (
        "Online GO analysis using Enrichr API"
    )
    input_keys = ["protein_df",
                  "differential_expression_col",
                  "differential_expression_threshold",
                  "gene_mapping",
                  "gene_sets_field",
                  "gene_sets_path",
                  "gene_sets_enrichr",
                  "direction",
                  "organism",
                  "background_field",
                  "background_path",
                  "background_number",
                  "background_biomart"
    ]
    output_keys = ["enrichment_df"]
    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.GO_analysis_with_Enrichr(**inputs)

class EnrichmentAnalysisGOAnalysisOffline(DataIntegrationStep):
    display_name = "GO analysis offline"
    operation = "enrichment_analysis"
    method_description = (
        "Offline GO Analysis using a hypergeometric test"
    )
    input_keys = ["protein_df",
                  "differential_expression_col",
                  "differential_expression_threshold",
                  "gene_mapping",
                  "gene_sets_path",
                  "direction",
                  "background_field",
                  "background_path",
                  "background_number",
    ]
    output_keys = ["enrichment_df"]
    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.GO_analysis_offline(**inputs)

class EnrichmentAnalysisWithGSEA(DataIntegrationStep):
    display_name = "GSEA"
    operation = "enrichment_analysis"
    method_description = (
        "Perform gene set enrichment analysis"
    )
    input_keys = ["protein_df",
                  "gene_mapping",
                  "gene_sets_field",
                  "gene_sets_path",
                  "gene_sets_enrichr",
                  "grouping",
                  "group1",
                  "group2",
                  "min_size",
                  "max_size",
                  "number_of_permutations",
                  "permutation_type"
                  "ranking_method",
                  "weighted_score",
                  "metadata_df"
    ]

    output_keys = ["enrichment_df", "ranking"]
    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.gsea(**inputs)

class EnrichmentAnalysisWithPrerankedGSEA(DataIntegrationStep):
    display_name = "GSEA preranked"
    operation = "enrichment_analysis"
    method_description = "Maps proteins to genes and performs GSEA according using provided numerical column for ranking"
    input_keys = ["protein_df",
                  "ranking_column",
                  "ranking_direction",
                  "gene_mapping",
                  "gene_sets_field",
                  "gene_sets_path",
                  "gene_sets_enrichr",
                  "min_size",
                  "max_size",
                  "number_of_permutations",
                  "permutation_type"
                  "weighted_score"
    ]

    output_keys = ["enrichment_df", "ranking"]
    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.gsea_preranked(**inputs)

class DatabaseIntegrationByGeneMapping(DataIntegrationStep):
    display_name = "Gene mapping"
    operation = "database_integration"
    method_description = "Map protein groups to genes"
    input_keys = ["dataframe",
                  "database_names",
                  "use_biomart"
    ]

    output_keys = ["gene_mapping"]
    def method(self, inputs: dict) -> dict:
        return database_integration.gene_mapping(**inputs)

class DatabaseIntegrationByUniprot(DataIntegrationStep):
    display_name = "Uniprot"
    operation = "database_integration"
    method_description = "Add Uniprot data to a dataframe"
    input_keys = ["dataframe",
                  "database_names",
                  "fields"
    ]

    output_keys = ["results_df"]
    def method(self, inputs: dict) -> dict:
        return database_integration.uniprot(**inputs)


