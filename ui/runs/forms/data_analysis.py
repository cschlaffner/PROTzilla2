import logging
from enum import Enum, StrEnum

from protzilla.methods.data_preprocessing import DataPreprocessingStep
from protzilla.methods.data_analysis import (
    DataAnalysisStep,
    DifferentialExpressionLinearModel,
    DifferentialExpressionTTest,
    DimensionReductionUMAP,
    DataAnalysisStep,
    PTMsPerSample,
    SelectPeptidesForProtein,
    DifferentialExpressionMannWhitneyOnPTM,
)
from protzilla.methods.data_preprocessing import DataPreprocessingStep
from protzilla.run import Run
from protzilla.steps import Step

from . import fill_helper
from .base import MethodForm
from .custom_fields import (
    CustomBooleanField,
    CustomCharField,
    CustomChoiceField,
    CustomFloatField,
    CustomMultipleChoiceField,
    CustomNumberField,
    CustomBooleanField,
)


class TTestType(Enum):
    welchs_t_test = "Welch's t-Test"
    students_t_test = "Student's t-Test"


class AnalysisLevel(Enum):
    protein = "Protein"


class MultipleTestingCorrectionMethod(Enum):
    benjamini_hochberg = "Benjamini-Hochberg"
    bonferroni = "Bonferroni"


class PValueCalculationMethod(Enum):
    auto = "Auto"
    exact = "Exact"
    asymptotic = "Asymptotic"


class YesNo(Enum):
    yes = "Yes"
    no = "No"


class ProteinsOfInterest(Enum):
    # TODO: Add the proteins of interest
    pass


class DynamicProteinFill(Enum):
    # TODO: Add the dynamic protein fill options
    pass


class SimilarityMeasure(StrEnum):
    euclidean_distance = "euclidean distance"
    cosine_similarity = "cosine similarity"


class ModelSelection(Enum):
    grid_search = "Grid search"
    randomized_search = "Randomized search"
    Manual = "Manual"


class ClusteringCriterion(Enum):
    gini = "gini"
    log_loss = "log_loss"
    entropy = "entropy"


class ClusteringScoring(Enum):
    adjusted_rand_score = "Adjusted Rand Score"
    completeness_score = "Completeness Score"
    fowlkes_mallows_score = "Fowlkes Mallows Score"
    homogeneity_score = "Homogeneity Score"
    mutual_info_score = "Mutual Info Score"
    normalized_mutual_info_score = "Normalized Mutual Info Score"
    rand_score = "Rand Score"
    v_measure_score = "V Measure Score"


class InitCentroidStrategy(Enum):
    kmeans_plus_plus = "k-means++"
    random = "random"


class ClusteringCovarianceType(Enum):
    full = "full"
    tied = "tied"
    diag = "diag"
    spherical = "spherical"


class ClusteringInitParams(Enum):
    kmeans = "kmeans"
    kmeans_plus_plus = "kmeans++"
    random = "random"
    random_from_data = "random from data"


class ClusteringMetric(Enum):
    euclidean = "euclidean"
    manhattan = "manhattan"
    cosine = "cosine"
    l1 = "l1"
    l2 = "l2"


class ClusteringLinkage(Enum):
    ward = "ward"
    complete = "complete"
    average = "average"
    single = "single"


class ClassificationValidationStrategy(Enum):
    k_fold = "KFold"
    repeated_k_fold = "repeated K-Fold"
    stratified_k_fold = "Stratified K-Fold"
    leave_one_out = "Leave One Out"
    leave_p_out = "Leave P Out"
    manual = "Manual"


class ClassificationScoring(Enum):
    accuracy = "accuracy"
    precision = "precision"
    recall = "recall"
    mathews_correlation_coefficient = "mathews correlation coefficient"


class ClassificationKernel(Enum):
    linear = "linear"
    poly = "poly"
    rbf = "rbf"
    sigmoid = "sigmoid"
    precomputed = "precomputed"


class DimensionReductionMetric(Enum):
    euclidean = "euclidean"
    manhattan = "manhattan"
    cosine = "cosine"
    havensine = "havensine"


