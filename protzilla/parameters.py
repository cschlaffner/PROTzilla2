"""
Contains the parameters of the steps of the pipeline.
"""
from enum import Enum
from typing import List


class PARAMETER_TYPE(Enum):
    """Enum of all possible types of parameters."""

    FILE = "file"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATAFRAME = "dataframe"
    METADATAFRAME = "metadataframe"
    STEP_OUTPUT = "step_output"
    TEXT = "text"


class Parameter:  # pylint: disable=too-few-public-methods
    """
    Represents the parameters of a step.
    """

    def __init__(
        self, name: str, parameter_type: PARAMETER_TYPE, text: str = None, default=None
    ):
        self.name = name
        self.text = text
        self.value = default
        self.type = parameter_type

    def set_value(self, value):
        self.value = value

    def __str__(self):
        return f'Parameter: {self.name}: "{self.text}" - {self.value}'

    def to_dict(self):
        """Convert the parameter to a dictionary"""
        if [param is None for param in [self.name, self.text, self.type]].any():
            raise ValueError(
                "Parameter is missing required fields, cannot convert to dict"
            )
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data):
        """Create a parameter from a dictionary"""
        raise NotImplementedError


class ContainerParameter:
    """
    Wrapper class for a list of parameters. This contains the parameters of a step.
    """

    def __init__(self):
        self.parameters = {}

    def add(self, parameter: Parameter):
        # if already a parameter with that exact name throw error
        if parameter.name in self.parameters:
            raise ValueError(f"Parameter with name {parameter.name} already exists")

        self.parameters[parameter.name] = parameter

    def add_from_dict(self, data):
        if data["type"] == PARAMETER_TYPE.FILE:
            self.add(ParameterFile.from_dict(data))
        elif data["type"] == PARAMETER_TYPE.CATEGORICAL:
            self.add(ParameterCategorical.from_dict(data))
        elif data["type"] == PARAMETER_TYPE.BOOLEAN:
            self.add(ParameterBoolean.from_dict(data))
        elif data["type"] == PARAMETER_TYPE.DATAFRAME:
            self.add(ParameterDataframe.from_dict(data))
        elif data["type"] == PARAMETER_TYPE.METADATAFRAME:
            self.add(ParameterMetaDataframe.from_dict(data))
        elif data["type"] == PARAMETER_TYPE.STEP_OUTPUT:
            self.add(ParameterStepOutput.from_dict(data))
        elif data["type"] == PARAMETER_TYPE.TEXT:
            self.add(ParameterText.from_dict(data))
        else:
            raise ValueError(f"Parameter type {data['type']} not recognized")

    def to_dict(self):
        return {param.name: param.to_dict() for param in self.parameters.values()}

    @classmethod
    def from_dict(cls, data):
        container = cls()
        for param in data.values():
            container.add_from_dict(param)
        return container

    def __getitem__(self, item):
        return self.parameters[item]

    def __setitem__(self, parameter_name, value):
        if parameter_name in self.parameters:
            self.parameters[parameter_name].set_value(value)
        else:
            raise ValueError(f"No parameter with name {parameter_name} exists")

    def __getattr__(self, item):
        if item in self.parameters:
            return self.parameters[item]
        raise AttributeError(f"No parameter with name {item} exists")

    def __iter__(self):
        return iter(self.parameters.values())

    @property
    def empty(self):
        return len(self.parameters) == 0


class ParameterFile(Parameter):
    """
    Represents a file parameter of a step.
    """

    def __init__(self, name: str, text: str, default=None):
        super().__init__(
            name, PARAMETER_TYPE.FILE, text, default if default is not None else ""
        )
        self

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "text": self.text,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["text"], data["value"])


class ParameterCategorical(Parameter):
    """
    Represents a categorical parameter of a step.
    """

    def __init__(
        self, name: str, text: str, options: list, default=None, parameter_type=None
    ):
        super().__init__(
            name,
            PARAMETER_TYPE.CATEGORICAL if parameter_type is None else parameter_type,
            text,
            default if default is not None else options[0],
        )
        self.options = options

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "text": self.text,
            "value": self.value,
            "options": self.options,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["text"], data["options"], data["value"])

    def set_options(self, options):
        self.options = options
        self.value = self.value if self.value in options else options[0]


class ParameterBoolean(Parameter):
    """
    Represents a boolean parameter of a step.
    """

    def __init__(self, name: str, text: str, default: bool = False):
        super().__init__(name, PARAMETER_TYPE.BOOLEAN, text, default)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "text": self.text,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["text"], data["value"])


class ParameterDataframe(ParameterCategorical):
    # TODO add logic to determine the correct options
    """
    Represents a dataframe parameter of a step.
    """

    def __init__(
        self,
        name: str = None,
        text: str = None,
        options: List[str] = None,
        default=None,
    ):
        # TODO determine options?
        options = [] if options is None else options

        super().__init__(
            name=name,
            parameter_type=PARAMETER_TYPE.DATAFRAME,
            text=text,
            options=options,
            default=default,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "text": self.text,
            "value": self.value,
            "options": self.options,
        }

    def from_dict(cls, data):
        return cls(data["name"], data["text"], data["options"], data["value"])

    def set_value(self, value):
        self.value = value


class ParameterMetaDataframe(ParameterCategorical):
    # TODO add logic to determine the correct options
    """
    Represents a dataframe parameter of a step.
    """

    def __init__(self, name: str = None, text: str = None, default=None):
        options = []
        super().__init__(
            name=name,
            text=text,
            parameter_type=PARAMETER_TYPE.DATAFRAME,
            options=options,
            default=default,
        )


class ParameterStepOutput(ParameterCategorical):
    """
    Parameter to choose the output of a previous step.
    """

    def __init__(self, name: str, text: str, options: List[str], default=None):
        # TODO get options from run object?
        options = [] if options is None else options
        super().__init__(
            name=name,
            text=text,
            options=options,
            default=default if default is not None else options[0],
            parameter_type=PARAMETER_TYPE.STEP_OUTPUT,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "text": self.text,
            "value": self.value,
            "options": self.options,
        }

    def from_dict(cls, data):
        return cls(data["name"], data["text"], data["options"], data["value"])


class ParameterText(Parameter):
    """
    Represents a text parameter of a step.
    """

    def __init__(self, name: str, text: str, default=None):
        super().__init__(name, PARAMETER_TYPE.TEXT, text, default)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "text": self.text,
            "value": self.value,
        }

    def from_dict(cls, data):
        return cls(data["name"], data["text"], data["value"])
