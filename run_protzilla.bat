@echo off
echo Welcome to PROTzilla

REM Check if Anaconda or Miniconda3 is installed
call conda --version >nul 2>&1
if %errorlevel% EQU 0 (
    echo conda already installed
    goto check_environment
)

echo Anaconda not already installed.
REM Check if Miniconda3 is installed
call miniconda --version >nul 2>&1
if %errorlevel% EQU 0 (
    echo Miniconda3 is already installed.
    goto check_environment
)
echo Miniconda3 not already installed.

REM Install Miniconda3
echo Downloading Miniconda3...
call powershell.exe -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile 'Miniconda3-latest.exe'"
echo Installing Miniconda3...
start "" /wait Miniconda3-latest.exe /InstallationType=JustMe /AddToPath=1 /S /D=%UserProfile%\Miniconda3
del Miniconda3-latest.exe
echo Miniconda3 installation completed.
echo please restart script
pause
goto :eof

:check_environment
REM Check if the environment exists
echo Checking if protzilla_win environment exists...
conda env list | findstr /C:"protzilla_win" >nul 2>&1
if %errorlevel% EQU 0 (
    echo protzilla_win environment already exists.
    goto activate_env
)

REM Create the environment
echo Creating protzilla_win environment...
call conda create -y --name protzilla_win python=3.11 -c conda-forge

echo protzilla_win environment created.

:activate_env
REM Activate the environment and install requirements
echo Activating protzilla_win environment...
call activate protzilla_win
pip install wheel
pip install -r requirements.txt
echo installed all requirements
REM Run Django server
python ui/manage.py runserver
