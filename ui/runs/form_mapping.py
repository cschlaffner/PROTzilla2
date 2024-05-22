from django.http import HttpRequest

import protzilla.methods.data_analysis as data_analysis
import protzilla.methods.data_integration as data_integration
import protzilla.methods.data_preprocessing as data_preprocessing
import protzilla.methods.importing as importing
import ui.runs.forms.data_analysis as data_analysis_forms
import ui.runs.forms.data_integration as data_integration_forms
import ui.runs.forms.data_preprocessing as data_preprocessing_forms
import ui.runs.forms.importing as importing_forms
from protzilla.run_v2 import Run
from protzilla.steps import Step

from .forms.base import MethodForm

_forward_mapping = {
    importing.MaxQuantImport: importing_forms.MaxQuantImportForm,
    importing.DiannImport: importing_forms.DiannImportForm,
    importing.MsFraggerImport: importing_forms.MSFraggerImportForm,
    importing.MetadataImport: importing_forms.MetadataImportForm,
    importing.MetadataImportMethodDiann: importing_forms.MetadataImportMethodDiannForm,
    importing.MetadataColumnAssignment: importing_forms.MetadataColumnAssignmentForm,
    importing.PeptideImport: importing_forms.PeptideImportForm,
    data_preprocessing.FilterProteinsBySamplesMissing: data_preprocessing_forms.FilterProteinsBySamplesMissingForm,
    data_preprocessing.FilterByProteinsCount: data_preprocessing_forms.FilterByProteinsCountForm,
    data_preprocessing.FilterSamplesByProteinsMissing: data_preprocessing_forms.FilterSamplesByProteinsMissingForm,
    data_preprocessing.FilterSamplesByProteinIntensitiesSum: data_preprocessing_forms.FilterSamplesByProteinIntensitiesSumForm,
    data_preprocessing.OutlierDetectionByPCA: data_preprocessing_forms.OutlierDetectionByPCAForm,
    data_preprocessing.OutlierDetectionByLocalOutlierFactor: data_preprocessing_forms.OutlierDetectionByLocalOutlierFactorForm,
    data_preprocessing.OutlierDetectionByIsolationForest: data_preprocessing_forms.OutlierDetectionByIsolationForestForm,
    data_preprocessing.TransformationLog: data_preprocessing_forms.TransformationLogForm,
    data_preprocessing.NormalisationByZScore: data_preprocessing_forms.NormalisationByZScoreForm,
    data_preprocessing.NormalisationByTotalSum: data_preprocessing_forms.NormalisationByTotalSumForm,
    data_preprocessing.NormalisationByMedian: data_preprocessing_forms.NormalisationByMedianForm,
    data_preprocessing.NormalisationByReferenceProtein: data_preprocessing_forms.NormalisationByReferenceProteinForms,
    data_preprocessing.ImputationByMinPerDataset: data_preprocessing_forms.ImputationByMinPerDatasetForm,
    data_preprocessing.ImputationByMinPerProtein: data_preprocessing_forms.ImputationByMinPerProteinForm,
    data_preprocessing.SimpleImputationPerProtein: data_preprocessing_forms.SimpleImputationPerProteinForm,
    data_preprocessing.ImputationByKNN: data_preprocessing_forms.ImputationByKNNForms,
    data_preprocessing.ImputationByNormalDistributionSampling: data_preprocessing_forms.ImputationByNormalDistributionSamplingForm,
    data_preprocessing.FilterPeptidesByPEPThreshold: data_preprocessing_forms.FilterPeptidesByPEPThresholdForm,
    data_analysis.DifferentialExpressionANOVA: data_analysis_forms.DifferentialExpressionANOVAForm,
    data_analysis.DifferentialExpressionTTest: data_analysis_forms.DifferentialExpressionTTestForm,
    data_analysis.DifferentialExpressionLinearModel: data_analysis_forms.DifferentialExpressionLinearModelForm,
    data_analysis.PlotVolcano: data_analysis_forms.PlotVolcanoForm,
    data_analysis.PlotScatterPlot: data_analysis_forms.PlotScatterPlotForm,
    data_analysis.PlotClustergram: data_analysis_forms.PlotClustergramForm,
    data_analysis.PlotProtQuant: data_analysis_forms.PlotProtQuantForm,
    data_analysis.PlotPrecisionRecallCurve: data_analysis_forms.PlotPrecisionRecallCurveForm,
    data_analysis.PlotROC: data_analysis_forms.PlotROCCurveForm,
    data_analysis.ClusteringKMeans: data_analysis_forms.ClusteringKMeansForm,
    data_analysis.ClusteringExpectationMaximisation: data_analysis_forms.ClusteringExpectationMaximizationForm,
    data_analysis.ClusteringHierarchicalAgglomerative: data_analysis_forms.ClusteringHierarchicalAgglomerativeClusteringForm,
    data_analysis.ClassificationRandomForest: data_analysis_forms.ClassificationRandomForestForm,
    data_analysis.ClassificationSVM: data_analysis_forms.ClassificationSVMForm,
    data_analysis.ModelEvaluationClassificationModel: data_analysis_forms.ModelEvaluationClassificationModelForm,
    data_analysis.DimensionReductionTSNE: data_analysis_forms.DimensionReductionTSNEForm,
    data_analysis.DimensionReductionUMAP: data_analysis_forms.DimensionReductionUMAPForm,
    data_analysis.ProteinGraphPeptidesToIsoform: data_analysis_forms.ProteinGraphPeptidesToIsoformForm,
    data_analysis.ProteinGraphVariationGraph: data_analysis_forms.ProteinGraphVariationGraphForm,
    data_preprocessing.ImputationByMinPerSample: data_preprocessing_forms.ImputationByMinPerSampleForms,
    data_integration.EnrichmentAnalysisGOAnalysisWithString: data_integration_forms.EnrichmentAnalysisGOAnalysisWithStringForm,
    data_integration.EnrichmentAnalysisGOAnalysisWithEnrichr: data_integration_forms.EnrichmentAnalysisGOAnalysisWithEnrichrForm,
    data_integration.EnrichmentAnalysisGOAnalysisOffline: data_integration_forms.EnrichmentAnalysisGOAnalysisOfflineForm,
    data_integration.EnrichmentAnalysisWithGSEA: data_integration_forms.EnrichmentAnalysisWithGSEAForm,
    data_integration.EnrichmentAnalysisWithPrerankedGSEA: data_integration_forms.EnrichmentAnalysisWithPrerankedGSEAForm,
    data_integration.DatabaseIntegrationByGeneMapping: data_integration_forms.DatabaseIntegrationByGeneMappingForm,
    data_integration.DatabaseIntegrationByUniprot: data_integration_forms.DatabaseIntegrationByUniprotForm,
    data_integration.PlotGOEnrichmentBarPlot: data_integration_forms.PlotGOEnrichmentBarPlotForm,
    data_integration.PlotGOEnrichmentDotPlot: data_integration_forms.PlotGOEnrichmentDotPlotForm,
    data_integration.PlotGSEADotPlot: data_integration_forms.PlotGSEADotPlotForm,
    data_integration.PlotGSEAEnrichmentPlot: data_integration_forms.PlotGSEAEnrichmentPlotForm,
}

