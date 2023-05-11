#!/bin/bash

if ! [[ "$OSTYPE" == "linux-gnu"* ]] && ! [[ "$OSTYPE" == "darwin"* ]]; then
  echo "OS not supported, use the install_windows.bat script (to be written)."
  exit 1
fi

ENV_NAME="protzilla"

# Check if the environment exists, create if not
if conda info --envs | grep -q "$ENV_NAME"; then
  echo "$ENV_NAME environment already exists."
else
  echo "Creating $ENV_NAME environment..."
  conda create -y --name $ENV_NAME python=3.11
fi

# Activate the new environment
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Check if the environment is activated, for debugging purposes
# conda info --envs | grep "$ENV_NAME"; exit 1

# Install the requirements using pip
echo "Installing requirements. This might take a while..."
pip install -r requirements.txt

echo "returning..."
