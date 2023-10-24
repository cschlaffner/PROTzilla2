## Build docs with Sphinx ##
- Docs are build with sphinx-autoapi
- after installing the packages in requirements.txt, all necessary dependencies for building the docs should be installed (sphinx==7.2.6, sphinx-autoapi==3.0.0, requests==2.31.0)
- to build the docs open the docs\ folder in a terminal and run "make html" to create the html documentation
    - in case error "Could not import extension sphinx.builders.linkcheck" occurs, try reinstalling python requests (pip install requests==2.31.0)
- To open the docs open the index.html in the docs\build\html folder 