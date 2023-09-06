
# dev guide
This is a guide for Developers, starting to work on PROTzilla and will provide an overview on how to extend the application

### TODO project structure
[...]


### workflow structure
To analyse protein data in PROTzilla a user will go through **sections** "importing", "data_preprocessing", "data_analysis" and "data_integration". 
Each section is divided into **steps** that can be added to the workflow. A step uses a **method** to achieve what it's supposed to do.
Also methods can have **parameters**.
All implemented methods are listed in `protzilla/constants/workflow_meta.json` following the tree structure `section > step > method > parameter`.

### adding a new method
- add your method in `workflow_meta.json` within the corresponding step
- implement your method in `protzilla/<section>/<step>.py` corresponding to section and step you added the method in `workflow_meta.json`
  - e.g. look at `protzilla/data_preprocessing/imputation.py`
- preprocessing methods also need a plot generation implementation.
- link the implementation to `workflow_meta.json` in the `method_map` and `plot_map` data structures located in `protzilla/constants/location_mapping.py`
- TODO: ist das alles?

### what is the user_data directory?
The directory `user_data/workflows` contains workflow templates, that can be shared among users for reproducibility. 
This workflows store the order of steps also their corresponding selected methods and parameters.
If no default methods or parameters are selected, default values from `workflow_meta.json` will be used.

When a user creates a new run in PROTzilla a new folder in `user_data/runs` will be generated. 
The user is asked to select a workflow template.
A copy of that workflow is copied into the run folder with the name `workflow.json`. 
It shaddows the state of `run.workflow_config` in `protzilla/run.py`.


> [!WARNING]
> ⚠️ never delete the `hello123` run as for some reason the tests on github will fail then. We tried to identify the problem but our best solution was to just leave the run

### why are there #TODOs with a number in the code?
Todos are small issues or suggestions listed in [the issues list with label "todo"](https://github.com/cschlaffner/PROTzilla2/issues?q=is%3Aissue+is%3Aopen+label%3Atodo).
The number corresponds to the issue id. 
