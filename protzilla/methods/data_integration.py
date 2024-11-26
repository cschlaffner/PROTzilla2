from __future__ import annotations

from protzilla.data_integration import (
    database_integration,
    di_plots,
    enrichment_analysis,
)
from protzilla.steps import Plots, Step, StepManager


class DataIntegrationStep(Step):
    section = "data_integration"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class PlotStep(DataIntegrationStep):
    operation = "plot"

    def handle_outputs(self, outputs: dict):
        super().handle_outputs(outputs)
        plots = outputs["plots"] if "plots" in outputs else []
        self.plots = Plots(plots)


class EnrichmentAnalysisGOAnalysisWithString(DataIntegrationStep):
    display_name = "GO analysis with STRING"
    operation = "enrichment_analysis"
    method_description = "Online GO analysis using STRING API"

    input_keys = [
        "proteins_df",
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

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["proteins_df"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["protein_df"]
        )  # TODO name fix
        if (
            inputs.get("proteins_df") is None
            or not "log2_fold_change" in inputs["proteins_df"].columns
        ):
            raise ValueError(
                "No data found to be enriched. Please do a differential expression analysis first or select the corrent step"
            )
        inputs["differential_expression_col"] = "log2_fold_change"

        return inputs


class EnrichmentAnalysisGOAnalysisWithEnrichr(DataIntegrationStep):
    display_name = "GO analysis with Enrichr"
    operation = "enrichment_analysis"
    method_description = "Online GO analysis using Enrichr API"
    input_keys = [
        "proteins_df",
        "differential_expression_col",
        "differential_expression_threshold",
        "gene_mapping_df",
        "gene_sets_field",
        "gene_sets_path",
        "gene_sets_enrichr",
        "direction",
        "organism",
        "background_field",
        "background_path",
        "background_number",
        "background_biomart",
    ]
    output_keys = ["enrichment_df"]

    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.GO_analysis_with_Enrichr(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["proteins_df"] = steps.get_step_output(
            Step,
            "differentially_expressed_proteins_df",
            inputs["protein_df_step_instance"],
        )  # TODO name fix
        if (
            inputs.get("proteins_df") is None
            or not "log2_fold_change" in inputs["proteins_df"].columns
        ):
            raise ValueError(
                "No data found to be enriched. Please do a differential expression analysis first or select the corrent step"
            )
        inputs["differential_expression_col"] = "log2_fold_change"
        inputs["gene_mapping_df"] = steps.get_step_output(
            Step, "gene_mapping_df", inputs["gene_mapping_step_instance"]
        )
        return inputs


class EnrichmentAnalysisGOAnalysisOffline(DataIntegrationStep):
    display_name = "GO analysis offline"
    operation = "enrichment_analysis"
    method_description = "Offline GO Analysis using a hypergeometric test"
    input_keys = [
        "protein_df",
        "differential_expression_col",
        "differential_expression_threshold",
        "gene_mapping",  # TODO adjust this method to use the gene_mapping_df from gene_mapping
        "gene_sets_path",
        "direction",
        "background_field",
        "background_path",
        "background_number",
    ]
    output_keys = ["enrichment_df"]

    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.GO_analysis_offline(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["proteins_df"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["protein_df"]
        )  # TODO name fix
        if (
            inputs.get("proteins_df") is None
            or not "log2_fold_change" in inputs["proteins_df"].columns
        ):
            raise ValueError(
                "No data found to be enriched. Please do a differential expression analysis first or select the corrent step"
            )
        inputs["differential_expression_col"] = "log2_fold_change"

        return inputs


class EnrichmentAnalysisWithGSEA(DataIntegrationStep):
    display_name = "GSEA"
    operation = "enrichment_analysis"
    method_description = "Perform gene set enrichment analysis"
    input_keys = [
        "protein_df",
        "gene_mapping_df",
        "gene_sets_field",
        "gene_sets_path",
        "gene_sets_enrichr",
        "grouping",
        "group1",
        "group2",
        "min_size",
        "max_size",
        "number_of_permutations",
        "permutation_type",
        "ranking_method",
        "weighted_score",
    ]

    output_keys = ["enrichment_df", "ranking"]

    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.gsea(**inputs)


class EnrichmentAnalysisWithPrerankedGSEA(DataIntegrationStep):
    display_name = "GSEA preranked"
    operation = "enrichment_analysis"
    method_description = "Maps proteins to genes and performs GSEA according using provided numerical column for ranking"
    input_keys = [
        "protein_df",
        "ranking_column",
        "ranking_direction",
        "gene_mapping_df",
        "gene_sets_field",
        "gene_sets_path",
        "gene_sets_enrichr",
        "min_size",
        "max_size",
        "number_of_permutations",
        "permutation_type",
        "weighted_score",
        "seed",
        "threads",
    ]

    output_keys = ["enrichment_df", "ranking"]

    def method(self, inputs: dict) -> dict:
        return enrichment_analysis.gsea_preranked(**inputs)


class DatabaseIntegrationByGeneMapping(DataIntegrationStep):
    display_name = "Gene mapping"
    operation = "database_integration"
    method_description = "Map protein groups to genes"
    input_keys = ["dataframe", "database_names", "use_biomart"]

    output_keys = ["gene_mapping_df", "filtered_protein_ids"]

    def method(self, inputs: dict) -> dict:
        return database_integration.gene_mapping(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["dataframe"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["dataframe"]
        )
        return inputs


class DatabaseIntegrationByUniprot(DataIntegrationStep):
    display_name = "Uniprot"
    operation = "database_integration"
    method_description = "Add Uniprot data to a dataframe"
    input_keys = ["dataframe", "database_names", "fields"]

    output_keys = ["results_df"]

    def method(self, inputs: dict) -> dict:
        return database_integration.add_uniprot_data(**inputs)


class PlotGOEnrichmentBarPlot(PlotStep):
    display_name = "Bar plot for GO enrichment analysis"
    operation = "plot"
    method_description = "Creates a bar plot from GO enrichment data"
    input_keys = [
        "input_df",
        "gene_sets",
        "value",
        "top_terms",
        "cutoff",
        "title",
        "figsize",
    ]
    # TODO: input figsize optional?
    output_keys = ["plots"]

    def method(self, inputs: dict) -> dict:
        return di_plots.GO_enrichment_bar_plot(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs[
            "figsize"
        ] = None  # TODO this should not have to be done manually if the parameter is optional
        inputs["input_df"] = steps.get_step_output(
            Step, "enrichment_df", inputs["input_df_step_instance"]
        )
        return inputs


class PlotGOEnrichmentDotPlot(PlotStep):
    display_name = "Dot plot for GO enrichment analysis (offline & with Enrichr) "
    operation = "plot"
    method_description = "Creates a categorical scatter plot from GO enrichment data"
    input_keys = [
        "x_axis_type",
        "gene_sets",
        "top_terms",
        "cutoff",
        "title",
        "rotate_x_labels",
        "show_ring",
        "dot_size",
        "figsize",
    ]
    output_keys = ["plots"]

    def method(self, inputs: dict) -> dict:
        return di_plots.GO_enrichment_dot_plot(**inputs)


class PlotGSEADotPlot(PlotStep):
    display_name = "Dot plot for (pre-ranked) GSEA"
    operation = "plot"
    method_description = "Creates a categorical scatter plot from GSEA data"
    input_keys = [
        "cutoff",
        "gene_sets",
        "dot_color_value",
        "x_axis_value",
        "title",
        "show_ring",
        "dot_size",
        "remove_library_names",
        "figsize",
    ]
    output_keys = ["plots"]

    def method(self, inputs: dict) -> dict:
        return di_plots.gsea_dot_plot(**inputs)


class PlotGSEAEnrichmentPlot(PlotStep):
    display_name = "Enrichment plot for (pre-ranked) GSEA"
    operation = "plot"
    method_description = "Creates an enrichment plot from (pre-ranked) GSEA data with the enrichment score, ranked_metric, gene rank and hits"
    input_keys = [
        "term_dict",
        "term_name",
        "ranking",
        "pos_pheno_label",
        "neg_pheno_label",
        "figsize",
    ]
    output_keys = ["plots"]

    def method(self, inputs: dict) -> dict:
        return di_plots.gsea_enrichment_plot(**inputs)
