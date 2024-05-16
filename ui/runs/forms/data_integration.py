from enum import Enum

import gseapy
import matplotlib.colors as mcolors
import restring

from protzilla.constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE
from protzilla.data_integration.database_query import (
    biomart_database,
    uniprot_databases,
)
from protzilla.run_v2 import Run
from protzilla.steps import Step

from . import fill_helper
from .base import MethodForm
from .custom_fields import (
    CustomBooleanField,
    CustomCharField,
    CustomChoiceField,
    CustomFileField,
    CustomFloatField,
    CustomMultipleChoiceField,
    CustomNumberField,
)

PROTEIN_DF = "protein_df"
DIFFERENTIALLY_EXPRESSED_PROTEINS_DF = "differentially_expressed_proteins_df"


class Direction(Enum):
    up = "up"
    down = "down"
    both = "both"


class GeneSetsField(Enum):
    upload_a_file = "Upload a file"
    choose_from_enrichr_options = "Choose from Enrichr options"


class Organism(Enum):
    human = "Human"
    mouse = "Mouse"
    rat = "Rat"
    yeast = "Yeast"
    fly = "Fly"
    fish = "Fish"
    worm = "Worm"


class PermutationTypeField(Enum):
    phenotype = "Phenotype"
    gene_set = "Gene Set"


class RankingMethodField(Enum):
    log2_ratio_of_classes = "Log2 Ratio of classes"
    signal_to_noise = "Signal to noise"
    t_test = "t-Test"
    ratio_of_classes = "Ratio of classes"
    diff_of_classes = "Difference of classes"


class RankingDirectionField(Enum):
    ascending = "ascending"
    descending = "descending"


class GOAnalysisWithEnrichrBackgroundField(Enum):
    upload_a_file = "Upload a file (recommended)"
    choose_biomart_dataset = "Choose Biomart dataset"
    number_of_expressed_genes = "Specify number of expressed genes (not recommended)"
    all_genes = "Use all genes in the gene set"


class GOEnrichmentBarPlotValue(Enum):
    p_value = "p-value"
    fdr = "FDR"


class GOEnrichmentDotPlotXAxisType(Enum):
    gene_sets = "Gene Sets"
    combined_score = "Combined Score"


class GSEADotPlotDotColorValue(Enum):
    fdr_q_val = "FDR q-val"
    nom_p_val = "NOM p-val"


class GSEADotPlotXAxisValue(Enum):
    es = "ES"
    nes = "NES"


class PlotColors(Enum):
    PROTzilla_default = PROTZILLA_DISCRETE_COLOR_SEQUENCE


class EmptyEnum(Enum):
    pass


class EnrichmentAnalysisGOAnalysisWithStringForm(MethodForm):
    protein_df = CustomChoiceField(
        choices=[],
        label="Dataframe with protein IDs and direction of expression change column (e.g. "
        "log2FC)",
    )
    differential_expression_threshold = CustomNumberField(
        label="Threshold for differential expression: Proteins with fold change > threshold are upregulated, proteins "
        "fold change < threshold downregulated. Applied symmetrically to log fold changes:",
        min_value=0,
        max_value=4294967295,
        initial=0,
    )
    gene_sets_restring = CustomMultipleChoiceField(
        choices=[], label="Knowledge bases for enrichment"
    )
    organism = CustomNumberField(
        label="Organism / NCBI taxon identifiers (e.g. Human is 9606)", initial=9606
    )
    direction = CustomChoiceField(
        choices=Direction, label="Direction of the analysis", initial=Direction.both
    )
    background_path = CustomFileField(
        label="Background set (no upload = entire proteome), UniProt IDs (one per line, txt or csv)",
        required=False,
    )

    def fill_form(self, run: Run) -> None:
        self.fields["protein_df"].choices = fill_helper.get_choices(
            run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
        )  # TODO maybe a step type? and maybe rename protein_df to something better

        self.fields["gene_sets_restring"].choices = fill_helper.to_choices(
            restring.settings.file_types
        )