class DifferentialExpressionANOVAForm(MethodForm):
    is_dynamic = True

    protein_df = CustomChoiceField(
        choices=[], label="Step to use protein intensities from"
    )
    multiple_testing_correction_method = CustomChoiceField(
        choices=MultipleTestingCorrectionMethod,
        label="Multiple testing correction",
        initial=MultipleTestingCorrectionMethod.benjamini_hochberg,
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)", min_value=0, max_value=1, step_size=0.01, initial=0.05
    )

    grouping = CustomChoiceField(choices=[], label="Grouping from metadata")
    selected_groups = CustomMultipleChoiceField(
        choices=[], label="Select groups to perform ANOVA on"
    )

    def fill_form(self, run: Run) -> None:
        self.fields[
            "protein_df"
        ].choices = fill_helper.get_choices_for_protein_df_steps(run)
        self.fields[
            "grouping"
        ].choices = fill_helper.get_choices_for_metadata_non_sample_columns(run)
        grouping = self.data.get("grouping", self.fields["grouping"].choices[0][0])
        self.fields["selected_groups"].choices = fill_helper.to_choices(
            run.steps.metadata_df[grouping].unique()
        )


class DifferentialExpressionTTestForm(MethodForm):
    is_dynamic = True

    ttest_type = CustomChoiceField(choices=TTestType, label="T-test type")
    protein_df = CustomChoiceField(
        choices=[], label="Step to use protein intensities from"
    )
    multiple_testing_correction_method = CustomChoiceField(
        choices=MultipleTestingCorrectionMethod,
        initial=MultipleTestingCorrectionMethod.benjamini_hochberg,
        label="Multiple testing correction",
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)",
        min_value=0,
        max_value=1,
        step_size=0.01,
        initial=0.05,
    )
    # log_base = CustomChoiceField(
    #     choices=LogBase,
    #     label="Base of the log transformation (optional)",
    #     required=False,
    # )
    grouping = CustomChoiceField(choices=[], label="Grouping from metadata")
    group1 = CustomChoiceField(choices=[], label="Group 1")
    group2 = CustomChoiceField(choices=[], label="Group 2")

    def fill_form(self, run: Run) -> None:
        self.fields[
            "protein_df"
        ].choices = fill_helper.get_choices_for_protein_df_steps(run)
        self.fields[
            "grouping"
        ].choices = fill_helper.get_choices_for_metadata_non_sample_columns(run)

        grouping = self.data.get("grouping", self.fields["grouping"].choices[0][0])

        # Set choices for group1 field based on selected grouping
        self.fields["group1"].choices = fill_helper.to_choices(
            run.steps.metadata_df[grouping].unique()
        )

        # Set choices for group2 field based on selected grouping and group1
        if (
            "group1" in self.data
            and self.data["group1"] in run.steps.metadata_df[grouping].unique()
        ):
            self.fields["group2"].choices = [
                (el, el)
                for el in run.steps.metadata_df[grouping].unique()
                if el != self.data["group1"]
            ]
        else:
            self.fields["group2"].choices = reversed(
                fill_helper.to_choices(run.steps.metadata_df[grouping].unique())
            )


class DifferentialExpressionLinearModelForm(MethodForm):
    multiple_testing_correction_method = CustomChoiceField(
        choices=MultipleTestingCorrectionMethod,
        label="Multiple testing correction",
        initial=MultipleTestingCorrectionMethod.benjamini_hochberg,
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)", min_value=0, max_value=1, step_size=0.01, initial=0.05
    )
    grouping = CustomChoiceField(choices=[], label="Grouping from metadata")
    group1 = CustomChoiceField(choices=[], label="Group 1")
    group2 = CustomChoiceField(choices=[], label="Group 2")

    def fill_form(self, run: Run) -> None:
        self.fields[
            "grouping"
        ].choices = fill_helper.get_choices_for_metadata_non_sample_columns(run)

        grouping = self.data.get("grouping", self.fields["grouping"].choices[0][0])

        # Set choices for group1 field based on selected grouping
        self.fields["group1"].choices = fill_helper.to_choices(
            run.steps.metadata_df[grouping].unique()
        )

        # Set choices for group2 field based on selected grouping and group1
        if (
            "group1" in self.data
            and self.data["group1"] in run.steps.metadata_df[grouping].unique()
        ):
            self.fields["group2"].choices = [
                (el, el)
                for el in run.steps.metadata_df[grouping].unique()
                if el != self.data["group1"]
            ]
        else:
            self.fields["group2"].choices = reversed(
                fill_helper.to_choices(run.steps.metadata_df[grouping].unique())
            )


