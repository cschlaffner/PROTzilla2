# tutorial

### adding a new method/step
To provide an example, I will display the `knn` method within the step `imputation`. Feel free to have a look at the code by yourself.
1. Add your method in `protzilla/constants/workflow_meta.json` within the corresponding step and also specify parameters and their defaults.
 <p align="center"><img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/50cbd068-bdeb-4073-ae18-7edaf77df96b" width="400"></p>
 
2. Implement your method in `protzilla/<section>/<step>.py` corresponding to the section and step you added in `workflow_meta.json` with the parameters specified there.<br>
   Importing and preprocessing steps should return the dataframe, that gets handed to the next step and a dict with further results. Data analysis and integration steps just return a dict.<br>
   > [!NOTE]
   >    Do not forget to explain your method with python docstrings!
   
   in `protzilla/data_preprocessing/imputation.py`:
 <p align="center"><img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/7a57a27a-4ac6-4629-981e-e196ab3e6e32" width="400"></p>

3. Preprocessing methods also need a plot generation implementation which returns a list of `plotly.graph_objects.Figure`:
    <p align="center"><img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/5b8927d4-97e7-4b0b-b679-a2ee05c577f4" width="400"></p>
4. Link the implementation to the entry in `workflow_meta.json` in the `method_map` and `plot_map` data structures located in `protzilla/constants/location_mapping.py`
      <p align="center"><img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/1b4f7349-27a1-4c1c-946d-f9f21b778665" height="100">
      <img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/ec623847-82f6-49d2-b17f-e44e73b46224" height="100"></p>
5. Write tests for your new method (experiment with TDD and write tests before implementing the method, it can save you some time:) )


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

# tutorial

### adding a new method/step
1. add your method in `workflow_meta.json` within the corresponding step and also specify parameters and their defaults.
2. <img src="https://github.com/cschlaffner/PROTzilla2/assets/44113112/0aa5e7be-e72e-4f52-9c60-0ee86743348e" width="48">
- ![image]( | width=100)

- implement your method in `protzilla/<section>/<step>.py` corresponding to the section and step you added in `workflow_meta.json` with the parameters specified there
  - e.g. look at `protzilla/data_preprocessing/imputation.py`
- preprocessing methods also need a plot generation implementation.
- link the implementation to `workflow_meta.json` in the `method_map` and `plot_map` data structures located in `protzilla/constants/location_mapping.py`
- TODO: ist das alles?