_forward_mapping_plots = {
    data_preprocessing.FilterProteinsBySamplesMissing: data_preprocessing_forms.FilterProteinsBySamplesMissingPlotForm,
    data_preprocessing.FilterByProteinsCount: data_preprocessing_forms.FilterByProteinsCountPlotForm,
    data_preprocessing.FilterSamplesByProteinsMissing: data_preprocessing_forms.FilterSamplesByProteinsMissingPlotForm,
    data_preprocessing.FilterSamplesByProteinIntensitiesSum: data_preprocessing_forms.FilterSamplesByProteinIntensitiesSumPlotForm,
    data_preprocessing.TransformationLog: data_preprocessing_forms.TransformationLogPlotForm,
    data_preprocessing.NormalisationByZScore: data_preprocessing_forms.NormalisationByZscorePlotForm,
    data_preprocessing.NormalisationByTotalSum: data_preprocessing_forms.NormalisationByTotalSumPlotForm,
    data_preprocessing.NormalisationByMedian: data_preprocessing_forms.NormalisationByMedianPlotForm,
    data_preprocessing.NormalisationByReferenceProtein: data_preprocessing_forms.NormalisationByReferenceProteinPlotForm,
    data_preprocessing.ImputationByMinPerDataset: data_preprocessing_forms.ImputationByMinPerDatasetPlotForm,
    data_preprocessing.ImputationByMinPerProtein: data_preprocessing_forms.ImputationByMinPerProteinPlotForm,
    data_preprocessing.ImputationByMinPerSample: data_preprocessing_forms.ImputationByMinPerSamplePlotForm,
    data_preprocessing.SimpleImputationPerProtein: data_preprocessing_forms.SimpleImputationPerProteinPlotForm,
    data_preprocessing.ImputationByKNN: data_preprocessing_forms.ImputationByKNNPlotForm,
    data_preprocessing.ImputationByNormalDistributionSampling: data_preprocessing_forms.ImputationByNormalDistributionSamplingPlotForm,
    data_preprocessing.FilterPeptidesByPEPThreshold: data_preprocessing_forms.FilterPeptidesByPEPThresholdPlotForm,
}


