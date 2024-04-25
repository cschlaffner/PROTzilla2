from enum import Enum

from .base import MethodForm
from .custom_fields import (
    CustomCharField,
    CustomChoiceField,
    CustomFloatField,
    CustomNumberField,
)


class EmptyEnum(Enum):
    pass


class LogTransformationBaseType(Enum):
    log2 = "log2"
    log10 = "log10"


class SimpleImputerStrategyType(Enum):
    mean = "mean"
    median = "median"
    most_frequent = "most_frequent"


class ImputationByNormalDistributionSamplingStrategyType(Enum):
    per_protein = "perProtein"
    per_dataset = "perDataset"


class ImputationGraphTypes(Enum):
    boxplot = "Boxplot"
    histogram = "Histogram"


class GroupBy(Enum):
    no_grouping = "None"
    sample = "Sample"
    protein_id = "Protein ID"


class VisualTrasformations(Enum):
    linear = "linear"
    log10 = "log10"


class GraphTypesImputedValues(Enum):
    bar = "Bar chart"
    pie = "Pie chart"


class FilterProteinsBySamplesMissingForm(MethodForm):
    percentage = CustomFloatField(
        label="Percentage of minimum non-missing samples per protein",
        min_value=0,
        max_value=1,
        step_size=0.1,
        initial=0.5,
    )


class FilterByProteinsCountForm(MethodForm):
    deviation_threshold = CustomNumberField(
        label="Number of standard deviations from the median",
        min_value=0,
        initial=2,
    )


class FilterSamplesByProteinsMissingForm(MethodForm):
    percentage = CustomFloatField(
        label="Percentage of minimum non-missing proteins per sample",
        min_value=0,
        max_value=1,
        step_size=0.1,
        initial=0.5,
    )


class FilterSamplesByProteinIntensitiesSumForm(MethodForm):
    deviation_threshold = CustomFloatField(
        label="Number of standard deviations from the median:",
        min_value=0,
        initial=2,
    )


class OutlierDetectionByPCAForm(MethodForm):
    threshold = CustomFloatField(
        label="Threshold for number of standard deviations from the median:",
        min_value=0,
        initial=2,
    )
    number_of_components = CustomNumberField(
        label="Number of components",
        min_value=2,
        max_value=3,
        step_size=1,
        initial=3,
    )


class OutlierDetectionByIsolationForestForm(MethodForm):
    n_estimators = CustomNumberField(
        label="Number of estimators",
        min_value=1,
        step_size=1,
        initial=100,
    )


class OutlierDetectionByLocalOutlierFactorForm(MethodForm):
    number_of_neighbors = CustomNumberField(
        label="Number of neighbours",
        min_value=1,
        step_size=1,
        initial=20,
    )


class OutlierDetectionByPCAForm(MethodForm):
    threshold = CustomFloatField(
        label="Threshold for number of standard deviations from the median:",
        min_value=0,
        initial=2,
    )
    number_of_components = CustomNumberField(
        label="Number of components",
        min_value=2,
        max_value=3,
        step_size=1,
        initial=3,)

class OutlierDetectionByIsolationForestForm(MethodForm):
    n_estimators = CustomNumberField(
        label="Number of estimators",
        min_value=1,
        step_size=1,
        initial=100,
    )


class OutlierDetectionByLocalOutlierFactorForm(MethodForm):
    number_of_neighbors = CustomNumberField(
        label="Number of neighbours",
        min_value=1,
        step_size=1,
        initial=20,
    )


class TransformationLogForm(MethodForm):
    log_base = CustomChoiceField(
        choices=LogTransformationBaseType,
        label="Log transformation base:",
        initial=LogTransformationBaseType.log2,
    )


class NormalisationByZScoreForm(MethodForm):
    pass


class NormalisationByTotalSumForm(MethodForm):
    pass


class NormalisationByMedianForm(MethodForm):
    percentile = CustomFloatField(
        label="Percentile for normalisation:",
        min_value=0,
        max_value=1,
        step_size=0.1,
        initial=0.5,
    )


class NormalisationByReferenceProteinForms(MethodForm):
    reference_protein = CustomCharField(
        label="A function to perform protein-intensity normalisation in reference to "
        "a selected protein on your dataframe. Normalises the data on the level "
        "of each sample. Divides each intensity by the intensity of the chosen "
        "reference protein in each sample. Samples where this value is zero "
        "will be removed and returned separately.A function to perform "
        "protein-intensity normalisation in reference to a selected protein on "
        "your dataframe. Normalises the data on the level of each sample. "
        "Divides each intensity by the intensity of the chosen reference "
        "protein in each sample. Samples where this value is zero will be "
        "removed and returned separately."
    )


class ImputationByMinPerDatasetForm(MethodForm):
    shrinking_value = CustomNumberField(
        label="A function to impute missing values for each protein by taking into account "
        "data from the entire dataframe. Sets missing value to the smallest measured "
        "value in the dataframe. The user can also assign a shrinking factor to take a "
        "fraction of that minimum value for imputation.",
        min_value=0,
        max_value=1,
        step_size=0.1,
        initial=0.5,
    )


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomFloatField(label="Shrinking value")


class ImputationByMinPerProteinForm(MethodForm):
    shrinking_value = CustomFloatField(
        label="A function to impute missing values for each protein by taking into account data from each protein. "
        "Sets missing value to the smallest measured value for each protein column. The user can also assign a "
        "shrinking factor to take a fraction of that minimum value for imputation. CAVE: All proteins without "
        "any values will be filtered out.",
        min_value=0,
        max_value=1,
        step_size=0.1,
        initial=0.5,
    )


class ImputationByMinPerSampleForms(MethodForm):
    shrinking_value = CustomFloatField(
        label="Sets missing intensity values to the smallest measured value for each sample",
        min_value=0,
        max_value=1,
        step_size=0.1,
        initial=0.5,
    )


class SimpleImputationPerProteinForm(MethodForm):
    strategy = CustomChoiceField(
        choices=SimpleImputerStrategyType,
        label="Strategy",
        initial=SimpleImputerStrategyType.mean,
    )


class ImputationByKNNForms(MethodForm):
    number_of_neighbours = CustomNumberField(
        label="Number of neighbours",
        min_value=1,
        step_size=1,
        initial=5,
    )


class ImputationByNormalDistributionSamplingForm(MethodForm):
    strategy = CustomChoiceField(
        choices=ImputationByNormalDistributionSamplingStrategyType,
        label="Strategy",
        initial=ImputationByNormalDistributionSamplingStrategyType.per_protein,
    )
    down_shift = CustomNumberField(
        label="Downshift",
        min_value=-10,
        max_value=10,
        initial=-1
    )
    scaling_factor = CustomFloatField(
        label="Scaling factor",
        min_value=0,
        max_value=1,
        step_size=0.1,
        initial=0.5
    )


class FilterPeptidesByPEPThresholdForm(MethodForm):
    threshold = CustomFloatField(
        label="Threshold value for PEP",
        min_value=0,
        initial=0
    )
    peptide_df = CustomChoiceField(
        choices=EmptyEnum,
        label="peptide_df"
    )


class ImputationMinPerProteinPlotForm(MethodForm):
    graph_type = CustomChoiceField(choices=ImputationGraphTypes, label="Graph type")

    group_by = CustomChoiceField(choices=GroupBy, label="Group by")

    visual_transformation = CustomChoiceField(
        VisualTrasformations, label="Visual transformation"
    )

    graph_type_quantities = CustomChoiceField(
        GraphTypesImputedValues, label="Graph type - quantity of imputed values"
    )
