import logging

from protzilla.data_analysis.classification import random_forest, svm
from protzilla.data_analysis.clustering import (
    expectation_maximisation,
    hierarchical_agglomerative_clustering,
    k_means,
)
from protzilla.data_analysis.differential_expression_anova import anova
from protzilla.data_analysis.differential_expression_kruskal_wallis import kruskal_wallis_test_on_ptm_data, \
    kruskal_wallis_test_on_intensity_data
from protzilla.data_analysis.differential_expression_linear_model import linear_model
from protzilla.data_analysis.differential_expression_mann_whitney import (
    mann_whitney_test_on_intensity_data, mann_whitney_test_on_ptm_data)
from protzilla.data_analysis.differential_expression_t_test import t_test
from protzilla.data_analysis.dimension_reduction import t_sne, umap
from protzilla.data_analysis.ptm_analysis import ptms_per_sample, \
    ptms_per_protein_and_sample, select_peptides_of_protein
from protzilla.data_analysis.model_evaluation import evaluate_classification_model
from protzilla.data_analysis.plots import (
    clustergram_plot,
    create_volcano_plot,
    prot_quant_plot,
    scatter_plot,
)
from protzilla.data_analysis.protein_graphs import peptides_to_isoform, variation_graph
from protzilla.data_analysis.ptm_analysis import (
    select_peptides_of_protein,
    ptms_per_protein_and_sample,
    ptms_per_sample,
)
from protzilla.data_analysis.ptm_quantification import flexiquant_lf
from protzilla.methods.data_preprocessing import TransformationLog
from protzilla.steps import Plots, Step, StepManager


class DataAnalysisStep(Step):
    section = "data_analysis"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class DifferentialExpressionANOVA(DataAnalysisStep):
    display_name = "ANOVA"
    operation = "differential_expression"
    method_description = "A function that uses ANOVA to test the difference between two or more groups defined in the clinical data. The ANOVA test is conducted on the level of each protein. The p-values are corrected for multiple testing."

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "sample_group_df",
        "corrected_alpha",
        "filtered_proteins",
    ]

    calc_method = staticmethod(anova)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionTTest(DataAnalysisStep):
    display_name = "t-Test"
    operation = "differential_expression"
    method_description = "A function to conduct a two sample t-test between groups defined in the clinical data. The t-test is conducted on the level of each protein. The p-values are corrected for multiple testing. The fold change is calculated by group2/group1."

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "t_statistic_df",
        "log2_fold_change_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(t_test)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionLinearModel(DataAnalysisStep):
    display_name = "Linear Model"
    operation = "differential_expression"
    method_description = "A function to fit a linear model using ordinary least squares for each protein. The linear model fits the protein intensities on Y axis and the grouping on X for group1 X=-1 and group2 X=1. The p-values are corrected for multiple testing."

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "log2_fold_change_df",
        "corrected_alpha",
        "filtered_proteins",
    ]

    calc_method = staticmethod(linear_model)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionMannWhitneyOnIntensity(DataAnalysisStep):
    display_name = "Mann-Whitney Test"
    operation = "differential_expression"
    method_description = ("A function to conduct a Mann-Whitney U test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "u_statistic_df",
        "log2_fold_change_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(mann_whitney_test_on_intensity_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        if steps.get_step_output(Step, "protein_df", inputs["protein_df"]) is not None:
            inputs["protein_df"] = steps.get_step_output(Step, "protein_df", inputs["protein_df"])
        inputs["metadata_df"] = steps.metadata_df
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        return inputs


class DifferentialExpressionMannWhitneyOnPTM(DataAnalysisStep):
    display_name = "Mann-Whitney Test"
    operation = "Peptide analysis"
    method_description = ("A function to conduct a Mann-Whitney U test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_ptm_df",
        "significant_ptm_df",
        "corrected_p_values_df",
        "u_statistic_df",
        "log2_fold_change_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(mann_whitney_test_on_ptm_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ptm_df"] = steps.get_step_output(Step, "ptm_df", inputs["ptm_df"])
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionKruskalWallisOnIntensity(DataAnalysisStep):
    display_name = "Kruskal-Wallis Test"
    operation = "differential_expression"
    method_description = ("A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(kruskal_wallis_test_on_intensity_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ptm_df"] = steps.get_step_output(Step, "ptm_df", inputs["ptm_df"])
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionKruskalWallisOnIntensity(DataAnalysisStep):
    display_name = "Kruskal-Wallis Test"
    operation = "differential_expression"
    method_description = ("A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(kruskal_wallis_test_on_intensity_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(Step, "protein_df", inputs["protein_df"])
        inputs["metadata_df"] = steps.metadata_df
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        return inputs


class DifferentialExpressionKruskalWallisOnPTM(DataAnalysisStep):
    display_name = "Kruskal-Wallis Test"
    operation = "Peptide analysis"
    method_description = ("A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_ptm_df",
        "significant_ptm_df",
        "corrected_p_values_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(kruskal_wallis_test_on_ptm_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ptm_df"] = steps.get_step_output(Step, "ptm_df", inputs["ptm_df"])
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class PlotVolcano(DataAnalysisStep):
    display_name = "Volcano Plot"
    operation = "plot"
    method_description = ("Plots the results of a differential expression analysis in a volcano plot. The x-axis shows "
                          "the log2 fold change and the y-axis shows the -log10 of the corrected p-values. The user "
                          "can define a fold change threshold and an alpha level to highlight significant items.")
    
    output_keys = []

    plot_method = staticmethod(create_volcano_plot)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["p_values"] = steps.get_step_output(
            Step, "corrected_p_values_df", inputs["input_dict"]
        )

        step = next(
            s for s in steps.all_steps if s.instance_identifier == inputs["input_dict"]
        )
        inputs["alpha"] = step.inputs["alpha"]
        inputs["group1"] = step.inputs["group1"]
        inputs["group2"] = step.inputs["group2"]
        inputs["log2_fc"] = steps.get_step_output(
            Step, "log2_fold_change_df", inputs["input_dict"]
        )

        if step.operation == "differential_expression":
            inputs["item_type"] = "Protein ID"
        elif step.operation == "Peptide analysis":
            inputs["item_type"] = "PTM"

        return inputs


class PlotScatterPlot(DataAnalysisStep):
    display_name = "Scatter Plot"
    operation = "plot" 
    method_description = "Creates a scatter plot from data. This requires a dimension reduction method to be run first, as the input dataframe should contain only 2 or 3 columns."

    plot_method = staticmethod(scatter_plot)

    # TODO: input
    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "embedded_data", inputs["input_df"]
        )
        inputs["color_df"] = steps.get_step_output(Step, "color_df", inputs["color_df"])
        return inputs


class PlotClustergram(DataAnalysisStep):
    display_name = "Clustergram"
    operation = "plot"
    method_description = "Creates a clustergram from data"

    plot_method = staticmethod(clustergram_plot)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class PlotProtQuant(DataAnalysisStep):
    display_name = "Protein Quantification Plot"
    operation = "plot"
    method_description = (
        "Creates a line chart for intensity across samples for protein groups"
    )

    plot_method = staticmethod(prot_quant_plot)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "protein_df", inputs["input_df"]
        )
        return inputs