class EnrichmentAnalysisGOAnalysisWithEnrichrForm(MethodForm):
    is_dynamic = True
    protein_df_step_instance = CustomChoiceField(
        choices=[],
        label="Dataframe with protein IDs and direction of expression change column (e.g. "
        "log2FC)",
    )
    differential_expression_threshold = CustomNumberField(
        label="Threshold for differential expression: Proteins with fold change > threshold are upregulated, proteins "
        "fold change < threshold downregulated. Applied symmetrically to log fold changes:",
        min_value=0,
        max_value=4294967295,
        initial=0,
    )
    gene_mapping_step_instance = CustomChoiceField(choices=[], label="Gene mapping")
    direction = CustomChoiceField(
        choices=Direction, label="Direction of the analysis", initial=Direction.both
    )
    organism = CustomChoiceField(
        choices=Organism, label="Organism", initial=Organism.human
    )
    gene_sets_field = CustomChoiceField(
        choices=GeneSetsField,
        label="Gene sets",
        initial=GeneSetsField.choose_from_enrichr_options,
    )
    gene_sets_path = CustomFileField(
        label="Upload gene sets with uppercase gene symbols (any of the following file types: .gmt, .txt, .csv, "
        ".json | .txt (one set per line): SetName followed by tab-separated list of proteins | .csv (one set "
        "per line): SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], SetName2: [Gene2, Gene3, "
        "...]})"
    )
    gene_sets_enrichr = CustomChoiceField(choices=[], label="Gene set libraries")
    background_field = CustomChoiceField(
        choices=GOAnalysisWithEnrichrBackgroundField,
        label="Background",
        initial=GOAnalysisWithEnrichrBackgroundField.upload_a_file,
    )
    background_path = CustomFileField(
        label="Background set with uppercase gene symbols (one gene per line, csv or txt)",
        initial=None,
    )
    background_number = CustomNumberField(
        label="Number of expressed genes in the background",
        min_value=1,
        max_value=4294967295,
        step_size=1,
        initial=None,
    )
    background_biomart = CustomChoiceField(choices=[], label="Biomart dataset")

    def fill_form(self, run: Run) -> None:
        self.fields["protein_df_step_instance"].choices = fill_helper.get_choices(
            run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
        )
        self.fields["gene_mapping_step_instance"].choices = fill_helper.get_choices(
            run, "gene_mapping"
        )

        gene_sets_field = self.get_field("gene_sets_field")

        self.data = self.data.copy()
        # reset all the fields visibility
        for field_name in [
            "gene_sets_enrichr",
            "gene_sets_path",
            "background_path",
            "background_number",
            "background_biomart",
        ]:
            self.toggle_visibility(field_name, False)

        if gene_sets_field == GeneSetsField.choose_from_enrichr_options.value:
            self.toggle_visibility("gene_sets_enrichr", True)
            self.fields["gene_sets_enrichr"].choices = fill_helper.to_choices(
                gseapy.get_library_name()
            )  # TODO check whether we need to pass the organism name here
        else:
            self.toggle_visibility("gene_sets_path", True)

        if (
            self.get_field("background_field")
            == GOAnalysisWithEnrichrBackgroundField.choose_biomart_dataset.value
        ):
            self.toggle_visibility("background_biomart", True)
            database = biomart_database("ENSEMBL_MART_ENSEMBL")
            self.fields["background_biomart"].choices = fill_helper.to_choices(
                [
                    database.datasets[dataset].display_name
                    for dataset in database.datasets
                ]
            )
        elif (
            self.get_field("background_field")
            == GOAnalysisWithEnrichrBackgroundField.upload_a_file.value
        ):
            self.toggle_visibility("background_path", True)
        elif (
            self.get_field("background_field")
            == GOAnalysisWithEnrichrBackgroundField.number_of_expressed_genes.value
        ):
            self.toggle_visibility("background_number", True)


