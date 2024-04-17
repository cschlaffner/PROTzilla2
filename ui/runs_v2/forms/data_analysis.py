from enum import Enum

from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import (
    CustomCharField,
    CustomChoiceField,
    CustomFloatField,
    CustomMultipleChoiceField,
)


class TTestType(Enum):
    welchs_t_test = "Welch's t-Test"
    students_t_test = "Student's t-Test"


class AnalysisLevel(Enum):
    protein = "Protein"


class MultipelTestingCorrectionMethod(Enum):
    benjamini_hochberg = ("Benjamini-Hochberg",)
    bonferroni = "Bonferroni"


class LogBase(Enum):
    none = ("None",)
    log2 = ("log2",)
    log10 = "log10"


class YesNo(Enum):
    yes = "Yes"
    no = "No"


class ProteinsOfInterest(Enum):
    # TODO: Add the proteins of interest
    pass


class DynamicProteinFill(Enum):
    # TODO: Add the dynamic protein fill options
    pass


class SimilarityMeasure(Enum):
    euclidean_distance = "Euclidean distance"
    cosine_similarity = "Cosine similarity"


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
    pass


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


class DifferentialExpression_ANOVA(MethodForm):
    # intensity_df = CustomChoiceField(
    #    choices=AnalysisLevel, label="Intensitys"
    # )
    multiple_testing_correction = CustomChoiceField(
        choices=MultipelTestingCorrectionMethod,
        label="Multiple testing correction",
        default="Benjamini-Hochberg",
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)",
        min_value=0,
        max_value=1,
        default=0.05
    )
    log_base = CustomChoiceField(
        choices=LogBase,
        label="Base of the log transformation",
        default="log2"
    )
    #TODO: Add dynamic fill for grouping & selected_groups
    grouping = "Put a usefull default here"
    selected_groups = "Put a usefull default here"
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class DifferentialExpression_TTestForm(MethodForm):
    ttest_type = CustomChoiceField(
        choices=TTestType,
        label="T-test type"
    )
    # intensity_df = CustomChoiceField(
    #    choices=AnalysisLevel, label="Intensitys"
    # )
    multiple_testing_correction = CustomChoiceField(
        choices=MultipelTestingCorrectionMethod,
        label="Multiple testing correction",
        default="Benjamini-Hochberg",
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)",
        min_value=0,
        max_value=1,
        step_size=0.05,
        default=0.05
    )
    log_base = CustomChoiceField(
        choices=LogBase,
        label="Base of the log transformation",
        default="log2"
    )
    grouping = "Put a usefull default here"
    group1 = "Put a usefull default here"
    group2 = "Put a usefull default here"
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class DifferentialExpression_LinearModel(MethodForm):
    multiple_testing_correction = CustomChoiceField(
        choices=MultipelTestingCorrectionMethod,
        label="Multiple testing correction",
        default="Benjamini-Hochberg",
    )
    alpha = CustomFloatField(
        label="Error rate (alpha)",
        min_value=0,
        max_value=1,
        default=0.05
    )
    log_base = CustomChoiceField(
        choices=LogBase,
        label="Base of the log transformation",
        default="log2"
    )
    grouping = "Put a usefull default here"
    group1 = "Put a usefull default here"
    group2 = "Put a usefull default here"
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class PlotVolcano(MethodForm):
    #TODO: Add inbput_dict
    input_dict = "Put a usefull default here"
    fc_threshold = CustomFloatField(
        label="log 2 fold change threshold",
        min_value=0,
        default=0
    )
    #TODO: Add dynamic fill for proteins_of_interest
    proteins_of_interest = CustomMultipleChoiceField(
        choices=ProteinsOfInterest,
        label="Proteins of interest",
        default=None
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class PlotScatterPlot(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    color_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be used for coloring",
        default=[None, None],
        required=False,
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class PlotClustergram(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    sample_group_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be used for coloring",
        default=[None, None],
        required=False,
    )
    flip_axis = CustomChoiceField(
        choices=YesNo,
        label="Flip axis",
        default="No"
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class PlotProtQuant(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    protein_group = CustomChoiceField(
        choices=DynamicProteinFill,
        label="Protein group: choose highlighted protein group",
        default=None,
    )
    similarity_measure = CustomChoiceField(
        choices=SimilarityMeasure,
        label="Similarity Measurement: choose how to compare protein groups",
        default="Euclidean distance",
    )
    similarity = CustomFloatField(
        label="Similarity",
        min_value=-1,
        max_value=999,
        step_size=1,
        default=1
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class Plotprecision_recall_curve(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    plot_title = CustomCharField(
        label="Title of the plot (optional)",
        default="Precision-Recall Curve"
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class ClusteringKMeans(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(label="Choose labels column from metadata")
    positive_label = CustomChoiceField(label="Choose positive class")
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        default="Grid search",
    )
    # TODO: Add dynamic parameters for grid search & randomized search
    # TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(
        choices=ClusteringScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
        default="Adjusted Rand Score",
        dynamic=True,
    )
    scoring = CustomMultipleChoiceField(
        choices=ClusteringScoring,
        label="Scoring for the model",
        default="Adjusted Rand Score",
    )
    # TODO: workflow_meta line 1375
    n_clusters = CustomFloatField(
        label="Number of clusters to find",
        min_value=1,
        step_size=1,
        default=8
    )
    # TODO: workflow_meta line 1384
    random_state = CustomFloatField(
        label="Seed for centroid initialisation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        default=0,
    )
    init_centroid_strategy = CustomMultipleChoiceField(
        choices=InitCentroidStrategy,
        label="Method for initialisation of centroids",
        default="random",
    )
    # TODO: workflow_meta line 1402
    n_init = CustomFloatField(
        label="Number of times the k-means algorithm is run with different centroid seeds",
        min_value=1,
        step_size=1,
        default=10,
    )
    # TODO: workflow_meta line 1410
    max_iter = CustomFloatField(
        label="Maximum number of iterations of the k-means algorithm for a single run",
        min_value=1,
        step_size=1,
        default=300,
    )
    # TODO: workflow_meta line 1417
    tolerance = CustomFloatField(
        label="Relative tolerance with regards to Frobenius norm",
        min_value=0,
        default=1e-4,
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class ClusteringExpectationMaximization(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(label="Choose labels column from metadata")
    positive_label = CustomChoiceField(label="Choose positive class")
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        default="Grid search",
    )
    # TODO: Add dynamic parameters for grid search & randomized search
    # TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(
        choices=ClusteringScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
        default="Adjusted Rand Score",
        dynamic=True,
    )
    scoring = CustomMultipleChoiceField(
        choices=ClusteringScoring,
        label="Scoring for the model",
        default="Adjusted Rand Score",
    )
    # TODO: workflow_meta line 1509
    n_components = CustomFloatField(
        label="The number of mixture components",
        default=1)
    # TODO: workflow_meta line 1515
    reg_covar = CustomFloatField(
        label="Non-negative regularization added to the diagonal of covariance",
        min_value=0,
        default=1e-6,
    )
    covariance_type = CustomMultipleChoiceField(
        choices=ClusteringCovarianceType,
        label="Type of covariance",
        default="full"
    )
    init_params = CustomMultipleChoiceField(
        choices=ClusteringInitParams,
        label="The method used to initialize the weights, the means and the precisions.",
        default="kmeans",
    )
    max_iter = CustomFloatField(
        label="The number of EM iterations to perform",
        default=100
    )
    random_state = CustomFloatField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        default=0,
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class ClusteringHierarchicalAgglomerativeClustering(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(label="Choose labels column from metadata")
    positive_label = CustomChoiceField(label="Choose positive class")
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        default="Grid search",
    )
    # TODO: Add dynamic parameters for grid search & randomized search
    # TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(
        choices=ClusteringScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
        default="Adjusted Rand Score",
        dynamic=True,
    )
    scoring = CustomMultipleChoiceField(
        choices=ClusteringScoring,
        label="Scoring for the model",
        default="Adjusted Rand Score",
    )
    # TODO: workflow_meta line 1647
    n_clusters = CustomFloatField(
        label="The number of clusters to find",
        min_value=1,
        step_size=1,
        default=2
    )
    metric = CustomMultipleChoiceField(
        choices=ClusteringMetric,
        label="Distance metric",
        default="euclidean"
    )
    linkage = CustomMultipleChoiceField(
        choices=ClusteringLinkage,
        label="The linkage criterion to use in order to to determine the distance to use between sets of observation",
        default="ward",
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class ClassificationRandomForest(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(label="Choose labels column from metadata")
    positive_label = CustomChoiceField(label="Choose positive class")
    test_size = CustomFloatField(
        label="Test size",
        min_value=0,
        default=0.20)
    split_stratify = CustomChoiceField(
        choices=YesNo,
        label="Stratify the split",
        default="Yes"
    )
    # TODO: Validation strategy
    validatation_strategy = CustomChoiceField(choices=ClassificationValidationStrategy)
    # TODO: Workflow_meta line 1763
    train_val_split = CustomFloatField(
        label="Choose the size of the validation data set (you can either enter the absolute number of validation samples or a number between 0.0 and 1.0 to represent the percentage of validation samples)",
        default=0.20,
    )
    # TODO: Workflow_meta line 1770
    n_splits = CustomFloatField(
        label="Number of folds",
        min_value=2,
        default=5)
    # TODO: workflow_meta line 1781-1784
    shuffle = CustomChoiceField(
        choices=YesNo,
        label="Whether to shuffle the data before splitting into batches",
        default="Yes",
    )
    # TODO: workflow_meta line 1791
    n_repeats = CustomFloatField(
        label="Number of times cross-validator needs to be repeated",
        min_value=1,
        default=10,
    )
    # TODO: workflow_meta line 1801
    random_state_cv = CustomFloatField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        default=42,
    )
    # TODO: workflow_meta line 1806
    p_samples = CustomFloatField(
        label="Size of the test sets",
        default=1
    )
    scoring = CustomMultipleChoiceField(
        choices=ClassificationScoring,
        label="Scoring for the model",
        default="accuracy"
    )
    # TODO: workflow_meta line 1830-1837
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        default="Grid search",
    )
    # TODO: workflow_meta line 1849
    model_selection_scoring = CustomChoiceField(
        choices=ClassificationScoring,
        label="Select a scoring for identifying the best estimator following a grid search",
        default="accuracy",
    )
    n_estimators = CustomFloatField(
        label="The number of trees in the forest",
        min_value=1,
        step_size=1,
        default=100
    )
    criterion = CustomMultipleChoiceField(
        choices=ClusteringCriterion,
        label="The function to measure the quality of a split",
        default="gini",
    )
    max_depth = CustomFloatField(
        label="The maximum depth of the tree",
        min_value=1,
        default=1
    )
    random_state = CustomFloatField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        default=6,
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class ClassificationSVM(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Choose dataframe to be plotted",
        default=[None, None],
    )
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(label="Choose labels column from metadata")
    positive_label = CustomChoiceField(label="Choose positive class")
    test_size = CustomFloatField(
        label="Test size",
        min_value=0,
        default=0.20)
    split_stratify = CustomChoiceField(
        choices=YesNo,
        label="Stratify the split",
        default="Yes"
    )
    # TODO: Validation strategy
    validatation_strategy = CustomChoiceField(choices=ClassificationValidationStrategy)
    train_val_split = CustomFloatField(
        label="Choose the size of the validation data set (you can either enter the absolute number of validation samples or a number between 0.0 and 1.0 to represent the percentage of validation samples)",
        default=0.20,
    )
    # TODO: Workflow_meta line 1973
    n_splits = CustomFloatField(
        label="Number of folds",
        min_value=2,
        default=5)
    # TODO: workflow_meta line 1984-1989
    shuffle = CustomChoiceField(
        choices=YesNo,
        label="Whether to shuffle the data before splitting into batches",
        default="Yes",
    )
    # TODO: workflow_meta line 1994
    n_repeats = CustomFloatField(
        label="Number of times cross-validator needs to be repeated",
        min_value=1,
        default=10,
    )
    # TODO: workflow_meta line 2004
    random_state_cv = CustomFloatField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        default=42,
    )
    p_samples = CustomFloatField(
        label="Size of the test sets",
        default=1
    )
    scoring = CustomMultipleChoiceField(
        choices=ClassificationScoring,
        label="Scoring for the model",
        default="accuracy"
    )
    # TODO: workflow_meta line 2033-2040
    model_selection = CustomChoiceField(
        choices=ModelSelection,
        label="Choose strategy to perform parameter fine-tuning",
        default="Grid search",
    )
    # TODO: workflow_meta line 2059
    C = CustomFloatField(
        label="C: regularization parameter (the strength of the regularization is inversely proportional to C)",
        min_value=0.0,
        default=1.0,
    )
    kernel = CustomMultipleChoiceField(
        choices=ClassificationKernel,
        label="Specifies the kernel type to be used in the algorithm",
        default="linear",
    )
    tolerance = CustomFloatField(
        label="Tolerance for stopping criterion",
        min_value=0.0,
        default=1e-4
    )
    random_state = CustomFloatField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        default=6,
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class ModelEvaluationClassificationModel(MethodForm):
    # TODO: Input_dict
    scoring = CustomMultipleChoiceField(
        choices=ClassificationScoring,
        label="Scoring for the model",
        default="accuracy"
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class DimensionReductionTSNE(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Dimension reduction of a dataframe using t-SNE",
        default=[None, None],
    )
    n_components = CustomFloatField(
        label="Dimension of the embedded space",
        min_value=1,
        step_size=1,
        default=2
    )
    perplexity = CustomFloatField(
        label="Perplexity",
        min_value=5.0,
        max_value=50.0,
        default=30.0
    )
    metric = CustomMultipleChoiceField(
        choices=DimensionReductionMetric,
        label="Metric",
        default="euclidean"
    )
    random_state = CustomFloatField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        default=6,
    )
    n_iter = CustomFloatField(
        label="Maximum number of iterations for the optimization",
        min_value=250,
        default=1000,
    )
    n_iter_without_progress = CustomFloatField(
        label="Maximum number of iterations without progress before we abort the optimization",
        min_value=250,
        step_size=1,
        default=300,
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class DimensionReductionUMAP(MethodForm):
    input_df = CustomChoiceField(
        choices=AnalysisLevel,
        label="Dimension reduction of a dataframe using UMAP",
        default=[None, None],
    )
    n_neighbors = CustomFloatField(
        label="The size of local neighborhood (in terms of number of neighboring sample points) used for manifold approximation",
        min_value=2,
        max=100,
        step_size=1,
        default=15,
    )
    n_components = CustomFloatField(
        label="Number of components",
        min_value=1,
        step_size=1,
        default=2
    )
    min_dist = CustomFloatField(
        label="The minimum distance between embedded points",
        min_value=0.1,
        step_size=0.1,
        default=0.1,
    )
    metric = CustomMultipleChoiceField(
        choices=DimensionReductionMetric,
        label="Metric",
        default="euclidean"
    )
    random_state = CustomFloatField(
        label="Seed for random number generation",
        min_value=0,
        max_value=4294967295,
        step_size=1,
        default=42,
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class ProteinGraph(MethodForm):
    protein_ID = CustomCharField(
        label="Protein ID",
        placeholder="Enter the Uniprot-ID of the protein"
    )
    # TODO: workflow_meta line 2255 - 2263
    k = CustomFloatField(
        label="k-mer length",
        min_value=1,
        step_size=1,
        default=5)
    allowed_mismatches = CustomFloatField(
        label="Number of allowed mismatched amino acids per peptide. For many allowed mismatches, this can take a long time.",
        min_value=0,
        step_size=1,
        default=2,
    )
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class variationGraph(MethodForm):
    protein_ID = CustomCharField(
        label="Protein ID",
        placeholder="Enter the Uniprot-ID of the protein"
    )
    # TODO: workflow_meta line 2291 - 2295
    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)

