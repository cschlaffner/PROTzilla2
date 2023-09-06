
# dev guide
This is a guide for developers starting to work on PROTzilla and will provide an overview of how to extend the application.

### project structure
[...]

### workflow structure
To analyze protein data in PROTzilla a user will go through **sections** "importing", "data_preprocessing", "data_analysis" and "data_integration". 
Each section is divided into **steps** that can be added to the workflow. A step uses a **method** to achieve what it's supposed to do.
Also, methods can have **parameters**.
All implemented methods are listed in `protzilla/constants/workflow_meta.json` following the tree structure `section > step > method > parameter`.

> [!NOTE]
> remember the hierarchy `section > step > method > parameter`

### adding a new method
- add your method in `workflow_meta.json` within the corresponding step and also specify parameters and their defaults.
- implement your method in `protzilla/<section>/<step>.py` corresponding to the section and step you added in `workflow_meta.json` with the parameters specified there
  - e.g. look at `protzilla/data_preprocessing/imputation.py`
- preprocessing methods also need a plot generation implementation.
- link the implementation to `workflow_meta.json` in the `method_map` and `plot_map` data structures located in `protzilla/constants/location_mapping.py`
- TODO: ist das alles?

### what is the difference between run, workflow and history?
The directory `user_data/workflows` contains workflow templates. 
They store the configuration of an analysis, which contains the order of steps and also their corresponding selected methods and parameters.
A workflow can be shared among users for reproducible results. 

When a user starts PROTzilla, they are asked to create a new run and select a workflow template.
A Run object from `protzilla/run.py` will be created, and a new folder with the name of the run will be generated in `user_data/runs`.
The selected workflow will be copied into the run directory and will be the `workflow_config` of this run.

The run will follow the steps listed in the `workflow_config` and selected methods and parameter values as default. 
If no default methods or parameters are selected within `workflow_config`, default values from `workflow_meta.json` will be used.

The history contains the outputs of steps that have already been executed and is necessary for the back button.

> [!WARNING]
> never delete the `hello123` run as for some reason the tests on github will fail then. We tried to identify the problem but our best solution was to just leave `hello123` where it was.

### why are there #TODOs with a number in the code?
To-dos are small issues or suggestions listed in [the issues list with label "todo"](https://github.com/cschlaffner/PROTzilla2/issues?q=is%3Aissue+is%3Aopen+label%3Atodo).
The number corresponds to the issue ID. 