class EnrichmentAnalysisGOAnalysisOfflineForm(MethodForm):
    is_dynamic = True
    protein_df_step_instance = CustomChoiceField(
        choices=[],
        label="Dataframe with protein IDs and direction of expression change column (e.g. "
        "log2FC)",
    )
    differential_expression_threshold = CustomNumberField(
        label="Threshold for differential expression: proteins with values > threshold are upregulated, proteins "
        'values < threshold downregulated. If "log" is in the name of differential_expression_col, '
        "threshold is applied symmetrically: e.g. log2_fold_change > threshold is upregulated, "
        "if log2_fold_change < -threshold downregulated",
        min_value=0,
        max_value=4294967295,
        initial=0,
    )
    gene_mapping_step_instance = CustomChoiceField(choices=[], label="Gene mapping")
    gene_sets_path = CustomFileField(
        label="Upload gene sets with uppercase gene symbols (any of the following file "
        "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
        "followed by tab-separated list of proteins | .csv (one set per line): "
        "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
        "SetName2: [Gene2, Gene3, ...]})",
    )
    direction = CustomChoiceField(
        choices=Direction, label="Direction of the analysis", initial=Direction.both
    )
    background_field = CustomChoiceField(
        choices=GOAnalysisWithEnrichrBackgroundField,
        label="How do you want to provide the background set? This parameter works only for uploaded gene sets and "
        "will otherwise be ignored!",
        initial=GOAnalysisWithEnrichrBackgroundField.upload_a_file,
    )
    background_path = CustomFileField(
        label="Background set with uppercase gene symbols (one protein per line, csv or txt)",
        initial=None,
    )
    background_number = CustomNumberField(
        label="Number of expressed genes",
        min_value=1,
        max_value=4294967295,
        step_size=1,
        initial=None,
    )

    def fill_form(self, run: Run) -> None:
        self.fields["protein_df_step_instance"].choices = fill_helper.get_choices(
            run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
        )
        self.fields["gene_mapping_step_instance"].choices = fill_helper.get_choices(
            run, "gene_mapping"
        )

        self.data = self.data.copy()
        for field_name in [
            "background_path",
            "background_number",
        ]:
            self.toggle_visibility(field_name, False)

        if (
            self.get_field("background_field")
            == GOAnalysisWithEnrichrBackgroundField.upload_a_file.value
        ):
            self.toggle_visibility("background_path", True)
        elif (
            self.get_field("background_field")
            == GOAnalysisWithEnrichrBackgroundField.number_of_expressed_genes.value
        ):
            self.toggle_visibility("background_number", True)


class EnrichmentAnalysisWithGSEAForm(MethodForm):
    protein_df = CustomChoiceField(
        choices=[], label="Dataframe with protein IDs, samples and intensities"
    )
    gene_mapping = CustomChoiceField(choices=[], label="Gene mapping")
    gene_sets_field = CustomChoiceField(
        choices=GeneSetsField,
        label="How do you want to provide the gene sets? (reselect to show dynamic fields)",
        initial="Choose from Enrichr options"
        # Todo: Dynamic parameters
    )
    gene_sets_path = CustomFileField(
        label="Upload gene sets with uppercase gene symbols (any of the following file "
        "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
        "followed by tab-separated list of proteins | .csv (one set per line): "
        "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
        "SetName2: [Gene2, Gene3, ...]})",
        initial=None,
    )
    # Todo: gene_sets_enrichr dynamic filling
    gene_sets_enrichr = CustomChoiceField(choices=[], label="Gene sets")
    grouping = CustomChoiceField(
        choices=[],
        label="Grouping from metadata",
        initial=None
        # Todo: Dynamic parameters
    )
    # Todo: add dynamic filling to group1, group2
    group1 = CustomChoiceField(choices=[], label="Group1", initial=None)

    group2 = CustomChoiceField(choices=[], label="Group2", initial=None)

    min_size = CustomNumberField(
        label="Minimum number of genes from gene set also in data", initial=15
    )

    max_size = CustomNumberField(
        label="Maximum number of genes from gene set also in data", initial=500
    )

    number_of_permutations = CustomNumberField(
        label="number_of_permutations", initial=1000
    )

    permutation_type = CustomChoiceField(
        choices=PermutationTypeField,
        label="Permutation type (if samples >=15 set to phenotype)",
        initial=PermutationTypeField.phenotype,
    )

    ranking_method = CustomChoiceField(
        choices=RankingMethodField,
        label="Method to calculate correlation or ranking",
        initial=RankingMethodField.signal_to_noise,
    )

    weighted_score = CustomFloatField(
        label="Weighted score for the enrichment score calculation, recommended values: "
        "0, 1, 1.5 or 2",
        initial=1,
    )

    def fill_form(self, run: Run) -> None:
        self.fields["protein_df"].choices = fill_helper.get_choices(
            run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
        )
        self.fields["gene_mapping"].choices = fill_helper.get_choices(
            run, "gene_mapping"
        )
        protein_df_instance_id = self.data.get(
            "proteins_df", self.fields["protein_df"].choices[0][0]
        )

        gene_sets_field = self.get_field("gene_sets_field")

        self.data = self.data.copy()
        # reset all the fields visibility
        for field_name in [
            "gene_sets_enrichr",
            "gene_sets_path",
        ]:
            self.toggle_visibility(field_name, False)

        if gene_sets_field == GeneSetsField.choose_from_enrichr_options.value:
            self.toggle_visibility("gene_sets_enrichr", True)
            self.fields["gene_sets_enrichr"].choices = fill_helper.to_choices(
                gseapy.get_library_name()
            )  # TODO check whether we need to pass the organism name here
        else:
            self.toggle_visibility("gene_sets_path", True)

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

    @property
    def is_dynamic(self) -> bool:
        return True

    """
    def fill_form(self, run: Run) -> None:
        self.fields["grouping"].choices = fill_helper.get_choices_for_metadata_non_sample_columns(run)
        grouping = self.data.get("grouping", self.fields["grouping"].choices[0][0])
        self.fields["grouping"].choices = fill_helper.to_choices(
            run.steps.metadata_df["group1"].unique()
        )
    """


