from enum import Enum

from .base import MethodForm
from .custom_fields import (
    CustomCharField,
    CustomChoiceField,
    CustomFloatField,
    CustomNumberInput,
)


class EmptyEnum(Enum):
    pass


class LogTransformationBaseType(Enum):
    LOG2 = "log2"
    LOG10 = "log10"


class SimpleImputerStrategyType(Enum):
    MEAN = "mean"
    MEDIAN = "median"
    MOST_FREQUENT = "most_frequent"


class ImputationByNormalDistributionSamplingStrategyType(Enum):
    PERPROTEIN = "perProtein"
    PERDATASET = "perDataset"


class ImputationGraphTypes(Enum):
    Boxplot = "Boxplot"
    Histogram = "Histogram"


class GroupBy(Enum):
    NoGrouping = "None"
    Sample = "Sample"
    ProteinID = "Protein ID"


class VisualTrasformations(Enum):
    linear = "linear"
    Log10 = "log10"


class GraphTypesImputedValues(Enum):
    Bar = "Bar chart"
    Pie = "Pie chart"


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomFloatField(label="Shrinking value")


class FilterProteinsBySamplesMissingForm(MethodForm):
    percentage = CustomFloatField(
        label="Percentage of minimum non-missing samples per protein"
    )


class FilterByProteinsCountForm(MethodForm):
    deviation_threshold = CustomFloatField(
        label="Number of standard deviations from the median"
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
    shrinking_value = CustomFloatField(
        label="A function to impute missing values for each protein by taking into account "
        "data from the entire dataframe. Sets missing value to the smallest measured "
        "value in the dataframe. The user can also assign a shrinking factor to take a "
        "fraction of that minimum value for imputation."
    )


class ImputationByMinPerProteinForm(MethodForm):
    shrinking_value = CustomFloatField(
        label="A function to impute missing values for each protein by taking into account data from each protein. "
        "Sets missing value to the smallest measured value for each protein column. The user can also assign a "
        "shrinking factor to take a fraction of that minimum value for imputation. CAVE: All proteins without "
        "any values will be filtered out."
    )


class ImputationByMinPerSampleForms(MethodForm):
    shrinking_value = CustomFloatField(
        label="Sets missing intensity values to the smallest measured value for each sample"
    )


class FilterSamplesByProteinsMissingForm(MethodForm):
    percentage = CustomFloatField(
        label="Percentage of minimum non-missing proteins per sample"
    )


class FilterSamplesByProteinIntensitiesSumForm(MethodForm):
    deviation_threshold = CustomFloatField(
        label="Number of standard deviations from the median:"
    )


class OutlierDetectionByPCAForm(MethodForm):
    threshold = CustomFloatField(
        label="Threshold for number of standard deviations from the median:"
    )
    number_of_components = CustomNumberInput(label="Number of components")


class OutlierDetectionByLocalOutlierFactorForm(MethodForm):
    number_of_neighbors = CustomNumberInput(label="Number of neighbours")


class OutlierDetectionByIsolationForestForm(MethodForm):
    n_estimators = CustomNumberInput(label="Number of estimators")


class TransformationLogForm(MethodForm):
    log_base = CustomChoiceField(
        choices=LogTransformationBaseType, label="Log transformation base:"
    )


class NormalisationByZScoreForm(MethodForm):
    pass


class NormalisationByTotalSumForm(MethodForm):
    pass


class NormalisationByMedianForm(MethodForm):
    percentile = CustomFloatField(label="Percentile for normalisation:")


class SimpleImputationPerProteinForm(MethodForm):
    strategy = CustomChoiceField(choices=SimpleImputerStrategyType, label="Strategy")


class ImputationByKNNForms(MethodForm):
    number_of_neighbours = CustomNumberInput(label="Number of neighbours")


class ImputationByNormalDistributionSamplingForm(MethodForm):
    strategy = CustomChoiceField(
        choices=ImputationByNormalDistributionSamplingStrategyType, label="Strategy"
    )
    down_shift = CustomFloatField(label="Downshift")
    scaling_factor = CustomFloatField(label="Scaling factor")


class FilterPeptidesByPEPThresholdForm(MethodForm):
    threshold = CustomFloatField(label="Threshold value for PEP")
    peptide_df = CustomChoiceField(choices=EmptyEnum, label="peptide_df")


class ImputationMinPerProteinPlotForm(MethodForm):
    graph_type = CustomChoiceField(choices=ImputationGraphTypes, label="Graph type")

    group_by = CustomChoiceField(choices=GroupBy, label="Group by")

    visual_transformation = CustomChoiceField(
        VisualTrasformations, label="Visual transformation"
    )

    graph_type_quantities = CustomChoiceField(
        GraphTypesImputedValues, label="Graph type - quantity of imputed values"
    )
