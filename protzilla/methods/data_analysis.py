from protzilla.data_analysis.classification import random_forest, svm
from protzilla.data_analysis.clustering import (
    expectation_maximisation,
    hierarchical_agglomerative_clustering,
    k_means,
)
from protzilla.data_analysis.differential_expression_anova import anova
from protzilla.data_analysis.differential_expression_linear_model import linear_model
from protzilla.data_analysis.differential_expression_t_test import t_test
from protzilla.data_analysis.dimension_reduction import t_sne, umap
from protzilla.data_analysis.model_evaluation import evaluate_classification_model
from protzilla.data_analysis.plots import (
    clustergram_plot,
    create_volcano_plot,
    prot_quant_plot,
    scatter_plot,
)
from protzilla.data_analysis.protein_graphs import peptides_to_isoform, variation_graph
from protzilla.methods.data_preprocessing import TransformationLog
from protzilla.steps import Plots, Step, StepManager


class DataAnalysisStep(Step):
    section = "data_analysis"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class PlotStep(DataAnalysisStep):
    step = "plot"

    def handle_outputs(self, outputs: dict):
        super().handle_outputs(outputs)
        plots = outputs.pop("plots", [])
        self.plots = Plots(plots)


class DifferentialExpressionANOVA(DataAnalysisStep):
    display_name = "ANOVA"
    operation = "differential_expression"
    method_description = "A function that uses ANOVA to test the difference between two or more groups defined in the clinical data. The ANOVA test is conducted on the level of each protein. The p-values are corrected for multiple testing."

    input_keys = [
        "intensity_df",
        "multiple_testing_correction_method",
        "alpha",
        "log_base",
        "grouping",
        "selected_groups",
        "metadata_df",
    ]
    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "sample_group_df",
        "corrected_alpha",
        "filtered_proteins",
    ]

    def method(self, inputs: dict) -> dict:
        return anova(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")


class DifferentialExpressionTTest(DataAnalysisStep):
    display_name = "t-Test"
    operation = "differential_expression"
    method_description = "A function to conduct a two sample t-test between groups defined in the clinical data. The t-test is conducted on the level of each protein. The p-values are corrected for multiple testing. The fold change is calculated by group2/group1."

    input_keys = [
        "ttest_type",
        "intensity_df",
        "multiple_testing_correction_method",
        "alpha",
        "log_base",
        "grouping",
        "group1",
        "group2",
        "metadata_df",
    ]
    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "t_statistic_df",
        "log2_fold_change_df",
        "corrected_alpha",
        "group1",
        "group2",
    ]

    def method(self, inputs: dict) -> dict:
        return t_test(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")


class DifferentialExpressionLinearModel(DataAnalysisStep):
    display_name = "Linear Model"
    operation = "differential_expression"
    method_description = "A function to fit a linear model using ordinary least squares for each protein. The linear model fits the protein intensities on Y axis and the grouping on X for group1 X=-1 and group2 X=1. The p-values are corrected for multiple testing."

    input_keys = [
        "intensity_df",
        "multiple_testing_correction_method",
        "alpha",
        "log_base",
        "grouping",
        "group1",
        "group2",
        "metadata_df",
    ]
    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "log2_fold_change_df",
        "corrected_alpha",
        "filtered_proteins",
        "group1",
        "group2",
    ]

    def method(self, inputs: dict) -> dict:
        return linear_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")


class PlotVolcano(PlotStep):
    display_name = "Volcano Plot"
    operation = "plot"
    input_keys = [
        "p_values",
        "fc_threshold",
        "alpha",
        "group1",
        "group2",
        "proteins_of_interest",
        "log2_fc",
    ]
    output_keys = []

    def method(self, inputs: dict) -> dict:
        return create_volcano_plot(**inputs)

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

        return inputs


