"""
Contains the abstract class for the steps of the pipeline.
Also contains the implementation of the steps, e.g. the parameters and such. 
"""
from pathlib import Path

import pandas as pd

from protzilla.importing import metadata_import, ms_data_import
from protzilla.parameters import (
    ContainerParameter,
    ParameterBoolean,
    ParameterCategorical,
    ParameterDataframe,
    ParameterFile,
)

TEMP_FOLDER = Path("./temp").resolve()


class STEP_TYPE:
    """
    Enum for the type of the step
    """

    IMPORTMAXQUANT = "ImportMaxQuant"
    IMPORTMSFRAGGER = "ImportMSFragger"
    IMPORTDIANN = "ImportDIANN"
    METADATAIMPORT = "MetadataImport"


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
        self.step_type = None
        self.output = None
        self.parameters = ContainerParameter()

    def calculate(self):
        """
        Calculates the step.
        """
        if self.parameters.empty:
            raise ValueError("No parameters were given")
        self.call_method()

    @property
    def output_path(self):
        if self.output is not None:
            return TEMP_FOLDER / (f"./{self.method}")
        return None

    @property
    def dataframe(self):
        if self.output is not None:
            return self.output.dataframe
        else:
            return None

    def call_method(self):
        """
        Calls the method of the step.
        """
        raise NotImplementedError

    def initialize(self):
        """
        Initializes the step.
        """
        raise NotImplementedError

    def dynamic_update(self, run):
        """
        Updates the parameters of the step based on the run object
        """
        raise NotImplementedError

    def plot(self):
        """
        Plots the output of the step
        """
        raise NotImplementedError

    def plot_method(self):
        """
        Calls the plot method of the step
        """
        raise NotImplementedError

    def finished(self):
        """
        Method that is called when the step is finished
        """
        raise NotImplementedError

    def to_dict(self):
        """
        Convert the step to a dictionary
        """
        if self.output_path is not None:
            self.output.write_to_path(self.output_path)
        return {
            "name": self.name,
            "method": self.method,
            "section": self.section,
            "step_type": self.step_type,
            "parameters": self.parameters.to_dict(),
            "output_path": self.output_path,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Factory: Create a step from a dictionary
        """
        name = data["name"]
        method = data["method"]
        section = data["section"]
        step_type = data["step_type"]
        parameters = ContainerParameter.from_dict(data["parameters"])
        output_path = None if data["output_path"] is None else Path(data["output_path"])
        if step_type == STEP_TYPE.IMPORTMAXQUANT:
            step = ImportMaxQuant()
        elif step_type == STEP_TYPE.IMPORTMSFRAGGER:
            step = ImportMSFragger()
        elif step_type == STEP_TYPE.IMPORTDIANN:
            step = ImportDIANN()
        elif step_type == STEP_TYPE.METADATAIMPORT:
            step = MetadataImport()
        else:
            raise ValueError(f"Unknown step type {step_type}")

        step.name = name
        step.method = method
        step.section = section
        step.step_type = step_type
        step.parameters = parameters
        # Further processing, like reading files etc.
        if output_path is not None:
            step.output = Output.from_path(output_path)
        return step


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
        self.dataframe = self.output[0]


class ImportMaxQuant(MSDataImport):
    def __init__(self):
        super().__init__()
        self.method = method = "MaxQuant"
        self.method_function = ms_data_import.max_quant_import
        self.step_type = STEP_TYPE.IMPORTMAXQUANT

    def call_method(self):
        calculation_result = self.method_function(
            _=None,
            file_path=self.parameters["file"].value,
            intensity_name=self.parameters["intensity_name"].value,
            map_to_uniprot=self.parameters["map_to_uniprot"].value,
        )
        output_dict = {
            "dataframe": calculation_result[0],
            "messages": calculation_result[1],
        }
        self.output = Output(output_dict)


class ImportMSFragger(MSDataImport):
    def __init__(self):
        super().__init__()
        self.method = method = "MS Fragger"
        self.method_function = ms_data_import.ms_fragger_import
        self.step_type = STEP_TYPE.IMPORTMSFRAGGER
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


class ImportDIANN(MSDataImport):
    def __init__(self):
        super().__init__()
        self.method = method = "DIA-NN"
        self.method_function = ms_data_import.diann_import
        self.step_type = STEP_TYPE.IMPORTDIANN

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
        self.method = "Normal"
        self.method_function = metadata_import.metadata_import_method
        self.step_type = STEP_TYPE.METADATAIMPORT
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

    def call_method(self):
        self.output = self.method_function(
            df=self.parameters.df.value,
            file_path=self.parameters.file.value,
            feature_orientation=self.parameters.feature_orientation.value,
        )


class Output:  # pylint: disable=too-few-public-methods
    """
    Represents a named output of a step.
    responsibilities:

    """

    def __init__(self, data=None):
        if isinstance(data, pd.DataFrame):
            self.data = {"dataframe": data}
        elif isinstance(data, dict):
            self.data = data
        elif isinstance(data, tuple):
            raise ValueError(
                "Tuple not supported as output of a step. Please convert it to a dictionary before passing it to the output class, or change the return type."
            )
        elif data is None:
            self.data = {}

    @classmethod
    def from_path(cls, path):
        output = cls()
        output.read_from_path(path)
        return output

    def write_to_path(self, path: Path):
        """
        Write the output to a file
        """
        Path(path).mkdir(exist_ok=True, parents=True)
        for key, value in self.data.items():
            if isinstance(value, pd.DataFrame):
                filename = f"{path}/{key}.csv"
                value.to_csv(filename, index=False)
        return path

    def read_from_path(self, path: Path):
        """
        Read the output from a file
        """
        self.data = {}
        for file in path.iterdir():
            if file.suffix == ".csv":
                self.data[file.stem] = pd.read_csv(file)

    def __getattr__(self, item):
        return self.data[item]

    def __getitem__(self, item):
        return self.data[item]


if __name__ == "__main__":
    # attempt to create a data import step
    # creation
    step = ImportMaxQuant()
    for parameter in step.parameters:
        print(parameter)

    # front-end value insertion
    print("Front end insertion... \n")
    step.parameters[
        "file"
    ] = "/home/henning/BP2023BR1/PROTzilla2/example/proteinGroups.txt"

    step.calculate()
    dic = step.to_dict()
    step2 = Step.from_dict(dic)
    step2.calculate()

    # General workflow
    """
    1. Initialize the step, this should happen when the workflow is created from a template and when the user adds a new step in the front-end
    2. When the step is reached, a "initialize" method is called, which fills necessary parameters (e.g. the intensity df)
        this could maybe be done by passing the run object into the step and letting it decide what is needs
    3. The information is inputted via the front-end
    4. the post-processing is done, again include a way to access the run object
    5. The step is calculated, which calls the method of the step
    6. the output is returned / the class calls some "finsihsed" method and manipulates the run object
    7. the next step is initialized and the process starts again
    """