class DifferentialExpressionMannWhitneyOnIntensityForm(MethodForm):
    is_dynamic = True

    protein_df = CustomChoiceField(
        choices=[], label="Step to use protein data from"
    )
    multiple_testing_correction_method = CustomChoiceField(
        choices=MultipleTestingCorrectionMethod,
        label="Multiple testing correction",
        initial=MultipleTestingCorrectionMethod.benjamini_hochberg,
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)", min_value=0, max_value=1, step_size=0.01, initial=0.05
    )
    grouping = CustomChoiceField(choices=[], label="Grouping from metadata")
    group1 = CustomChoiceField(choices=[], label="Group 1")
    group2 = CustomChoiceField(choices=[], label="Group 2")

    def fill_form(self, run: Run) -> None:
        self.fields["protein_df"].choices = fill_helper.get_choices_for_protein_df_steps(run)

        self.fields["grouping"].choices = fill_helper.get_choices_for_metadata_non_sample_columns(run)

        grouping = self.data.get("grouping", self.fields["grouping"].choices[0][0])

        # Set choices for group1 field based on selected grouping
        self.fields["group1"].choices = fill_helper.to_choices(
            run.steps.metadata_df[grouping].unique()
        )

        # Set choices for group2 field based on selected grouping and group1
        if (
            "group1" in self.data
            and self.data["group1"] in run.steps.metadata_df[grouping].unique()
        ):
            self.fields["group2"].choices = [
                (el, el)
                for el in run.steps.metadata_df[grouping].unique()
                if el != self.data["group1"]
            ]
        else:
            self.fields["group2"].choices = reversed(
                fill_helper.to_choices(run.steps.metadata_df[grouping].unique())
            )


class DifferentialExpressionMannWhitneyOnPTMForm(MethodForm):
    is_dynamic = True

    ptm_df = CustomChoiceField(choices=[], label="Step to use ptm data from")
    multiple_testing_correction_method = CustomChoiceField(
        choices=MultipleTestingCorrectionMethod,
        label="Multiple testing correction",
        initial=MultipleTestingCorrectionMethod.benjamini_hochberg,
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)", min_value=0, max_value=1, step_size=0.01, initial=0.05
    )
    p_value_calculation_method = CustomChoiceField(
        choices=PValueCalculationMethod,
        label="P-value calculation method",
        initial=PValueCalculationMethod.auto,
    )
    grouping = CustomChoiceField(choices=[], label="Grouping from metadata")
    group1 = CustomChoiceField(choices=[], label="Group 1")
    group2 = CustomChoiceField(choices=[], label="Group 2")

    def fill_form(self, run: Run) -> None:
        self.fields["ptm_df"].choices = fill_helper.to_choices(
            run.steps.get_instance_identifiers(PTMsPerSample, "ptm_df")
        )

        self.fields["grouping"].choices = fill_helper.get_choices_for_metadata_non_sample_columns(run)

        grouping = self.data.get("grouping", self.fields["grouping"].choices[0][0])

        # Set choices for group1 field based on selected grouping
        self.fields["group1"].choices = fill_helper.to_choices(
            run.steps.metadata_df[grouping].unique()
        )

        # Set choices for group2 field based on selected grouping and group1
        if (
            "group1" in self.data
            and self.data["group1"] in run.steps.metadata_df[grouping].unique()
        ):
            self.fields["group2"].choices = [
                (el, el)
                for el in run.steps.metadata_df[grouping].unique()
                if el != self.data["group1"]
            ]
        else:
            self.fields["group2"].choices = reversed(
                fill_helper.to_choices(run.steps.metadata_df[grouping].unique())
            )


class DifferentialExpressionKruskalWallisOnIntensityForm(MethodForm):
    is_dynamic = True

    protein_df = CustomChoiceField(
        choices=[], label="Step to use protein data from"
    )
    multiple_testing_correction_method = CustomChoiceField(
        choices=MultipleTestingCorrectionMethod,
        label="Multiple testing correction",
        initial=MultipleTestingCorrectionMethod.benjamini_hochberg,
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)", min_value=0, max_value=1, step_size=0.01, initial=0.05
    )

    grouping = CustomChoiceField(choices=[], label="Grouping from metadata")
    selected_groups = CustomMultipleChoiceField(
        choices=[], label="Select groups to perform Kruskal-Wallis Test on"
    )

    def fill_form(self, run: Run) -> None:
        self.fields["protein_df"].choices = fill_helper.get_choices_for_protein_df_steps(run)

        self.fields["grouping"].choices = fill_helper.get_choices_for_metadata_non_sample_columns(run)
        grouping = self.data.get("grouping", self.fields["grouping"].choices[0][0])
        self.fields["selected_groups"].choices = fill_helper.to_choices(
            run.steps.metadata_df[grouping].unique()
        )


