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

    def __getattr__(self, item):
        if item in self.parameters:
            return self.parameters[item]
        raise AttributeError(f"No parameter with name {item} exists")

    def __iter__(self):
        return iter(self.parameters.values())


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

    def set_options(self, options):
        self.options = options
        self.value = self.value if self.value in options else options[0]

    def __str__(self):
        return f'Parameter: {self.name}: "{self.text}" - {self.options} - {self.value}'


class ParameterBoolean(Parameter):
    """
    Represents a boolean parameter of a step.
    """

    def __init__(self, name: str, text: str, default: bool = False):
        super().__init__(name, text, default)


class ParameterDataframe(Parameter):
    """
    Represents a dataframe parameter of a step.
    """

    def __init__(self, name: str = None, text: str = None, default=None):
        super().__init__(name, text, default)

    def set_value(self, value):
        self.value = value

    def __str__(self):
        return f'Parameter: {self.name}: "{self.text}" - {self.value}'
