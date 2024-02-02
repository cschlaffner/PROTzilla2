# PROTzilla2
[![Coverage badge](https://github.com/antonneubauer/PROTzilla2/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/antonneubauer/PROTzilla2/tree/python-coverage-comment-action-data)  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


PROTzilla aims to be a one-stop-shop for proteomics-researchers (with or without a background in programming) providing a platform that allows a user to go from raw data to paper-ready graphics in a user-friendly web-based interface. While doing so we focus on scaleable data-analysis as well as shareable and reproducible results and methods. 


## Quick(-and-easy)-Start-Guide
> [!NOTE]
> For Documentation on how to use PROTzilla, look [here](./docs/user-guide.md).

To make it easy getting started we have written `run_protzilla.sh` for the macOS and Linux users and `run_protzilla.bat` for windows-users. The script takes care of installing miniconda, creating the environment, installing the requirements and starting the Server at  `http://127.0.0.1:8000`. Everytime you want to run PROTzilla, **just execute the script**. If you don't have some version of conda installed, the script will install miniconda. PROTzilla (and the script) will only work as we planned with it installed. Therefore, when installing conda you have to accept their terms and conditions and should accept the suggested folders and commands to be run (tldr: `Enter` and `yes` are your friends ;) )

The first time starting PROTzilla might take up to 15 minutes.

If you are on **macOS**: You can either do that via opening `run_protzilla.sh` with the terminal (right-click on the file -> "open with" -> "terminal").

If you are on **linux or macOS**: Run the script from the command-line from within Project-Folder (`PROTzilla2`) by running `./run_protzilla.sh`.

If you are on **Windows**: just double-click `run_protzilla.bat`. If you start PROTzilla for the first time you might need to restart the script after miniconda installation.

In any case: the window that opens when you run the script (the terminal-window you ran the the script from) will also display error-messages and information about the communication between the web-frontent and the backend as well as error-messages from the protzilla-backend performing all the calculations, creating plots and so on.

Once the script has done most of its work, something along the lines of `Starting development server at http://127.0.0.1:8000/` should appear. This just means that you can now open your browser, type `http://127.0.0.1:8000/` and you should be good to go! The PROTzilla starting-page should show up and you should have the choice to either create a run or continue an existing one.


## Start-Guide - a little more technical
> [!NOTE]
> For further information on how to contribute on PROTzilla read our [dev-guide](./docs/dev-guide.md).

PROTzilla2 uses Python 3.11 and conda to manage the environment and pip for installing packages.

Use `conda create -n <environment Name> python=3.11` to create the environment, activate it with `conda activate <environment Name>` (you might need to reopen your shell for this to work) and use `pip install -r requirements.txt` to install the relevant requirements in your environment.

We use pre-commit hooks to lint and format the python code. For this to work, please run `pre-commit install` after installing the requirements (this has caused some problems when developing, especially for windows-users so temporarily deactivating this might be a good idea if you get persistent errors when trying to commit)


### UI
After you went through the setup, open a shell and move into the projectfolder. Once there, make sure the correct python/conda environment is activated and execute `python ui/manage.py runserver` to start the server locally. You can access it via your Browsers of choice at  http://127.0.0.1:8000/runs. Since this is a normal Django Development-Server, you can use the usual flags and features that come with that like making it accessible to all users on the network that can see your machine by running `python ui/manage.py runserver 0.0.0.0:8000` instead (you might need to add `"*"` to `allowed_hosts` in `ui/main/settings.py` to whitelist all external hosts).


## Using PROTzilla
### Scripting
We separated the UI and the calculations-part of PROTzilla making it possible to use PROTzilla just as an import in your own scripts or notebooks. A good starting-point is the `run` and `runner`-classes as well as looking at the tests (`PROTzilla2/tests/protzilla/test_run.py`, `PROTzilla2/tests/protzilla/test_runner.py`, `PROTzilla2/tests/protzilla/test_runner_cli.py`).

### Runner
The runner exists to make it easy to compute a given dataset using a given workflow (and getting all the interesting plots to look at). It can be used from the command-line by running (with your PROTzilla-environment active, of course) `python runner_cli.py`. This will display a very rudimentary list of options and help. Running `python runner_cli.py -h` will provide a much more detailed overview over the options. 

For examples on how to use it, it might be easiest to look at the existing tests concering the runner, located at `PROTzilla2/tests/protzilla/test_runner_cli.py` and `PROTzilla2/tests/protzilla/test_runner.py` respectively.

We are thinking about making the runner usable from the web-interface, though currently this does not have a timeline.

### Storage
User-Data, that is workflows and runs, are saved at `PROTzilla2/user_data/workflows` and `PROTzilla2/user_data/runs` respectively. The Workflows saved here are the ones you are able to select when creating a run. We provide a "standard"-Workflow that covers all-out data-preprocessing and basic data-analysis. When you export a workflow (you will find the button in the sidebar when working on a run), it will be saved here as well.
When creating a run, all the associated data, settings and a copy of the used workflow (with parameters set that were actually used when a calculation was performed) are saved in `runs/<run_name>`.

In the future, we will likely work on making it possible for users to define the location where `user_data` is saved at. For now, this is, unfortunately, not possible.
