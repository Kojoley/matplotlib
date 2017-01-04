# Building on Windows

There are a few possibilities to build matplotlib on Windows:

* Wheels via [matplotlib-winbuild](https://github.com/jbmohler/matplotlib-winbuild)
* Wheels by using conda packages
* Conda packages

## Wheel builds using conda packages

This is a wheel build, but we use conda packages to get all the requirements. The binary
requirements (png, freetype,...) are statically linked and therefore not needed during the wheel
install.

The commands below assume that you can compile a native python lib for the python version of your
choice. See [this howto](http://blog.ionelmc.ro/2014/12/21/compiling-python-extensions-on-windows/)
how to install and setup such environments. If in doubt: use python 3.5 as it mostly works
without fiddling with environment variables.

``` sh
# create a new environment with the required packages
conda create  -n "matplotlib_build" python=3.4 numpy python-dateutil pyparsing pytz tornado "cycler>=0.10" tk freetype
activate matplotlib_build
# if you want a qt backend, you also have to install pyqt (be aware that pyqt doesn't mix well if
# you have created the environment with conda-forge already activated...)
conda install pyqt
# this package is only available in the conda-forge channel
conda install -c conda-forge msinttypes
# for python 2.7
conda install -c conda-forge functools32

# build the wheel
python setup.py bdist_wheel
```

The `build_alllocal.cmd` script automates these steps if you already created and activated the conda environment.


## Conda packages

This needs a [working installed C compiler](http://blog.ionelmc.ro/2014/12/21/compiling-python-extensions-on-windows/)
for the version of python you are compiling the package for but you don't need to setup the
environment variables.

```sh
# only the first time...
conda install conda-build

# the python version you want a package for...
set CONDA_PY=3.5

# builds the package, using a clean build environment
conda build ci\conda_recipe

# install the new package
conda install --use-local matplotlib
```
