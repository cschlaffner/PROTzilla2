# PROTzilla2
[![Coverage badge](https://github.com/antonneubauer/PROTzilla2/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/antonneubauer/PROTzilla2/tree/python-coverage-comment-action-data)  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



## Setup

### Script:

To make it easy to get started (on MacOS, Linux (only tested on Ubuntu)) we have written `run_protzilla.sh`. The script takes care of installing miniconda, creating the environment and starting the Server at  `http://127.0.0.1:8000`. Everytime you want to run PROTzilla, just execute the script. You can either do that via the command-line from within Project-Folder (`PROTzilla2') by running `./run_protzilla.sh` or opening the


### Environment

PROTzilla2 uses Python 3.11 and conda to manage the environment and pip for installing packages.

Use `conda create -n <environment Name> python=3.11` to create the environment, activate it with `conda activate <environment Name>` (you might need to reopen your shell for this to work) and use `pip install -r requirements.txt` to install the relevant requirements.

We use pre-commit hooks to lint and format the python code. For this to work, please run `pre-commit install` after installing the requirement.


## Execution

### UI

After you went through the setup, open a shell and move into the projectfolder. Once there, execute `python ui/manage.py runserver` to start the server locally. You can access it via your Browers of choice at  http://127.0.0.1:8000/runs.
