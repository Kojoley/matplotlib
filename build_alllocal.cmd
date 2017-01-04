:: This assumes you have installed all the dependencies via conda packages:
:: # create a new environment with the required packages
:: conda create  -n "matplotlib_build" python=3.4 numpy python-dateutil pyparsing pytz tornado "cycler>=0.10" tk freetype
:: activate matplotlib_build
:: if you want qt backend, you also have to install pyqt
:: conda install pyqt
:: # this package is only available in the conda-forge channel
:: conda install -c conda-forge msinttypes
:: if you build on py2.7:
:: conda install -c conda-forge functools32

set TARGET=bdist_wheel
IF [%1]==[] (
    echo Using default target: %TARGET%
) else (
    set TARGET=%1
    echo Using user supplied target: %TARGET%
)

IF NOT DEFINED CONDA_PREFIX (
    echo No Conda env activated: you need to create a conda env with the right packages and activate it!
    GOTO:eof
)

:: build the target
python setup.py %TARGET%