class EnrichmentAnalysisWithPrerankedGSEAForm(MethodForm):
    # Todo: protein_df
    # Todo: ranking_column
    ranking_direction = CustomChoiceField(
        choices=RankingDirectionField,
        label="Sort the ranking column (ascending - smaller values are better, "
        "descending - larger values are better)",
        initial=RankingDirectionField.ascending,
    )
    # Todo: gene_mapping
    gene_sets_field = CustomChoiceField(
        choices=GeneSetsField,
        label="How do you want to provide the gene sets? (reselect to show dynamic fields)",
        initial=GeneSetsField.choose_from_enrichr_options
        # Todo: Dynamic parameters
    )
    gene_sets_path = CustomFileField(
        label="Upload gene sets with uppercase gene symbols (any of the following file "
        "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
        "followed by tab-separated list of proteins | .csv (one set per line): "
        "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
        "SetName2: [Gene2, Gene3, ...]})",
        initial=None,
    )
    # Todo: gene_sets_enrichr
    min_size = CustomNumberField(
        label="Minimum number of genes from gene set also in data", initial=15
    )

    max_size = CustomNumberField(
        label="Maximum number of genes from gene set also in data", initial=500
    )

    number_of_permutations = CustomNumberField(
        label="number_of_permutations", initial=1000
    )

    permutation_type = CustomChoiceField(
        choices=PermutationTypeField,
        label="Permutation type (if samples >=15 set to phenotype)",
        initial=PermutationTypeField.phenotype,
    )

    ranking_method = CustomChoiceField(
        choices=RankingMethodField,
        label="Method to calculate correlation or ranking",
        initial=RankingMethodField.signal_to_noise,
    )

    weighted_score = CustomFloatField(
        label="Weighted score for the enrichment score calculation, recommended values: "
        "0, 1, 1.5 or 2",
        initial=1,
    )


class DatabaseIntegrationByGeneMappingForm(MethodForm):
    database_names = CustomMultipleChoiceField(
        choices=[],
        label="Uniprot databases (offline)",
    )
    use_biomart = CustomBooleanField(
        label="Use Biomart after Uniprot databases (online)",
        initial=False,
        required=False,
    )
    dataframe = CustomChoiceField(
        choices=[], label="Step to use"
    )  # TODO this looks and sounds very generic, be more specific, maybe it needs diffexp step

    def fill_form(self, run: Run) -> None:
        self.fields["database_names"].choices = fill_helper.to_choices(
            uniprot_databases()
        )
        self.fields["dataframe"].choices = fill_helper.get_choices(
            run, "differentially_expressed_proteins_df"
        )


class DatabaseIntegrationByUniprotForm(MethodForm):
    # Todo: uniprot
    # Todo: Add dynamic fill for database name and fields
    database_name = CustomChoiceField(
        choices=[],
        label="Uniprot databases (offline)",
    )
    fields = CustomMultipleChoiceField(choices=[], label="Fields")


