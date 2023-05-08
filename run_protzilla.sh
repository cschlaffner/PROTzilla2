#!/bin/bash

ENV_NAME="protzilla"


if ! [ -d "$HOME/miniconda3" ] && ! [ -d "$HOME/anaconda3" ]; then
    echo "Miniconda or Anaconda are not installed. Running install_unix.sh..."
    ./install_scripts/install_unix.sh
fi
if ! eval "$(conda shell.bash hook)" && conda activate "$ENV_NAME"; then
    echo "conda is not accessible. Check if the installation was successful."
    exit 1
fi
python --version
conda activate "$ENV_NAME"
python --version
python ui/manage.py runserver
