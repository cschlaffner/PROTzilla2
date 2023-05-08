#!/bin/bash

ENV_NAME="protzilla"
CONDA_URL="https://repo.anaconda.com/miniconda/"
MACOS_MINICONDA="Miniconda3-latest-MacOSX-x86_64.sh"
LINUX_MINICONDA="Miniconda3-latest-Linux-x86_64.sh"
URL_TO_USE=""
VERSION_TO_USE=""

# check if the script is running on macos or linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    URL_TO_USE=$CONDA_URL+$LINUX_MINICONDA
    VERSION_TO_USE=$LINUX_MINICONDA
elif [[ "$OSTYPE" == "darwin"* ]]; then
    URL_TO_USE=$CONDA_URL+$MACOS_MINICONDA
    VERSION_TO_USE=$MACOS_MINICONDA
else
    echo "OS not supported, use the install_windows.sh script (to be written)."
    exit 1
fi

# Check if Miniconda is already installed
if [ -d "$HOME/miniconda3" ] || [ -d "$HOME/anaconda3" ]; then
    echo "Miniconda or Anaconda are already installed."
    conda init bash
else
    echo "Installing Miniconda..."
    exit 1
    curl -O $URL_TO_USE
    bash $VERSION_TO_USE -p "$HOME"/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    source $HOME/miniconda/bin/activate
    echo "conda init"
    conda init "$SHELL"
    exec $SHELL
fi

if ! conda --version; then
    echo "conda is not accessible. Check if the installation was successful."
    exit 1
fi

# Check if the environment exists
if conda info --envs | grep -q $ENV_NAME; then
    echo "$ENV_NAME environment already exists."
else
    # Create a new environment
    echo "Creating $ENV_NAME environment..."
    conda create -y --name $ENV_NAME python=3.11
fi

# Activate the new environment
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Check if the environment is activated, for debugging purposes
# conda info --envs | grep "$ENV_NAME"; exit 1

# Install the requirements using pip
pip install -r requirements.txt


echo ""
echo "install complete. You can check if the environment can be activated by running:"
echo "conda activate $ENV_NAME"
