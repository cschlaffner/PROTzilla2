# PROTzilla2



## Setup

### Environment

PROTzilla2 uses Python 3.11 and conda to manage the environment and pip for installing packages.

Use `conda create -n <environment Name> python=3.11` to create the environment, activate it with `conda activate <environment Name>` (you might need to reopen your shell for this to work) and use `pip install -r requirements.txt` to install the relevant requirements.

We use pre-commit hooks to lint and format the python code. For this to work, please run `pre-commit install` after installing the requirement.