class DifferentialExpressionKruskalWallisOnPTMForm(MethodForm):
    is_dynamic = True

    ptm_df = CustomChoiceField(
        choices=[], label="Step to use ptm data from"
    )
    multiple_testing_correction_method = CustomChoiceField(
        choices=MultipleTestingCorrectionMethod,
        label="Multiple testing correction",
        initial=MultipleTestingCorrectionMethod.benjamini_hochberg,
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)", min_value=0, max_value=1, step_size=0.01, initial=0.05
    )

    grouping = CustomChoiceField(choices=[], label="Grouping from metadata")
    selected_groups = CustomMultipleChoiceField(
        choices=[], label="Select groups to perform Kruskal-Wallis Test on"
    )

    def fill_form(self, run: Run) -> None:
        self.fields["ptm_df"].choices = fill_helper.to_choices(
            run.steps.get_instance_identifiers(PTMsPerSample, "ptm_df")
        )
        self.fields["grouping"].choices = fill_helper.get_choices_for_metadata_non_sample_columns(run)
        grouping = self.data.get("grouping", self.fields["grouping"].choices[0][0])
        self.fields["selected_groups"].choices = fill_helper.to_choices(
            run.steps.metadata_df[grouping].unique()
        )


class PlotVolcanoForm(MethodForm):
    is_dynamic = True

    input_dict = CustomChoiceField(
        choices=[],
        label="Input data dict (generated by t-Test or Linear Model Diff Exp)",
    )
    fc_threshold = CustomNumberField(
        label="Log2 fold change threshold", min_value=0, initial=0
    )
    items_of_interest = CustomMultipleChoiceField(
        choices=[],
        label="Items of interest (will be highlighted)",
    )

    def fill_form(self, run: Run) -> None:
        self.fields["input_dict"].choices = fill_helper.to_choices(
            run.steps.get_instance_identifiers(
                Step, ["corrected_p_values_df", "log2_fold_change_df"],
            )
        )

        input_dict_instance_id = self.data.get(
            "input_dict", self.fields["input_dict"].choices[0][0]
        )

        items_of_interest = []
        step_output = run.steps.get_step_output(
            Step, "differentially_expressed_proteins_df", input_dict_instance_id
        )
        if step_output is not None:
            items_of_interest = step_output["Protein ID"].unique()
        step_output = run.steps.get_step_output(
            Step, "differentially_expressed_ptm_df", input_dict_instance_id
        )
        if step_output is not None:
            items_of_interest = step_output["PTM"].unique()

        self.fields["items_of_interest"].choices = fill_helper.to_choices(items_of_interest)


class PlotScatterPlotForm(MethodForm):
    input_df = CustomChoiceField(
        choices=[],
        label="Choose dataframe to be plotted",
    )
    color_df = CustomChoiceField(
        choices=[],
        label="Choose dataframe to be used for coloring",
        required=False,
    )

    def fill_form(self, run: Run) -> None:
        self.fields["input_df"].choices = fill_helper.to_choices(
            run.steps.get_instance_identifiers(DimensionReductionUMAP, "embedded_data")
        )

        self.fields["color_df"].choices = fill_helper.to_choices(
            run.steps.get_instance_identifiers(Step, "color_df"), required=False
        )


class PlotClustergramForm(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
    )
    sample_group_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be used for coloring",
        required=False,
    )
    flip_axis = CustomChoiceField(
        choices=YesNo,
        label="Flip axis",
        initial=YesNo.no,
    )


class PlotProtQuantForm(MethodForm):
    is_dynamic = True

    input_df = CustomChoiceField(
        choices=[],
        label="Choose dataframe to be plotted",
    )
    protein_group = CustomChoiceField(
        choices=[],
        label="Protein group: choose highlighted protein group",
    )
    similarity_measure = CustomChoiceField(
        choices=SimilarityMeasure,
        label="Similarity Measurement: choose how to compare protein groups",
        initial=SimilarityMeasure.euclidean_distance,
    )
    similarity = CustomNumberField(
        label="Similarity", min_value=-1, max_value=999, step_size=1, initial=1
    )

    def fill_form(self, run: Run) -> None:
        self.fields["input_df"].choices = fill_helper.get_choices_for_protein_df_steps(
            run
        )

        input_df_instance_id = self.data.get(
            "input_df", self.fields["input_df"].choices[0][0]
        )

        self.fields["protein_group"].choices = fill_helper.to_choices(
            run.steps.get_step_output(
                step_type=Step,
                output_key="protein_df",
                instance_identifier=input_df_instance_id,
            )["Protein ID"].unique()
        )

        similarity_measure = self.data.get(
            "similarity_measure", self.fields["similarity_measure"].choices[0][0]
        )
        self.data = self.data.copy()
        if similarity_measure == SimilarityMeasure.cosine_similarity:
            self.fields["similarity"] = CustomFloatField(
                label="Cosine Similarity",
                min_value=-1,
                max_value=1,
                step_size=0.1,
                initial=0,
            )
            if (
                "similarity" not in self.data
                or float(self.data["similarity"]) < -1
                or float(self.data["similarity"]) > 1
            ):
                self.data["similarity"] = 0
        else:
            self.fields["similarity"] = CustomNumberField(
                label="Euclidean Distance",
                min_value=0,
                max_value=999,
                step_size=1,
                initial=1,
            )
            if (
                "similarity" not in self.data
                or float(self.data["similarity"]) < 0
                or float(self.data["similarity"]) > 999
            ):
                self.data["similarity"] = 1


