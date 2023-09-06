# dev guide
This is a guide for Developers, starting to work on PROTzilla and will provide an overview on how to extend the application

### workflow structure
To analyse protein data in PROTzilla a user will go through **sections** "importing", "data_preprocessing", "data_analysis" and "data_integration". 
Each section is divided into **steps** that can be added to the workflow. A step uses a **method** to achieve what it's supposed to do.
Also methods can have **parameters**.
All implemented methods are listed in `protzilla/constants/workflow_meta.json` following the tree structure `section > step > method > parameter`.

### adding a new method
- add your method in `workflow_meta.json` within the corresponding step
- implement your method in `protzilla/<section>/<step>.py` corresponding to section and step you added the method in `workflow_meta.json`
- link the implementation to `workflow_meta.json` in the `method_map` data structure located in `protzilla/constants/location_mapping.py`
