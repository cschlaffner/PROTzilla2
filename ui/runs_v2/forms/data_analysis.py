from enum import Enum

from protzilla.run_v2 import Run
from .base import MethodForm
from .custom_fields import CustomChoiceField, CustomFloatField, CustomMultipleChoiceField, CustomCharField


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
    #TODO: Add the proteins of interest

class DynamicProteinFill(Enum):
    #TODO: Add the dynamic protein fill options

class SimilarityMeasure(Enum):
    euclidean_distance = "Euclidean distance"
    cosine_similarity = "Cosine similarity"

class ClusteringModelSelection(Enum):
    grid_search = "Grid search"
    randomized_search = "Randomized search"
    Manual = "Manual"

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



class DifferentialExpression_ANOVA(MethodForm):
    multiple_testing_correction = CustomChoiceField(
        choices=MultipelTestingCorrectionMethod, label="Multiple esting correction", default="Benjamini-Hochberg"
    )

    alpha = CustomFloatField(label="Error rate (alpha)", min_value=0, max_value=1, default=0.05)

    log_base = CustomChoiceField(choices=LogBase, label="Base of the log transformation", default="log2")

    grouping = "Put a usefull default here"

    selected_groups = "Put a usefull default here"

    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)
class DifferentialExpression_TTestForm(MethodForm):
    ttest_type = CustomChoiceField(choices=TTestType, label="T-test type")

    # intensity_df = CustomChoiceField(
    #    choices=AnalysisLevel, label="Intensitys"
    # )

    multiple_testing_correction = CustomChoiceField(
        choices=MultipelTestingCorrectionMethod, label="Multiple testing correction", default="Benjamini-Hochberg"
    )

    alpha = CustomFloatField(label="Alpha")

    log_base = CustomChoiceField(choices=LogBase, label="Log base")

    grouping = "Put a usefull default here"

    group1 = "Put a usefull default here"

    group2 = "Put a usefull default here"

class DifferentialExpression_LinearModel(MethodForm):
    multiple_testing_correction = CustomChoiceField(
        choices=MultipelTestingCorrectionMethod, label="Multiple testing correction", default="Benjamini-Hochberg"
    )
    alpha = CustomFloatField(label="Error rate (alpha)", min_value=0, max_value=1, default=0.05)
    log_base = CustomChoiceField(choices=LogBase, label="Base of the log transformation", default="log2")
    grouping = "Put a usefull default here"
    group1 = "Put a usefull default here"
    group2 = "Put a usefull default here"

class PlotVolcano(MethodForm):
    input_dict = "Put a usefull default here"
    fc_threshold = CustomFloatField(label="log 2 fold change threshold", min_value=0, default=0)
    proteins_of_interest = CustomMultipleChoiceField(choices=ProteinsOfInterest, label="Proteins of interest", default = None)

class PlotScatterPlot(MethodForm):
    input_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be plotted", default=[None, None])
    color_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be used for coloring", default=[None, None], required=False)

class PlotClustergram(MethodForm):
    input_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be plotted", default=[None, None])
    sample_group_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be used for coloring", default=[None, None], required=False)
    flip_axis = CustomChoiceField(choices=YesNo, label="Flip axis", default="No")

class PlotProtQuant(MethodForm):
    input_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be plotted", default=[None, None])
    protein_group = CustomChoiceField(choices=DynamicProteinFill, label="Protein group: choose highlighted protein group", default=None)
    similarity_measure = CustomChoiceField(choices=SimilarityMeasure, label="Similarity Measurement: choose how to compare protein groups", default="Euclidean distance")
    similarity = CustomFloatField(label="Similarity", min_value=-1, max_value=999, step_size=1, default = 1)

class Plotprecision_recall_curve(MethodForm):
    input_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be plotted", default=[None, None])
    plot_title = CustomCharField(label="Title of the plot (optional)", default="Precision-Recall Curve")

