#!/bin/bash

ENV_NAME="protzilla"
CONDA_URL="https://repo.anaconda.com/miniconda/"
MINICONDA_PREFIX="Miniconda3-latest-"

URL_TO_USE=""
SCRIPT_NAME=""
OS_TO_USE=""
ARCHITECTURE_TO_USE=""

# check the processor architecture
if [ "$(uname -m)" == "x86_64" ]; then
  ARCHITECTURE_TO_USE="x86_64"
elif [ "$(uname -m)" == "arm64" ]; then
  ARCHITECTURE_TO_USE="arm64"
elif [ "$(uname -m)" == "aarch64" ]; then
  ARCHITECTURE_TO_USE="aarch64"
else
  echo "Architecture not supported."
  exit 1
fi

# check if the script is running on macos or linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  OS_TO_USE="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  OS_TO_USE="MacOSX"
else
  echo "OS not supported, use the install_windows.sh script (to be written)."
  exit 1
fi

SCRIPT_NAME="$MINICONDA_PREFIX$OS_TO_USE-$ARCHITECTURE_TO_USE.sh"
URL_TO_USE="$CONDA_URL$SCRIPT_NAME"
echo "Downloading $URL_TO_USE"

# Check if some sort of conda is already installed
if [ -d "$HOME/miniconda3" ] || [ -d "$HOME/miniconda" ] || [ -d "$HOME/anaconda3" ] || [ -d "$HOME/anaconda" ] || command -v conda >/dev/null 2>&1; then

  echo "Miniconda or Anaconda are already installed."
  conda init bash
else
  echo "Installing Miniconda..."
  echo "$URL_TO_USE"
  curl -O $URL_TO_USE
  bash $SCRIPT_NAME -p "$HOME"/miniconda
  export PATH="$HOME/miniconda/bin:$PATH"
  source $HOME/miniconda/bin/activate
  conda config --set auto_activate_base false
fi

if ! conda --version >/dev/null; then
  echo "conda is not accessible. Check if the installation was successful."
  exit 1
fi

if conda info --envs | grep -q "$ENV_NAME"; then
  echo "$ENV_NAME environment already exists."
else
  echo "creating environment..."
  ./install_scripts/create_env.sh
fi

echo ""
echo "install complete. You can check if the environment can be activated by running:"
echo "conda activate $ENV_NAME"
echo "returning..."