class PlotGOEnrichmentBarPlotForm(MethodForm):
    # TODO: input:df fill dynamic with fill_forms
    input_df_step_instance = CustomChoiceField(
        choices=[], label="Choose dataframe to be plotted"
    )
    gene_sets = CustomMultipleChoiceField(choices=[], label="Sets to be plotted")
    value = CustomChoiceField(
        choices=GOEnrichmentBarPlotValue,
        label="Value (bars will be plotted as -log10(value)), fdr only for GO analysis with STRING, p_value is adjusted if available",
        initial=GOEnrichmentBarPlotValue.p_value,
    )
    top_terms = CustomNumberField(
        label="Number of top enriched terms per category",
        min_value=1,
        max_value=100,
        step_size=1,
        initial=10,
    )
    cutoff = CustomFloatField(
        label="Only terms with adjusted p-value (or FDR) < cutoff will be shown",
        min_value=0,
        max_value=1,
        step_size=0.01,
        initial=0.05,
    )
    title = CustomCharField(label="Title of the plot (optional)", required=False)

    colors = CustomMultipleChoiceField(
        choices=[], label="Colors for the plot (optional)"
    )  # TODO this should  not have to be set in fill_form

    def fill_form(self, run: Run) -> None:
        self.fields["colors"].choices = [
            (v, k) for k, v, in mcolors.CSS4_COLORS.items()
        ]

        self.fields["input_df_step_instance"].choices = fill_helper.get_choices(
            run, "enrichment_df"
        )
        if self.get_field("input_df_step_instance"):
            self.fields["gene_sets"].choices = fill_helper.to_choices(
                run.steps.get_step_output(
                    Step, "enrichment_df", self.get_field("input_df_step_instance")
                )["Gene_set"].unique()
            )

    @property
    def is_dynamic(self) -> bool:
        return True


class PlotGOEnrichmentDotPlotForm(MethodForm):
    # TODO: input_df fill dynamic with fill_forms
    input_df = CustomChoiceField(
        choices=[], label="Choose enrichment dataframe to be plotted"
    )
    x_axis_type = CustomChoiceField(
        choices=GOEnrichmentDotPlotXAxisType,
        label="Variable for x-axis: categorical scatter plot for one or multiple gene "
        "sets, or display combined score for one gene set",
        initial=GOEnrichmentDotPlotXAxisType.gene_sets,
    )
    gene_sets = CustomMultipleChoiceField(choices=[], label="Sets to be plotted")
    top_terms = CustomNumberField(
        label="Number of top enriched terms per category",
        min_value=1,
        max_value=100,
        initial=5,
    )
    cutoff = CustomNumberField(
        label="Only terms with adjusted p-value (or FDR) < cutoff will be shown",
        min_value=0,
        max_value=1,
        step_size=0.01,
        initial=0.05,
    )
    title = CustomCharField(label="Title of the plot (optional)")
    rotate_x_labels = CustomBooleanField(
        label="Rotate x-axis labels (if multiple categories are selected)", initial=True
    )
    show_ring = CustomBooleanField(label="Show ring around the dots", initial=False)
    dot_size = CustomNumberField(label="Scale the size of the dots", initial=5)

    def fill_form(self, run: Run) -> None:
        self.fields["gene_sets"].choices = [
            (el, el) for el in run.steps.protein_df["enrichment_categories"].unique()
        ]

    @property
    def is_dynamic(self) -> bool:
        return True


class PlotGSEADotPlotForm(MethodForm):
    # TODO: input_df fill dynamic with fill_forms
    input_df = CustomChoiceField(
        choices=[], label="Choose enrichment dataframe to be plotted"
    )
    gene_sets = CustomMultipleChoiceField(choices=[], label="Sets to be plotted")
    dot_color_value = CustomChoiceField(
        choices=GSEADotPlotDotColorValue,
        label="Color the dots by value",
        initial=GSEADotPlotDotColorValue.fdr_q_val,
    )
    x_axis_value = CustomChoiceField(
        choices=GSEADotPlotXAxisValue,
        label="Value to display on x axis",
        initial=GSEADotPlotXAxisValue.nes,
    )
    cutoff = CustomNumberField(
        label="Cutoff value for fdr q-value or nominal p-value",
        min_value=0,
        max_value=1,
        step_size=0.01,
        initial=0.05,
    )
    title = CustomCharField(label="Title of the plot (optional)")
    dot_size = CustomNumberField(label="Scale the size of the dots", initial=5)
    show_ring = CustomBooleanField(label="Show ring around the dots", initial=False)
    remove_library_names = CustomBooleanField(
        label="Remove library names from gene sets (e.g. 'KEGG_2013__')", initial=False
    )


class PlotGSEAEnrichmentPlotForm(MethodForm):
    term_dict = CustomChoiceField(
        choices=[], label="Enrichment details gene set to be plotted"
    )
    term_name = CustomChoiceField(
        choices=EmptyEnum, label="name of the term_dict for title", required=False
    )
    ranking = CustomChoiceField(choices=[], label="Ranking from GSEA")
    pos_pheno_label = CustomCharField(
        label="Label for positively correlated phenotype", initial=""
    )
    neg_pheno_label = CustomCharField(
        label="Label for positively correlated phenotype", initial=""
    )
