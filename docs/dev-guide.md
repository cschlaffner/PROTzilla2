
# dev guide
This is a guide for developers starting to work on PROTzilla and will provide an overview of how to extend the application.

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


### Why are there #TODOs with a number in the code?
To-dos are small issues or suggestions listed in [the issues list with label "todo"](https://github.com/cschlaffner/PROTzilla2/issues?q=is%3Aissue+is%3Aopen+label%3Atodo).
The number corresponds to the issue ID. 

### The runner
PROTzilla can be used not only in the browser but also from the **command line** without a graphical user interface. The runner is a practical tool for this. 
It can execute an entire workflow without further user input. In the future, the runner should also be executable from the browser. 
This way, as soon as researchers created a workflow with the analysis they want to perform, they can get their results for multiple datasets with less effort.
PROTzilla is thus intended to be an **independent python package** that also works independently of UI and Django. 
> [!NOTE]
> think about whether new features should be implemented in the `protzilla` or `ui` folder.

### UI

#### Structure of Django project. 
The UI is built with the web framework Django. The folder /ui encapsulates all the frontend related code. 

A Django project is structured in such way that the root folder (in this case /ui) contains application folders. In PROTzilla there are two applications main and runs. The primary functionality of PROTzilla is in the runs application.

In Django, web pages and other content are delivered by views. Each view is represented by a Python function, which is usually found in the views.py file. A view function takes a HTTP request and returns a HTTP response, for example this can be a HTML page or a HTTP error. Also, Django allows to create HTML pages dynamically with templates. A template contains the static parts of the desired HTML output as well as some special syntax describing how dynamic content will be inserted. Templates are usually located at the templates folder inside the app folder. For further information on Django see their [documentation](https://docs.djangoproject.com/).

PROTzilla's frontend has two main pages: the home page, where runs can be created and continued and the run page, where the user can upload, process, analyse and plot proteomics data according to the selected workflow or add and delete any steps in the current workflow.

#### The "run" page
The "run" page is generated by the Django view function called `detail`, which uses the Django template `details.html`. This view, along with the template, serves as the foundation for the PROTzillas frontend and therefore a good starting point to understand how the frontend is structured. 

##### Layout
The layout of the "run" page consists of the History displayed at the top, the current step at the bottom, and a sidebar. Regardless of the current step, the HTML page's structure remains the same. Whenever an action, such as adding a step or pressing the next/back button, occurs, it triggers the detail view to be called again by the corresponding add, next, or back view, and subsequently renders the page with the updated state obtained from the Run and History classes.

##### Input fields 
The `fields.py` file contains methods for creating various input fields required for the method parameters. The field type and default information is specified in the workflow meta file. The `make_parameter_input` function selects the appropriate template based on the field type. But before creating the fields, the method `insert_special_params` in `run_helper` manages the display and retrieval of runtime-specific information, like outputs from previous steps, the groups present in the metadata uploaded by the user or protein database information. To see a more detailed example on how each special parameter works see  [`insert_special_params`](protzilla/run_helper.py)

Certain fields need to be loaded without the web page being reloaded. This includes: selecting the method for the current step, populating dropdown categories based on a previous selection, and loading dynamically additional fields based on specific choices. To achieve this, AJAX asyncronous server requests are employed. HTML elements with special functionalities in the dropdowns are identified by class IDs that initiate this behavior. The JavaScript code responsible for handling these AJAX requests can be found in `run/templates/runs/dynamic_methods.html`. 




# tutorial

### adding a new method/step
To provide an example, I will display the `knn` method within the step `imputation`. Feel free to have a look at the code by yourself.
0. Think about what method you want to implement, what parameters should be selectable by the user and to what step does the method belong.

1. Add your method in `protzilla/constants/workflow_meta.json` within the corresponding step and also specify parameters and their defaults.
 <p align="center"><img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/50cbd068-bdeb-4073-ae18-7edaf77df96b" width="400"></p>
 
2. Implement your method in `protzilla/<section>/<step>.py` corresponding to the section and step you added in `workflow_meta.json` with the parameters specified there.<br>
   Importing and preprocessing steps should return the **dataframe**, that gets handed to the next step and a **dict** with further results. Data analysis and integration steps just return a dict.<br>
   **Do not forget to explain your method with python docstrings!**
   
   in `protzilla/data_preprocessing/imputation.py`:
 <p align="center"><img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/7a57a27a-4ac6-4629-981e-e196ab3e6e32" width="400"></p>

3. Preprocessing methods also need a plot generation implementation which returns a list of `plotly.graph_objects.Figure`:
    <p align="center"><img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/5b8927d4-97e7-4b0b-b679-a2ee05c577f4" width="400"></p>
4. Link the implementation to the entry in `workflow_meta.json` in the `method_map` and `plot_map` data structures located in `protzilla/constants/location_mapping.py`
      <p align="center"><img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/1b4f7349-27a1-4c1c-946d-f9f21b778665" height="100">
      <img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/ec623847-82f6-49d2-b17f-e44e73b46224" height="100"></p>
5. Write **tests** for your new method (experiment with TDD and write tests before implementing the method, it can save you some time:) )

