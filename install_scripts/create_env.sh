#!/bin/bash

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