class PlotPrecisionRecallCurve(DataAnalysisStep):
    display_name = "Precision Recall"
    operation = "plot"
    method_description = "The precision-recall curve shows the tradeoff between precision and recall for different threshold"

    # Todo: output_keys

    calc_method = staticmethod(evaluate_classification_model)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        # TODO: Input
        return inputs


class PlotROC(DataAnalysisStep):
    display_name = "Receiver Operating Characteristic curve"
    operation = "plot"
    method_description = "The ROC curve helps assess the model's ability to discriminate between positive and negative classes and determine an optimal threshold for decision making"

    # Todo: output_keys

    calc_method = staticmethod(evaluate_classification_model)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        # Todo: Input
        return inputs


class ClusteringKMeans(DataAnalysisStep):
    display_name = "KMeans"
    operation = "clustering"
    method_description = "Partitions a number of samples in k clusters using k-means"

    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
        "cluster_centers_df",
    ]

    calc_method = staticmethod(k_means)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class ClusteringExpectationMaximisation(DataAnalysisStep):
    display_name = "Expectation-maximization (EM)"
    operation = "clustering"
    method_description = "A clustering algorithm that seeks to find the maximum likelihood estimates for a mixture of multivariate Gaussian distributions"

    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
        "cluster_labels_probabilities_df",
    ]

    calc_method = staticmethod(expectation_maximisation)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class ClusteringHierarchicalAgglomerative(DataAnalysisStep):
    display_name = "Hierarchical Agglomerative Clustering"
    operation = "clustering"
    method_description = (
        "Performs hierarchical clustering utilizing a bottom-up approach"
    )

    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
    ]

    calc_method = staticmethod(hierarchical_agglomerative_clustering)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class ClassificationRandomForest(DataAnalysisStep):
    display_name = "Random Forest"
    operation = "classification"
    method_description = "A random forest is a meta estimator that fits a number of decision tree classifiers on various sub-samples of the dataset and uses averaging to improve the predictive accuracy and control over-fitting."

    output_keys = [
        "model",
        "model_evaluation_df",
        "X_train_df",
        "X_test_df",
        "y_train_df",
        "y_test_df",
    ]

    calc_method = staticmethod(random_forest)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class ClassificationSVM(DataAnalysisStep):
    display_name = "Support Vector Machine"
    operation = "classification"
    method_description = "A support vector machine constructs a hyperplane or set of hyperplanes in a high- or infinite-dimensional space, which can be used for classification."

    output_keys = [
        "model",
        "model_evaluation_df",
        "X_train_df",
        "X_test_df",
        "y_train_df",
        "y_test_df",
    ]

    calc_method = staticmethod(svm)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class ModelEvaluationClassificationModel(DataAnalysisStep):
    display_name = "Evaluation of classification models"
    operation = "model_evaluation"
    method_description = "Assessing an already trained classification model on separate testing data using widely used scoring metrics"

    input_keys = [
        # Todo: input_dict
        "scoring",
    ]
    output_keys = ["scores_df"]

    def method(self, inputs: dict) -> dict:
        return evaluate_classification_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class DimensionReductionTSNE(DataAnalysisStep):
    display_name = "t-SNE"
    operation = "dimension_reduction"
    method_description = "Dimension reduction of a dataframe using t-SNE"

    output_keys = ["embedded_data"]

    calc_method = staticmethod(t_sne)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class DimensionReductionUMAP(DataAnalysisStep):
    display_name = "UMAP"
    operation = "dimension_reduction"
    method_description = "Dimension reduction of a dataframe using UMAP"

    output_keys = ["embedded_data"]

    calc_method = staticmethod(umap)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "protein_df", inputs["input_df"]
        )
        return inputs