class ClusteringKMeans(MethodForm):
    input_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be plotted", default=[None, None])
    #TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(label="Choose labels column from metadata")
    positive_label = CustomChoiceField(label="Choose positive class")
    model_selection = CustomChoiceField(choices=ClusteringModelSelection, label="Choose strategy to perform parameter fine-tuning", default="Grid search")
    #TODO: Add dynamic parameters for grid search & randomized search
    #TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(choices=ClusteringScoring, label="Select a scoring for identifying the best estimator following a grid search", default="Adjusted Rand Score" , dynamic = True)
    scoring = CustomMultipleChoiceField(choices=ClusteringScoring, label="Scoring for the model", default="Adjusted Rand Score")
    #TODO: workflow_meta line 1375
    n_clusters = CustomFloatField(label="Number of clusters to find", min_value=1, step_size=1, default=8)
    # TODO: workflow_meta line 1384
    random_state = CustomFloatField(label="Seed for centroid initialisation", min_value=0, max_value=4294967295, step_size=1, default=0)
    init_centroid_strategy = CustomMultipleChoiceField(choices=InitCentroidStrategy, label="Method for initialisation of centroids", default="random")
    #TODO: workflow_meta line 1402
    n_init = CustomFloatField(label="Number of times the k-means algorithm is run with different centroid seeds", min_value=1, step_size=1, default=10)
    #TODO: workflow_meta line 1410
    max_iter = CustomFloatField(label="Maximum number of iterations of the k-means algorithm for a single run", min_value=1, step_size=1, default=300)
    #TODO: workflow_meta line 1417
    tolerance = CustomFloatField(label="Relative tolerance with regards to Frobenius norm", min_value=0, default=1e-4)

class ClusteringExpectationMaximization(MethodForm):
    input_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be plotted", default=[None, None])
    input_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be plotted", default=[None, None])
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(label="Choose labels column from metadata")
    positive_label = CustomChoiceField(label="Choose positive class")
    model_selection = CustomChoiceField(choices=ClusteringModelSelection, label="Choose strategy to perform parameter fine-tuning", default="Grid search")
    # TODO: Add dynamic parameters for grid search & randomized search
    # TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(choices=ClusteringScoring, label="Select a scoring for identifying the best estimator following a grid search", default="Adjusted Rand Score", dynamic=True)
    scoring = CustomMultipleChoiceField(choices=ClusteringScoring, label="Scoring for the model", default="Adjusted Rand Score")
    #TODO: workflow_meta line 1509
    n_components = CustomFloatField(label="The number of mixture components", default=1)
    #TODO: workflow_meta line 1515
    reg_covar = CustomFloatField(label="Non-negative regularization added to the diagonal of covariance", min_value=0, default=1e-6)
    covariance_type = CustomMultipleChoiceField(choices=ClusteringCovarianceType, label="Type of covariance", default="full")
    init_params = CustomMultipleChoiceField(choices=ClusteringInitParams, label="The method used to initialize the weights, the means and the precisions.", default="kmeans")
    max_iter = CustomFloatField(label="The number of EM iterations to perform", default=100)
    random_state = CustomFloatField(label="Seed for random number generation", min_value=0, max_value=4294967295, step_size=1, default=0)

class ClusteringHierarchicalAgglomerativeClustering(MethodForm):
    input_df = CustomChoiceField(choices=AnalysisLevel, label="Choose dataframe to be plotted", default=[None, None])
    # TODO: Add dynamic fill for labels_column & positive_label
    labels_column = CustomChoiceField(label="Choose labels column from metadata")
    positive_label = CustomChoiceField(label="Choose positive class")
    model_selection = CustomChoiceField(choices=ClusteringModelSelection, label="Choose strategy to perform parameter fine-tuning", default="Grid search")
    # TODO: Add dynamic parameters for grid search & randomized search
    # TODO Add dynamic parameter for model selection scoring
    model_selection_scoring = CustomChoiceField(choices=ClusteringScoring, label="Select a scoring for identifying the best estimator following a grid search", default="Adjusted Rand Score", dynamic=True)
    scoring = CustomMultipleChoiceField(choices=ClusteringScoring, label="Scoring for the model", default="Adjusted Rand Score")
    #TODO: workflow_meta line 1647
    n_clusters = CustomFloatField(label="The number of clusters to find", min_value=1, step_size=1, default=2)
    metric = CustomMultipleChoiceField(choices=ClusteringMetric, label="Distance metric", default="euclidean")
    linkage = CustomMultipleChoiceField(choices=ClusteringLinkage, label="The linkage criterion to use in order to to determine the distance to use between sets of observation", default="ward")




    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)
