from protzilla.data_analysis.differential_expression_t_test import t_test
from protzilla.data_analysis.differential_expression_anova import anova
from protzilla.data_analysis.differential_expression_linear_model import linear_model
from protzilla.data_analysis.dimension_reduction import t_sne, umap
from protzilla.data_analysis.model_evaluation import evaluate_classification_model
from protzilla.data_analysis.classification import random_forest, svm
from protzilla.data_analysis.clustering import k_means, expectation_maximisation, hierarchical_agglomerative_clustering
from protzilla.data_analysis.plots import create_volcano_plot, clustergram_plot, prot_quant_plot
from protzilla.data_analysis.protein_graphs import variation_graph, peptides_to_isoform


from protzilla.steps import Step, StepManager


class DataAnalysisStep(Step):
    section = "data_analysis"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs

class DifferentialExpressionANOVA(DataAnalysisStep):
    name = "ANOVA"
    step = "differential_expression"
    method_description = (
        "A function that uses ANOVA to test the difference between two or more groups defined in the clinical data. The ANOVA test is conducted on the level of each protein. The p-values are corrected for multiple testing."
    )

    parameter_names = [
        "intensity_df",
        "multiple_testing_correction_method",
        "alpha",
        "log_base",
        "grouping",
        "selected_groups",
        "metadata_df",
    ]


    def method(self, inputs: dict) -> dict:
        return anova(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")


class DifferentialExpressionTTest(DataAnalysisStep):
    name = "t-test"
    step = "differential_expression"
    method_description = (
        "A function to conduct a two sample t-test between groups defined in the clinical data. The t-test is conducted on the level of each protein. The p-values are corrected for multiple testing. The fold change is calculated by group2/group1."
    )

    parameter_names = [
        "ttest_type",
        "intensity_df",
        "multiple_testing_correction",
        "alpha",
        "log_base",
        "grouping",
        "group1",
        "group2",
        "metadata_df",
    ]
    output_names = ["t-test_results"]

    def method(self, inputs: dict) -> dict:
        return t_test(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")

class DifferentialExpressionLinearModel(DataAnalysisStep):
    name = "Linear Model"
    step = "differential_expression"
    method_description = (
        "A function to fit a linear model using ordinary least squares for each protein. The linear model fits the protein intensities on Y axis and the grouping on X for group1 X=-1 and group2 X=1. The p-values are corrected for multiple testing."
    )

    parameter_names = [
        "intensity_df",
        "multiple_testing_correction_method",
        "alpha",
        "log_base",
        "grouping",
        "group1",
        "group2",
        "metadata_df",
    ]

    def method(self, inputs: dict) -> dict:
        return linear_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")

class PlotVolcano(DataAnalysisStep):
    name = "Volcano Plot"
    step = "differential_expression"
    parameter_names = [
        #TODO: Input the results from the differential expression analysis,
       'fc_threshold',
        'proteins_of_interest',
    ]

    def method(self, inputs: dict) -> dict:
        return create_volcano_plot(**inputs)

#TODO: input
    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ttest_results"] = steps.ttest_results
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]

class PlotScatter(DataAnalysisStep):
    name = "Scatter Plot"
    step = "data_analysis"

    parameter_names = [
        'input_df',
        'color_df',
    ]

    def method(self, inputs: dict) -> dict:
        return prot_quant_plot(**inputs)

    #TODO: input
    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["color_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]


class PlotClustergram(DataAnalysisStep):
    name = "Clustergram"
    step = "data_analysis"
    method_description = "Creates a clustergram from data"

    parameter_names = [
        'input_df',
        'sample_group_df',
        'flip_axes',
    ]

    def method(self, inputs: dict) -> dict:
        return clustergram_plot(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]


class PlotProtQuant(DataAnalysisStep):
    name = "Protein Quantification Plot"
    step = "data_analysis"
    method_description = "Creates a line chart for intensity across samples for proteingroups"

    parameter_names = [
        'input_df',
        'protein_group',
        'similarity_measure',
        'similarity'
    ]

    def method(self, inputs: dict) -> dict:
        return prot_quant_plot(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["color_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]


class PlotPrecisionRecallCurve(DataAnalysisStep):
    name = "Precision Recall"
    step = "data_analysis"
    method_description = "The precision-recall curve shows the tradeoff between precision and recall for different threshold"

    parameter_names = [
        #TODO: Input
        'plot_title',
    ]

    def method(self, inputs: dict) -> dict:
        return evaluate_classification_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
    #TODO: Input
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]


class PlotROC(DataAnalysisStep):
    name = "ROC"
    step = "data_analysis"
    method_description = "The ROC curve helps assess the model's ability to discriminate between positive and negative classes and determine an optimal threshold for decision making""

    parameter_names = [
        #TODO: Input
        'plot_title',
    ]

    def method(self, inputs: dict) -> dict:
        return evaluate_classification_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        #Todo: Input
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]


class ClusteringKMeans(DataAnalysisStep):
    name = "KMeans"
    step = "data_analysis"
    method_description = "Partitions a number of samples in k clusters using k-means"

    parameter_names = [
        'input_df',
        'labels_column',
        'positive_label',
        'model_selection',
        'model_selection_scoring',
        'scoring',
        'n_clusters',
        'random_state',
        'init_centroid_strategy',
        'n_init',
        'max_iter',
        'tolerance'
        'metadata_df',
    ]

    def method(self, inputs: dict) -> dict:
        return k_means(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]


class ClusteringExpectationMaximisation(DataAnalysisStep):
    name = "Expectation-maximization (EM) algorithm for fitting mixture-of-Gaussian models"
    step = "data_analysis"

    parameter_names = [
        'input_df',
        'labels_column',
        'positive_label',
        'model_selection',
        'model_selection_scoring',
        'scoring',
        'n_components',
        'reg_covar',
        'covariance_type',
        'init_params',
        'max_iter',
        'random_state',
        'metadata_df',
    ]

    def method(self, inputs: dict) -> dict:
        return expectation_maximisation(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]


class ClusteringHierarchicalAgglomerative(DataAnalysisStep):
    name = "Hierarchical Agglomerative Clustering"
    step = "data_analysis"
    method_description = "Performs hierarchical clustering utilizing a bottom-up approach"

    parameter_names = [
        'input_df',
        'labels_column',
        'positive_label',
        'model_selection',
        'model_selection_scoring',
        'scoring',
        'n_clusters',
        'metric',
        'linkage',
        'metadata_df',
    ]

    def method(self, inputs: dict) -> dict:
        return hierarchical_agglomerative_clustering(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        return inputs["Plotting is not implemented yet for this step."]