class PlotPrecisionRecallCurveForm(MethodForm):
    # Todo: Input
    plot_title = CustomCharField(
        label="Title of the plot (optional)", initial="Precision-Recall Curve"
    )


class PlotROCCurveForm(MethodForm):
    # Todo: Input
    plot_title = CustomCharField(
        label="Title of the plot (optional)", initial="ROC Curve"
    )


class ClusteringKMeansForm(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(
        choices=[], label="Choose labels column from metadata"
    )
    positive_label = CustomChoiceField(choices=[], label="Choose positive class")
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        initial=ModelSelection.grid_search,
    )
    # TODO: Add dynamic parameters for grid search & randomized search
    # TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(
        choices=ClusteringScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
    )
    scoring = CustomMultipleChoiceField(
        choices=ClusteringScoring,
        label="Scoring for the model",
    )
    # TODO: workflow_meta line 1375
    n_clusters = CustomNumberField(
        label="Number of clusters to find", min_value=1, step_size=1, initial=8
    )
    # TODO: workflow_meta line 1384
    random_state = CustomNumberField(
        label="Seed for centroid initialisation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        initial=0,
    )
    init_centroid_strategy = CustomMultipleChoiceField(
        choices=InitCentroidStrategy,
        label="Method for initialisation of centroids",
        initial=InitCentroidStrategy.random,
    )
    # TODO: workflow_meta line 1402
    n_init = CustomNumberField(
        label="Number of times the k-means algorithm is run with different centroid seeds",
        min_value=1,
        step_size=1,
        initial=10,
    )
    # TODO: workflow_meta line 1410
    max_iter = CustomNumberField(
        label="Maximum number of iterations of the k-means algorithm for a single run",
        min_value=1,
        step_size=1,
        initial=300,
    )
    # TODO: workflow_meta line 1417
    tolerance = CustomNumberField(
        label="Relative tolerance with regards to Frobenius norm",
        min_value=0,
        initial=1e-4,
    )


class ClusteringExpectationMaximizationForm(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
    )
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(
        choices=[], label="Choose labels column from metadata"
    )
    positive_label = CustomChoiceField(choices=[], label="Choose positive class")
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        initial=ModelSelection.grid_search,
    )
    # TODO: Add dynamic parameters for grid search & randomized search
    # TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(
        choices=ClusteringScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
    )
    scoring = CustomMultipleChoiceField(
        choices=ClusteringScoring,
        label="Scoring for the model",
        initial=ClusteringScoring.adjusted_rand_score,
    )
    # TODO: workflow_meta line 1509
    n_components = CustomNumberField(
        label="The number of mixture components", initial=1
    )
    # TODO: workflow_meta line 1515
    reg_covar = CustomNumberField(
        label="Non-negative regularization added to the diagonal of covariance",
        min_value=0,
        initial=1e-6,
    )
    covariance_type = CustomMultipleChoiceField(
        choices=ClusteringCovarianceType,
        label="Type of covariance",
        initial=ClusteringCovarianceType.full,
    )
    init_params = CustomMultipleChoiceField(
        choices=ClusteringInitParams,
        label="The method used to initialize the weights, the means and the precisions.",
    )
    max_iter = CustomNumberField(
        label="The number of EM iterations to perform", initial=100
    )
    random_state = CustomNumberField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        initial=0,
    )


