This documentation is meant to give new users an overview of the structure of PROTzilla and where data sets and calculation results are saved.

## Concepts
There are a few key concepts that one needs to understand to effectively use and communicate about PROTzilla. They are explained in the following paragraph.

- **Workflow**: A workflow is a construct specifies how data is being handled, what calculations are performed in what order and what graphics are created.  When providing the same data, a workflow will always result in the same results. All workflows are saved in their own `.json` files, located at `user_data/workflows/...`.

- **Run**: A run is the application of a workflow, the workflow on a given data set. In a run the workflow can be modified. It is for example possible to add additional preprocessing steps, remove other ones or apply different analysis methods. When all steps in a run are completed that a user wants to perform, this potentially modified workflow can be exported under a new name for later use.


## Structure
PROTzilla is split into four sections, **Importing**, **Data Preprocessing**, **Data Analysis** and **Data Integration**. Within each section, there are many available steps. A step groups related methods. A step in the Data Preprocessing section, for example, is Imputation and available methods in this step are, among others, by k-nearest neighbor or by minimum value per sample. A workflow starts with the importing section, continues with data preprocessing and finishes with data analysis integration. These last two steps can be intertwined.


## Start Page
t



