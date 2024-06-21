
# dev guide
This is a guide for developers starting to work on PROTzilla and will provide an overview of how to extend the application. For more detailed information, please refer to the wiki, especially the [Project structure in the Wiki](https://github.com/cschlaffner/PROTzilla2/wiki/The-architecture-of-PROTzilla)

### Project Structure
PROTzilla is structured as follows:
- [PROTzilla2/protzilla](../protzilla) package: contains all methods to perform calculations and generate plots. It can be used without the UI. You can find more information about each method in the corresponding docstring.
- [PROTzilla2/run.py](../protzilla/run.py): The Run class oversees run management, calculations, workflow configuration, and history tracking, including result accumulation upon calling next.
- [PROTzilla2/runner.py](../protzilla/runner.py): the runner is able to execute a given workflow without the the UI.
- [PROTzilla2/ui](../ui): contains the Django apps main and runs, therefore all code that has to do with the frontend. 
- [PROTzilla2/user_data](../user_data): contains all data produced by the user, including the user's workflows and the processed data and plots produced by a run. For each run a new folder is created


### Concept of methods, calculation methods, steps, and forms
Forms are the front-end part of calculations. The user sets the parameters, that should be used for the calculation, in the form, meaning that all the parameter fields are located in them. Dynamic updating also happens here.
Steps are a base-class in the code, describing a part of the calculation pipeline. One step is equivalent to one calculation, for example is MSdata importing a step, then metadata importing another, and log transformation another. 
Methods are different variants / ways of performing a step, like `DifferentialExpressionTTest`. Foe example,during the MSdata importing step, there is the MaxQuant variant, MSFragger variant and so on. Generally speaking, any given workflow only requires one method for each step, although there might be exceptions (like performing both a t-test as well as an anova analysis during the differential expression step.)
Calculation methods are the actual python functions that receive the parameters and input data and return the result of the calculation, for example the `t_test(...)`. 


### Calculation methods
The three folders below each represent a **section**. Each file in these folders represents a **step**. In a file there is a function for each method.

#### PROTzilla2/protzilla/importing
This folder contains the methods used for importing mass spectrometry data and metadata. Its methods always have the following signature: an input dataframe and any other method parameters. They return a protein intensities dataframe and a dict of other outputs.

#### PROTzilla2/protzilla/data_preprocessing
This folder contains the methods for filtering, imputation, normalisation, outlier detection and methods to create the corresponding plots. Its methods have the same signature as importing, receiving an input dataframe plus the method's parameters and returning a transformed dataframe together with a dict that contains other outputs specific to the method, such as dropouts, p-values or other values. The dataframe that is used as input is the output of the previous importing/data preprocessing step.

#### PROTzilla2/protzilla/data_analysis
This folder contains methods that are used to analyse the outputs of the data preprocessing section and previous data analysis steps. Always using the previous output dataframe as input gets replaced by naming the steps that should be used and choosing the right named step as input. On this section the calculation and the plots be can separated from each other. In the case of the calculation methods, they return a dictionary including dataframes and other outputs. On the other hand, plot methods return a list of figures.