class ProteinGraphPeptidesToIsoform(DataAnalysisStep):
    display_name = "Peptides to Isoform"
    operation = "protein_graph"
    method_description = "Create a variation graph (.graphml) for a Protein and map the peptides onto the graph for coverage visualisation. The protein data will be downloaded from https://rest.uniprot.org/uniprotkb/<Protein ID>.txt. Only `Variant`-Features are included in the graph. This, currently, only works with Uniport-IDs and while you are online."

    output_keys = [
        "graph_path",
        "protein_id",
        "peptide_matches",
        "peptide_mismatches",
        "filtered_blocks",
    ]

    calc_method = staticmethod(peptides_to_isoform)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.peptide_df
        inputs["isoform_df"] = steps.isoform_df
        return inputs


class ProteinGraphVariationGraph(DataAnalysisStep):
    display_name = "Protein Variation Graph"
    operation = "protein_graph"
    method_description = "Create a variation graph (.graphml) for a protein, including variation-features. The protein data will be downloaded from https://rest.uniprot.org/uniprotkb/<Protein ID>.txt. This, currently, only works with Uniport-IDs and while you are online."

    output_keys = [
        "graph_path",
        "filtered_blocks",
    ]

    calc_method = staticmethod(variation_graph)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.peptide_df
        inputs["isoform_df"] = steps.isoform_df
        return inputs


class FLEXIQuantLF(DataAnalysisStep):
    display_name = "FLEXIQuant-LF"
    operation = "modification_quantification"
    method_description = "FLEXIQuant-LF is an unbiased, label-free computational tool to indirectly detect modified peptides and to quantify the degree of modification based solely on the unmodified peptide species."

    output_keys = [
        "raw_scores",
        "RM_scores",
        "diff_modified",
        "removed_peptides",
    ]

    plot_method = staticmethod(flexiquant_lf)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )

        inputs["metadata_df"] = steps.metadata_df


class SelectPeptidesForProtein(DataAnalysisStep):
    display_name = "Select Peptides of Protein"
    operation = "Peptide analysis"
    method_description = "Filter peptides for the a selected Protein of Interest from a peptide dataframe"

    output_keys = [
        "peptide_df",
    ]

    calc_method = staticmethod(select_peptides_of_protein)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )

        inputs["metadata_df"] = steps.metadata_df

        if inputs["auto_select"]:
            significant_proteins = (
                steps.get_step_output(DataAnalysisStep, "significant_proteins_df", inputs["protein_list"]))
            index_of_most_significant_protein = significant_proteins['corrected_p_value'].idxmin()
            most_significant_protein = significant_proteins.loc[index_of_most_significant_protein]
            inputs["protein_id"] = [most_significant_protein["Protein ID"]]
            self.messages.append({
                "level": logging.INFO,
                "msg":
                    f"Selected the most significant Protein: {most_significant_protein['Protein ID']}, "
                    f"from {inputs['protein_list']}"
            })

        return inputs


class PTMsPerSample(DataAnalysisStep):
    display_name = "PTMs per Sample"
    operation = "Peptide analysis"
    method_description = ("Analyze the post-translational modifications (PTMs) of a single protein of interest. "
                          "This function requires a peptide dataframe with PTM information.")

    output_keys = [
        "ptm_df",
    ]

    calc_method = staticmethod(ptms_per_sample)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )
        return inputs


class PTMsProteinAndPerSample(DataAnalysisStep):
    display_name = "PTMs per Sample and Protein"
    operation = "Peptide analysis"
    method_description = ("Analyze the post-translational modifications (PTMs) of all Proteins. "
                          "This function requires a peptide dataframe with PTM information.")

    output_keys = [
        "ptm_df",
    ]

    calc_method = staticmethod(ptms_per_protein_and_sample)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )
        return inputs