class PlotScatterPlot(PlotStep):
    display_name = "Scatter Plot"
    operation = "plot"
    method_description = "Creates a scatter plot from data. This requires a dimension reduction method to be run first, as the input dataframe should contain only 2 or 3 columns."

    input_keys = [
        "input_df",
        "color_df",
    ]
    output_keys = []

    def method(self, inputs: dict) -> dict:
        return scatter_plot(**inputs)

    # TODO: input
    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "embedded_data", inputs["input_df"]
        )
        inputs["color_df"] = steps.get_step_output(Step, "color_df", inputs["color_df"])
        return inputs


class PlotClustergram(PlotStep):
    display_name = "Clustergram"
    operation = "plot"
    method_description = "Creates a clustergram from data"

    input_keys = [
        "input_df",
        "sample_group_df",
        "flip_axes",
    ]
    output_keys = ["plots"]

    def method(self, inputs: dict) -> dict:
        return clustergram_plot(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class PlotProtQuant(PlotStep):
    display_name = "Protein Quantification Plot"
    operation = "plot"
    method_description = (
        "Creates a line chart for intensity across samples for protein groups"
    )

    input_keys = ["input_df", "protein_group", "similarity_measure", "similarity"]
    output_keys = []

    def method(self, inputs: dict) -> dict:
        return prot_quant_plot(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "protein_df", inputs["input_df"]
        )
        return inputs


class PlotPrecisionRecallCurve(PlotStep):
    display_name = "Precision Recall"
    operation = "plot"
    method_description = "The precision-recall curve shows the tradeoff between precision and recall for different threshold"

    input_keys = [
        # TODO: Input
        "plot_title",
    ]
    # Todo: output_keys

    def method(self, inputs: dict) -> dict:
        return evaluate_classification_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        # TODO: Input
        return inputs


class PlotROC(PlotStep):
    display_name = "Receiver Operating Characteristic curve"
    operation = "plot"
    method_description = "The ROC curve helps assess the model's ability to discriminate between positive and negative classes and determine an optimal threshold for decision making"

    input_keys = [
        # TODO: Input
        "plot_title",
    ]
    # Todo: output_keys

    def method(self, inputs: dict) -> dict:
        return evaluate_classification_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        # Todo: Input
        return inputs


class ClusteringKMeans(DataAnalysisStep):
    display_name = "KMeans"
    operation = "clustering"
    method_description = "Partitions a number of samples in k clusters using k-means"

    input_keys = [
        "input_df",
        "labels_column",
        "positive_label",
        "model_selection",
        "model_selection_scoring",
        "scoring",
        "n_clusters",
        "random_state",
        "init_centroid_strategy",
        "n_init",
        "max_iter",
        "tolerance" "metadata_df",
    ]
    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
        "cluster_centers_df",
    ]

    def method(self, inputs: dict) -> dict:
        return k_means(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class ClusteringExpectationMaximisation(DataAnalysisStep):
    display_name = "Expectation-maximization (EM)"
    operation = "clustering"
    method_description = "A clustering algorithm that seeks to find the maximum likelihood estimates for a mixture of multivariate Gaussian distributions"

    input_keys = [
        "input_df",
        "labels_column",
        "positive_label",
        "model_selection",
        "model_selection_scoring",
        "scoring",
        "n_components",
        "reg_covar",
        "covariance_type",
        "init_params",
        "max_iter",
        "random_state",
        "metadata_df",
    ]
    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
        "cluster_labels_probabilities_df",
    ]

    def method(self, inputs: dict) -> dict:
        return expectation_maximisation(**inputs)

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

    input_keys = [
        "input_df",
        "labels_column",
        "positive_label",
        "model_selection",
        "model_selection_scoring",
        "scoring",
        "n_clusters",
        "metric",
        "linkage",
        "metadata_df",
    ]
    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
    ]

    def method(self, inputs: dict) -> dict:
        return hierarchical_agglomerative_clustering(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class ClassificationRandomForest(DataAnalysisStep):
    display_name = "Random Forest"
    operation = "classification"
    method_description = "A random forest is a meta estimator that fits a number of decision tree classifiers on various sub-samples of the dataset and uses averaging to improve the predictive accuracy and control over-fitting."

    input_keys = [
        "input_df",
        "labels_column",
        "positive_label",
        "test_size",
        "split_stratify",
        "validation_strategy",
        "train_val_split",
        "n_splits",
        "shuffle",
        "n_repeats",
        "random_state_cv",
        "p_samples",
        "scoring",
        "model_selection",
        "model_selection_scoring",
        "criterion",
        "max_depth",
        "random_state",
        "metadata_df",
    ]
    output_keys = [
        "model",
        "model_evaluation_df",
        "X_train_df",
        "X_test_df",
        "y_train_df",
        "y_test_df",
    ]

    def method(self, inputs: dict) -> dict:
        return random_forest(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class ClassificationSVM(DataAnalysisStep):
    display_name = "Support Vector Machine"
    operation = "classification"
    method_description = "A support vector machine constructs a hyperplane or set of hyperplanes in a high- or infinite-dimensional space, which can be used for classification."

    input_keys = [
        "input_df",
        "labels_column",
        "positive_label",
        "test_size",
        "split_stratify",
        "validation_strategy",
        "train_val_split",
        "n_splits",
        "shuffle",
        "n_repeats",
        "random_state_cv",
        "p_samples",
        "scoring",
        "model_selection",
        "model_selection_scoring",
        "C",
        "kernel",
        "tolerance" "random_state",
        "metadata_df",
    ]
    output_keys = [
        "model",
        "model_evaluation_df",
        "X_train_df",
        "X_test_df",
        "y_train_df",
        "y_test_df",
    ]

    def method(self, inputs: dict) -> dict:
        return svm(**inputs)

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

    input_keys = [
        "input_df",
        "n_components",
        "perplexity",
        "metric",
        "random_state",
        "n_iter",
        "n_iter_without_progress",
    ]
    output_keys = ["embedded_data"]

    def method(self, inputs: dict) -> dict:
        return t_sne(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


class DimensionReductionUMAP(DataAnalysisStep):
    display_name = "UMAP"
    operation = "dimension_reduction"
    method_description = "Dimension reduction of a dataframe using UMAP"

    input_keys = [
        "input_df",
        "n_neighbors",
        "n_components",
        "min_dist",
        "metric",
        "random_state",
    ]
    output_keys = ["embedded_data"]

    def method(self, inputs: dict) -> dict:
        return umap(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "protein_df", inputs["input_df"]
        )
        return inputs


class ProteinGraphPeptidesToIsoform(DataAnalysisStep):
    display_name = "Peptides to Isoform"
    operation = "protein_graph"
    method_description = "Create a variation graph (.graphml) for a Protein and map the peptides onto the graph for coverage visualisation. The protein data will be downloaded from https://rest.uniprot.org/uniprotkb/<Protein ID>.txt. Only `Variant`-Features are included in the graph. This, currently, only works with Uniport-IDs and while you are online."

    input_keys = [
        "protein_id",
        "run_name",
        "peptide_df",
        "k" "allowed_mismatches",
    ]
    output_keys = [
        "graph_path" "protein_id",
        "peptide_matches",
        "peptide_mismatches",
        "filtered_blocks",
    ]

    def method(self, inputs: dict) -> dict:
        return peptides_to_isoform(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.peptide_df
        inputs["isoform_df"] = steps.isoform_df
        return inputs


class ProteinGraphVariationGraph(DataAnalysisStep):
    display_name = "Protein Variation Graph"
    operation = "protein_graph"
    method_description = "Create a variation graph (.graphml) for a protein, including variation-features. The protein data will be downloaded from https://rest.uniprot.org/uniprotkb/<Protein ID>.txt. This, currently, only works with Uniport-IDs and while you are online."

    input_keys = [
        "protein_id",
        "run_name",
    ]
    output_keys = [
        "graph_path",
        "filtered_blocks",
    ]

    def method(self, inputs: dict) -> dict:
        return variation_graph(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.peptide_df
        inputs["isoform_df"] = steps.isoform_df
        return inputs
