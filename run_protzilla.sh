#!/bin/bash

ENV_NAME="protzilla"

# check if the script is running on macos or linux
if ! [[ "$OSTYPE" == "linux-gnu"* ]] && ! [[ "$OSTYPE" == "darwin"* ]]; then
  echo "OS not supported, use the install_windows.sh script (to be written)."
  exit 1
fi

if ! conda --version; then
  echo "conda is not accessible. Checking if conda is installed..."
  if ! [ -d "$HOME/miniconda3" ] && ! [ -d "$HOME/anaconda3" ]; then
    echo "Miniconda or Anaconda are not installed. Running install_unix.sh..."
    ./install_scripts/install_unix.sh
  else
    echo "conda seems to be installed but not accessible. Check your path"
    exit 1
  fi
  if ! eval "$(conda shell.bash hook)" && conda activate "$ENV_NAME"; then
    echo "'$ENV_NAME'-environment doesn't exist yet. Running create_env.sh..."
    ./install_scripts/create_env.sh
  fi
fi

ENV_STRING=$(conda info --envs | grep "$ENV_NAME")

python --version
if ! grep -q "\*" <<< "$ENV_STRING"; then
  eval "$(conda shell.bash hook)"
  conda activate protzilla
fi
python --version
python ui/manage.py runserver
