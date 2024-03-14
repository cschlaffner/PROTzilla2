"""
Contains the abstract class for the steps of the pipeline.
Also contains the implementation of the steps, e.g. the parameters and such. 
"""
from importing import ms_data_import


class Parameter:  # pylint: disable=too-few-public-methods
    """
    Represents the parameters of a step.
    """

    def __init__(self, name: str, text: str = None, default=None):
        self.name = name
        self.text = text
        self.value = default

    def set_value(self, value):
        self.value = value

    def __str__(self):
        return f'Parameter: {self.name}: "{self.text}" - {self.value}'


class ParameterList:
    """
    Wrapper class for a list of parameters. This contains the parameters of a step.
    """

    def __init__(self):
        self.parameters = {}

    def __getitem__(self, item):
        return self.parameters[item]

    def add(self, parameter: Parameter):
        # if already a parameter with that exact name throw error
        if parameter.name in self.parameters:
            raise ValueError(f"Parameter with name {parameter.name} already exists")

        self.parameters[parameter.name] = parameter

    def __setitem__(self, parameter_name, value):
        if parameter_name in self.parameters:
            self.parameters[parameter_name].set_value(value)
        else:
            raise ValueError(f"No parameter with name {parameter_name} exists")

    def __iter__(self):
        return iter(self.parameters.values())


class Step:
    """
    Abstract class for the steps of the pipeline.
    """

    def __init__(self, section: str, name: str, method: str):
        """
        :param name: The name of the step
        :param method: The method of the step
        """
        self.section = section
        self.name = name
        self.method = method
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


class MaxQuantImport(Step):
    """
    Represents the importing step.
    """

    def __init__(self, section: str, name: str, method: str):
        super().__init__(section, name, method)
        self.method_function = ms_data_import.max_quant_import
        self.parameters.add(ParameterFile("file", "Please enter a file"))
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
        """
        Calls the method of the step.
        """
        # TODO convert to new output datatype
        self.output = self.method_function(
            _=None,
            file_path=self.parameters["file"].value,
            intensity_name=self.parameters["intensity_name"].value,
            map_to_uniprot=self.parameters["map_to_uniprot"].value,
        )


class Output:  # pylint: disable=too-few-public-methods
    """
    Represents a named output of a step.
    """

    def __init__(self):
        pass


class ParameterFile(Parameter):
    """
    Represents a file parameter of a step.
    """

    def __init__(self, name: str, text: str, default=None):
        super().__init__(name, text, default if default is not None else "")


class ParameterCategorical(Parameter):
    """
    Represents a categorical parameter of a step.
    """

    def __init__(self, name: str, text: str, options: list, default=None):
        super().__init__(name, text, default if default is not None else options[0])
        self.options = options


class ParameterBoolean(Parameter):
    """
    Represents a boolean parameter of a step.
    """

    def __init__(self, name: str, text: str, default: bool = False):
        super().__init__(name, text, default)


if __name__ == "__main__":
    # attempt to create a data import step
    # creation
    step = MaxQuantImport("Importing", "MS Data Import", "MaxQuant")
    for parameter in step.parameters:
        print(parameter)

    # front-end value insertion
    print("Front end insertion... \n")
    step.parameters[
        "file"
    ] = "/home/henning/BP2023BR1/PROTzilla2/example/proteinGroups.txt"
    step.parameters["intensity_name"] = "LFQ intensity"

    for parameter in step.parameters:
        print(parameter)

    # back-end value insertion
    # e.g. find a file
    # calculation
    step.calculate()

    # output
    print(step.output)
