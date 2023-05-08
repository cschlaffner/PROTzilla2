@echo off

REM Check if Anaconda is installed
conda --version >nul 2>&1
if %errorlevel% EQU 0 (
    echo Anaconda is already installed.
    goto check_environment
)

REM Check if Miniconda3 is installed
miniconda --version >nul 2>&1
if %errorlevel% EQU 0 (
    echo Miniconda3 is already installed.
    goto check_environment
)

REM Install Miniconda3
echo Installing Miniconda3...
powershell.exe -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile 'Miniconda3-latest.exe'"
start "" /wait Miniconda3-latest.exe /InstallationType=JustMe /AddToPath=0 /S
del Miniconda3-latest.exe

echo Miniconda3 installation completed.

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
conda create --name protzilla_win

echo protzilla_win environment created.

:activate_env
REM Activate the environment
echo Activating protzilla_win environment...
call activate protzilla_win

echo protzilla_win environment activated.
