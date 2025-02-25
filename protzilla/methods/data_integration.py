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

    def handle_calc_outputs(self, outputs: dict):
        super().handle_calc_outputs(outputs)
        plots = outputs["plots"] if "plots" in outputs else []
        self.plots = Plots(plots)


class EnrichmentAnalysisGOAnalysisWithString(DataIntegrationStep):
    display_name = "GO analysis with STRING"
    operation = "enrichment_analysis"
    method_description = "Online GO analysis using STRING API"

    output_keys = ["enrichment_df"]

    calc_method = staticmethod(enrichment_analysis.GO_analysis_with_STRING)

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
    output_keys = ["enrichment_df"]

    calc_method = staticmethod(enrichment_analysis.GO_analysis_with_Enrichr)

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

    output_keys = ["enrichment_df"]

    calc_method = staticmethod(enrichment_analysis.GO_analysis_offline)
    # TODO gene_mapping - adjust this method to use the gene_mapping_df from gene_mapping

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

    output_keys = ["enrichment_df", "ranking"]

    calc_method = staticmethod(enrichment_analysis.gsea)


class EnrichmentAnalysisWithPrerankedGSEA(DataIntegrationStep):
    display_name = "GSEA preranked"
    operation = "enrichment_analysis"
    method_description = "Maps proteins to genes and performs GSEA according using provided numerical column for ranking"

    output_keys = ["enrichment_df", "ranking"]

    calc_method = staticmethod(enrichment_analysis.gsea_preranked)


class DatabaseIntegrationByGeneMapping(DataIntegrationStep):
    display_name = "Gene mapping"
    operation = "database_integration"
    method_description = "Map protein groups to genes"

    output_keys = ["gene_mapping_df", "filtered_protein_ids"]

    calc_method = staticmethod(database_integration.gene_mapping)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["dataframe"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["dataframe"]
        )
        return inputs


class DatabaseIntegrationByUniprot(DataIntegrationStep):
    display_name = "Uniprot"
    operation = "database_integration"
    method_description = "Add Uniprot data to a dataframe"

    output_keys = ["results_df"]

    calc_method = staticmethod(database_integration.add_uniprot_data)


class PlotGOEnrichmentBarPlot(PlotStep):
    display_name = "Bar plot for GO enrichment analysis"
    operation = "plot"
    method_description = "Creates a bar plot from GO enrichment data"

    output_keys = ["plots"]

    calc_method = staticmethod(di_plots.GO_enrichment_bar_plot)

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

    output_keys = ["plots"]

    calc_method = staticmethod(di_plots.GO_enrichment_dot_plot)


class PlotGSEADotPlot(PlotStep):
    display_name = "Dot plot for (pre-ranked) GSEA"
    operation = "plot"
    method_description = "Creates a categorical scatter plot from GSEA data"

    output_keys = ["plots"]

    calc_method = staticmethod(di_plots.gsea_dot_plot)


class PlotGSEAEnrichmentPlot(PlotStep):
    display_name = "Enrichment plot for (pre-ranked) GSEA"
    operation = "plot"
    method_description = "Creates an enrichment plot from (pre-ranked) GSEA data with the enrichment score, ranked_metric, gene rank and hits"

    output_keys = ["plots"]

    calc_method = staticmethod(di_plots.gsea_enrichment_plot)
