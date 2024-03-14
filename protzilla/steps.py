"""
Contains the abstract class for the steps of the pipeline.
Also contains the implementation of the steps, e.g. the parameters and such. 
"""
from importing import metadata_import, ms_data_import

from protzilla.parameters import (
    ParameterBoolean,
    ParameterCategorical,
    ParameterDataframe,
    ParameterFile,
    ParameterList,
)


class Step:
    """
    Abstract class for the steps of the pipeline.
    """

    def __init__(self):
        """
        :param name: The name of the step
        :param method: The method of the step
        """
        self.section = None
        self.name = None
        self.method = None
        self.method_function = None
        self.output = None
        self.parameters = ParameterList()

    def __str__(self):
        return f"{self.name} - {self.method}"

    def __eq__(self, other):
        return self.name == other.name and self.method == other.method

    def __hash__(self):
        return hash((self.name, self.method))

    def calculate(self):
        """
        Calculates the step.
        """
        if self.parameters is None:
            raise ValueError("No parameters were given")
        self.call_method()

    def call_method(self):
        """
        Calls the method of the step.
        """
        raise NotImplementedError


class Importing(Step):
    """
    Represents the importing section.
    """

    def __init__(self):
        super().__init__()
        self.section = "Importing"
        self.parameters.add(ParameterFile("file", "Please enter a file"))


class MSDataImport(Importing):
    def __init__(self):
        super().__init__()
        self.step = "MS Data Import"
        self.parameters.add(
            ParameterCategorical(
                "intensity_name",
                "Please select an intensity",
                ["LFQ intensity", "iBAQ", "Intensity"],
            ),
        )
        self.parameters.add(
            ParameterBoolean(
                "map_to_uniprot", "Map to Uniprot IDs using Biomart (online)", False
            )
        )

    def call_method(self):
        self.output = self.method_function(
            _=None,
            file_path=self.parameters["file"].value,
            intensity_name=self.parameters["intensity_name"].value,
            map_to_uniprot=self.parameters["map_to_uniprot"].value,
        )


class ImportMaxQuant(MSDataImport):
    def __init__(self):
        super().__init__()
        self.method = method = "MaxQuant"
        self.method_function = ms_data_import.max_quant_import


class ImportMSFragger(MSDataImport):
    def __init__(self):
        super().__init__()
        self.method = method = "MS Fragger"
        self.method_function = ms_data_import.ms_fragger_import
        self.parameters.intensity_name.set_options(
            [
                "Intensity",
                "MaxLFQ Total Intensity",
                "MaxLFQ Intensity",
                "Total Intensity",
                "MaxLFQ Unique Intensity",
                "Unique Spectral Count",
                "Unique Intensity",
                "Spectral Count",
                "Total Spectral Count",
            ]
        )
        self.parameters["intensity_name"].set_options(
            [
                "Intensity",
                "MaxLFQ Total Intensity",
                "MaxLFQ Intensity",
                "Total Intensity",
                "MaxLFQ Unique Intensity",
                "Unique Spectral Count",
                "Unique Intensity",
                "Spectral Count",
                "Total Spectral Count",
            ]
        )


class ImportDIANN(MSDataImport):
    def __init__(self):
        super().__init__()
        self.method = method = "DIA-NN"
        self.method_function = ms_data_import.diann_import

    def call_method(self):
        # TODO convert to new output datatype
        self.output = self.method_function(
            _=None,
            file_path=self.parameters["file"].value,
            map_to_uniprot=self.parameters["map_to_uniprot"].value,
        )


class MetadataImport(Importing):
    def __init__(self):
        super().__init__()
        self.step = "Metadata Import"
        self.parameters.add(
            ParameterCategorical(
                "feature_orientation",
                "Please select columns",
                [
                    "Columns (samples in rows, features in columns)",
                    "Rows (features in rows, samples in columns)",
                ],
            )
        )
        self.parameters.add(ParameterDataframe("df"))
        self.method_function = metadata_import.metadata_import_method

    def call_method(self):
        self.output = self.method_function(
            df=self.parameters.df.value,
            file_path=self.parameters.file.value,
            feature_orientation=self.parameters.feature_orientation.value,
        )


class Output:  # pylint: disable=too-few-public-methods
    """
    Represents a named output of a step.
    """

    def __init__(self):
        pass


if __name__ == "__main__":
    # attempt to create a data import step
    # creation
    step = ImportMSFragger()
    for parameter in step.parameters:
        print(parameter)

    # front-end value insertion
    print("Front end insertion... \n")
    step.parameters[
        "file"
    ] = "/home/henning/BP2023BR1/PROTzilla2/example/proteinGroups.txt"

    for parameter in step.parameters:
        print(parameter)

    step.calculate()

    df = step.output
    step = MetadataImport()
    for parameter in step.parameters:
        print(parameter)

    step.parameters["file"] = "/home/henning/BP2023BR1/PROTzilla2/example/meta.csv"
    step.parameters["df"] = df
    step.calculate()
    print(step.output)