class ClusteringHierarchicalAgglomerativeClusteringForm(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(
        choices=[], label="Choose labels column from metadata"
    )
    positive_label = CustomChoiceField(choices=[], label="Choose positive class")
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        initial=ModelSelection.grid_search,
    )
    # TODO: Add dynamic parameters for grid search & randomized search
    # TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(
        choices=ClusteringScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
        initial=ClusteringScoring.adjusted_rand_score,
    )
    scoring = CustomMultipleChoiceField(
        choices=ClusteringScoring,
        label="Scoring for the model",
    )
    # TODO: workflow_meta line 1647
    n_clusters = CustomNumberField(
        label="The number of clusters to find", min_value=1, step_size=1, initial=2
    )
    metric = CustomMultipleChoiceField(
        choices=ClusteringMetric,
        label="Distance metric",
        initial=ClusteringMetric.euclidean,
    )
    linkage = CustomMultipleChoiceField(
        choices=ClusteringLinkage,
        label="The linkage criterion to use in order to to determine the distance to use between sets of observation",
        initial=ClusteringLinkage.ward,
    )


class ClassificationRandomForestForm(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(
        choices=[], label="Choose labels column from metadata"
    )
    positive_label = CustomChoiceField(choices=[], label="Choose positive class")
    test_size = CustomNumberField(label="Test size", min_value=0, initial=0.20)
    split_stratify = CustomChoiceField(
        choices=YesNo,
        label="Stratify the split",
        initial=YesNo.yes,
    )
    # TODO: Validation strategy
    validatation_strategy = CustomChoiceField(
        choices=ClassificationValidationStrategy,
        label="Validation strategy",
        initial=ClassificationValidationStrategy.k_fold,
    )
    # TODO: Workflow_meta line 1763
    train_val_split = CustomNumberField(
        label="Choose the size of the validation data set (you can either enter the absolute number of validation "
              "samples or a number between 0.0 and 1.0 to represent the percentage of validation samples)",
        initial=0.20,
    )
    # TODO: Workflow_meta line 1770
    n_splits = CustomNumberField(label="Number of folds", min_value=2, initial=5)
    # TODO: workflow_meta line 1781-1784
    shuffle = CustomChoiceField(
        choices=YesNo,
        label="Whether to shuffle the data before splitting into batches",
        initial=YesNo.yes,
    )
    # TODO: workflow_meta line 1791
    n_repeats = CustomNumberField(
        label="Number of times cross-validator needs to be repeated",
        min_value=1,
        initial=10,
    )
    # TODO: workflow_meta line 1801
    random_state_cv = CustomNumberField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        initial=42,
    )
    # TODO: workflow_meta line 1806
    p_samples = CustomNumberField(label="Size of the test sets", initial=1)
    scoring = CustomMultipleChoiceField(
        choices=ClassificationScoring,
        label="Scoring for the model",
        initial=ClassificationScoring.accuracy,
    )
    # TODO: workflow_meta line 1830-1837
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        initial=ModelSelection.grid_search,
    )
    # TODO: workflow_meta line 1849
    model_selection_scoring = CustomChoiceField(
        choices=ClassificationScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
        initial=ClassificationScoring.accuracy,
    )
    n_estimators = CustomNumberField(
        label="The number of trees in the forest", min_value=1, step_size=1, initial=100
    )
    criterion = CustomMultipleChoiceField(
        choices=ClusteringCriterion,
        label="The function to measure the quality of a split",
        initial=ClusteringCriterion.gini,
    )
    max_depth = CustomNumberField(
        label="The maximum depth of the tree", min_value=1, initial=1
    )
    random_state = CustomNumberField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        initial=6,
    )


class ClassificationSVMForm(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(
        choices=[], label="Choose labels column from metadata"
    )
    positive_label = CustomChoiceField(choices=[], label="Choose positive class")
    test_size = CustomNumberField(label="Test size", min_value=0, initial=0.20)
    split_stratify = CustomChoiceField(
        choices=YesNo,
        label="Stratify the split",
        initial=YesNo.yes,
    )
    # TODO: Validation strategy
    validatation_strategy = CustomChoiceField(
        choices=ClassificationValidationStrategy,
        label="Validation strategy",
        initial=ClassificationValidationStrategy.k_fold,
    )
    train_val_split = CustomNumberField(
        label="Choose the size of the validation data set (you can either enter the absolute number of validation "
              "samples or a number between 0.0 and 1.0 to represent the percentage of validation samples)",
        initial=0.20,
    )
    # TODO: Workflow_meta line 1973
    n_splits = CustomNumberField(label="Number of folds", min_value=2, initial=5)
    # TODO: workflow_meta line 1984-1989
    shuffle = CustomChoiceField(
        choices=YesNo,
        label="Whether to shuffle the data before splitting into batches",
        initial=YesNo.yes,
    )
    # TODO: workflow_meta line 1994
    n_repeats = CustomNumberField(
        label="Number of times cross-validator needs to be repeated",
        min_value=1,
        initial=10,
    )
    # TODO: workflow_meta line 2004
    random_state_cv = CustomNumberField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        initial=42,
    )
    p_samples = CustomNumberField(label="Size of the test sets", initial=1)
    scoring = CustomMultipleChoiceField(
        choices=ClassificationScoring,
        label="Scoring for the model",
        initial=ClassificationScoring.accuracy,
    )
    # TODO: workflow_meta line 2033-2040
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        initial=ModelSelection.grid_search,
    )
    model_selection_scoring = CustomChoiceField(
        choices=ClassificationScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
        initial=ClassificationScoring.accuracy,
    )
    # TODO: workflow_meta line 2059
    C = CustomNumberField(
        label="C: regularization parameter (the strength of the regularization is inversely proportional to C)",
        min_value=0.0,
        initial=1.0,
    )
    kernel = CustomMultipleChoiceField(
        choices=ClassificationKernel,
        label="Specifies the kernel type to be used in the algorithm",
        initial=ClassificationKernel.linear,
    )
    tolerance = CustomNumberField(
        label="Tolerance for stopping criterion", min_value=0.0, initial=1e-4
    )
    random_state = CustomNumberField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        initial=6,
    )