_reverse_mapping = {v: k for k, v in _forward_mapping.items()}


def generate_hierarchical_dict() -> dict[str, dict[str, dict[str, type[Step]]]]:
    # Initialize an empty dictionary
    hierarchical_dict = {}

    # List of all Step subclasses
    step_classes = _forward_mapping.keys()

    # Iterate over each Step subclass
    for step_class in step_classes:
        # Create a nested dictionary with keys being the section, step, and method
        # and the value being the class itself
        if step_class.section not in hierarchical_dict:
            hierarchical_dict[step_class.section] = {}
        if step_class.operation not in hierarchical_dict[step_class.section]:
            hierarchical_dict[step_class.section][step_class.operation] = {}
        hierarchical_dict[step_class.section][step_class.operation][
            step_class.__name__
        ] = step_class

    return hierarchical_dict


def _get_form_class_by_step(step: Step) -> type[MethodForm]:
    form_class = _forward_mapping.get(type(step))
    if form_class:
        return form_class
    else:
        raise ValueError(f"No form has been provided for {type(step).__name__} step.")


def _get_plot_form_class_by_step(step: Step) -> type[MethodForm]:
    return _forward_mapping_plots.get(type(step))


def _get_step_class_by_form(form: MethodForm) -> type[Step]:
    step_class = _reverse_mapping.get(type(form))
    if step_class:
        return step_class
    else:
        raise ValueError(f"No step has been provided for {type(form).__name__} form.")


def get_empty_form_by_method(step: Step, run: Run) -> MethodForm:
    return _get_form_class_by_step(step)(run=run)


def get_empty_plot_form_by_method(step: Step, run: Run) -> MethodForm:
    plot_form_class = _get_plot_form_class_by_step(step)
    return plot_form_class(run=run) if plot_form_class else None


def get_filled_form_by_method(
    step: Step, run: Run, in_history: bool = False
) -> MethodForm:
    form_class = _get_form_class_by_step(step)
    return form_class(
        run=run,
        readonly=in_history,
        data=step.form_inputs if bool(step.form_inputs) else None,
    )


def get_filled_form_by_request(request: HttpRequest, run: Run) -> MethodForm:
    form_class = _get_form_class_by_step(run.current_step)
    return form_class(run=run, data=request.POST, files=request.FILES)


def get_all_methods() -> list[type[Step]]:
    return list(_forward_mapping.keys())
