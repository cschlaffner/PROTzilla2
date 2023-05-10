#!/bin/bash

ENV_NAME="protzilla"

if ! [[ "$OSTYPE" == "linux-gnu"* ]] && ! [[ "$OSTYPE" == "darwin"* ]]; then
  echo "OS not supported, use the install_windows.bat script (to be written)."
  exit 1
fi

if ! conda --version > /dev/null; then
  echo "conda is not accessible. Checking if conda is installed..."
  if ! [ -d "$HOME/miniconda3" ] && ! [ -d "$HOME/anaconda3" ]; then
    echo "Miniconda or Anaconda are not installed. Running install_unix.sh..."
    ./install_scripts/install_unix.sh
  else
    echo "conda seems to be installed but not accessible. Check your path"
    exit 1
  fi
  if ! conda --version; then
    echo "conda is still not accessible. Check if the installation was successful."
    exit 1
  fi
fi

eval "$(conda shell.bash hook)"
ENV_STRING=$(conda info --envs | grep "$ENV_NAME")

if [ "$ENV_STRING" == "" ]; then
  echo "'$ENV_NAME'-environment doesn't exist yet. Running create_env.sh..."
  ./install_scripts/create_env.sh
  echo "created '$ENV_NAME'-environment."
fi

ENV_STRING=$(conda info --envs | grep "$ENV_NAME")
if ! grep -q "\*" <<<"$ENV_STRING"; then
  echo "Activating '$ENV_NAME'-environment..."
  eval "$(conda shell.bash hook)"
  conda activate "$ENV_NAME"
  echo "activated '$ENV_NAME'-environment."
fi

# for debugging, should be python3.11.xx
# python --version

cd "$(dirname $0)"

echo "checking for and installing new requirements..."
pip install -q -r requirements.txt
echo "done."

echo "starting protzilla..."
python ui/manage.py runserver
echo "quit protzilla"