class ModelEvaluationClassificationModelForm(MethodForm):
    # TODO: Input_dict
    scoring = CustomMultipleChoiceField(
        choices=ClassificationScoring,
        label="Scoring for the model",
        initial=ClassificationScoring.accuracy,
    )


class DimensionReductionTSNEForm(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Dimension reduction of a dataframe using t-SNE",
    )
    n_components = CustomNumberField(
        label="Dimension of the embedded space", min_value=1, step_size=1, initial=2
    )
    perplexity = CustomNumberField(
        label="Perplexity", min_value=5.0, max_value=50.0, initial=30.0
    )
    metric = CustomMultipleChoiceField(
        choices=DimensionReductionMetric,
        label="Metric",
        initial=DimensionReductionMetric.euclidean,
    )
    random_state = CustomNumberField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        initial=6,
    )
    n_iter = CustomNumberField(
        label="Maximum number of iterations for the optimization",
        min_value=250,
        initial=1000,
    )
    n_iter_without_progress = CustomNumberField(
        label="Maximum number of iterations without progress before we abort the optimization",
        min_value=250,
        step_size=1,
        initial=300,
    )


class DimensionReductionUMAPForm(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Dimension reduction of a dataframe using UMAP",
    )
    n_neighbors = CustomNumberField(
        label="The size of local neighborhood (in terms of number of neighboring sample points) used for manifold "
              "approximation",
        min_value=2,
        max_value=100,
        step_size=1,
        initial=15,
    )
    n_components = CustomNumberField(
        label="Number of components", min_value=1, max_value=100, step_size=1, initial=2
    )
    min_dist = CustomFloatField(
        label="The effective minimum distance between embedded points",
        min_value=0.1,
        step_size=0.1,
        initial=0.1,
    )
    metric = CustomChoiceField(
        choices=DimensionReductionMetric,
        label="Distance metric",
    )
    random_state = CustomNumberField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        initial=42,
    )

    def fill_form(self, run: Run) -> None:
        self.fields["input_df"].choices = fill_helper.get_choices_for_protein_df_steps(
            run
        )


class ProteinGraphPeptidesToIsoformForm(MethodForm):
    protein_ID = CustomCharField(
        label="Protein ID", initial="Enter the Uniprot-ID of the protein"
    )
    # TODO: workflow_meta line 2255 - 2263
    k = CustomNumberField(label="k-mer length", min_value=1, step_size=1, initial=5)
    allowed_mismatches = CustomNumberField(
        label="Number of allowed mismatched amino acids per peptide. For many allowed mismatches, this can take a "
              "long time.",
        min_value=0,
        step_size=1,
        initial=2,
    )


class ProteinGraphVariationGraphForm(MethodForm):
    protein_ID = CustomCharField(
        label="Protein ID", initial="Enter the Uniprot-ID of the protein"
    )
    # TODO: workflow_meta line 2291 - 2295


class FLEXIQuantLFForm(MethodForm):
    is_dynamic = True

    peptide_df = CustomChoiceField(label="Peptide dataframe", choices=[])
    grouping_column = CustomChoiceField(label="Grouping column in metadata", choices=[])
    reference_group = CustomChoiceField(label="Reference group", choices=[])
    protein_id = CustomChoiceField(label="Protein ID", choices=[])
    num_init = CustomNumberField(
        label="Number of RANSAC initiations",
        initial=30,
        min_value=1,
        max_value=60,
        step_size=1,
    )
    mod_cutoff = CustomFloatField(
        label="Modification cutoff", initial=0.5, min_value=0, max_value=1
    )

    def fill_form(self, run: Run) -> None:
        self.fields["peptide_df"].choices = fill_helper.get_choices(run, "peptide_df")
        self.fields["grouping_column"].choices = fill_helper.to_choices(
            run.steps.metadata_df.drop("Sample", axis=1).columns[1:]
        )

        chosen_grouping_column = self.data.get(
            "grouping_column", self.fields["grouping_column"].choices[0][0]
        )

        self.fields["reference_group"].choices = fill_helper.to_choices(
            run.steps.metadata_df[chosen_grouping_column].unique()
        )
        peptide_df_instance_id = self.data.get(
            "peptide_df", self.fields["peptide_df"].choices[0][0]
        )

        self.fields["protein_id"].choices = fill_helper.to_choices(
            run.steps.get_step_output(Step, "peptide_df", peptide_df_instance_id)[
                "Protein ID"
            ].unique()
        )


class SelectPeptidesForProteinForm(MethodForm):
    is_dynamic = True

    peptide_df = CustomChoiceField(
        choices=[], label="Step to use peptide dataframe from"
    )

    auto_select = CustomBooleanField(
        label="Automatically select most significant Protein",
        initial=False,
    )

    protein_list = CustomChoiceField(
        choices=[],
        label="Select a list of Proteins from which you want to choose your Proteins of Interest",
    )

    sort_proteins = CustomBooleanField(
        label="Sort Proteins by p-value (requires a list of Proteins from a Differential Expression Analysis to be selected)",
        initial=False,
    )

    protein_ids = CustomMultipleChoiceField(
        choices=[],
        label="Protein IDs",
    )

    def fill_form(self, run: Run) -> None:
        self.fields["peptide_df"].choices = fill_helper.get_choices(
            run, "peptide_df", Step
        )
        self.fields["peptide_df"].initial = run.steps.get_instance_identifiers(
            DataPreprocessingStep, "peptide_df"
        )[-1]

        selected_auto_select = self.data.get("auto_select")

        choices = fill_helper.to_choices([] if selected_auto_select else ["all proteins"])
        choices.extend(fill_helper.get_choices(
            run, "significant_proteins_df", DataAnalysisStep
        ))
        self.fields["protein_list"].choices = choices

        chosen_list = self.data.get("protein_list", self.fields["protein_list"].choices[0][0])
        if not selected_auto_select:
            self.toggle_visibility("sort_proteins", True)
            self.toggle_visibility("protein_ids", True)

            if chosen_list == "all proteins":
                self.fields["protein_ids"].choices = fill_helper.to_choices(
                    run.steps.get_step_output(Step, "protein_df")["Protein ID"].unique()
                )
            else:
                if self.data.get("sort_proteins"):
                    self.fields["protein_ids"].choices = fill_helper.to_choices(
                        run.steps.get_step_output(
                            DataAnalysisStep, "significant_proteins_df", chosen_list
                        ).sort_values(by="corrected_p_value")["Protein ID"].unique()
                    )
                else:
                    self.fields["protein_ids"].choices = fill_helper.to_choices(
                        run.steps.get_step_output(
                            DataAnalysisStep, "significant_proteins_df", chosen_list
                        )["Protein ID"].unique()
                    )
        else:
            self.toggle_visibility("sort_proteins", False)
            self.toggle_visibility("protein_ids", False)


class PTMsPerSampleForm(MethodForm):
    peptide_df = CustomChoiceField(
        choices=[],
        label="Peptide dataframe containing the peptides of a single protein",
    )

    def fill_form(self, run: Run) -> None:
        self.fields["peptide_df"].choices = fill_helper.get_choices(
            run, "peptide_df"
        )[::-1]

        single_protein_peptides = run.steps.get_instance_identifiers(
            SelectPeptidesForProtein, "peptide_df"
        )
        if single_protein_peptides:
            self.fields["peptide_df"].initial = single_protein_peptides[0]


class PTMsPerProteinAndSampleForm(MethodForm):
    peptide_df = CustomChoiceField(
        choices=[],
        label="Peptide dataframe containing the peptides of a single protein",
    )

    def fill_form(self, run: Run) -> None:
        self.fields["peptide_df"].choices = fill_helper.get_choices(run, "peptide_df")[::-1]

        single_protein_peptides = run.steps.get_instance_identifiers(
            SelectPeptidesForProtein, "peptide_df"
        )
        if single_protein_peptides:
            self.fields["peptide_df"].initial = single_protein_peptides[0]