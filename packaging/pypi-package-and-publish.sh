#!/bin/bash
# Riverbed Community Toolkit
#
# Package and Publish into PyPI repository
# Ref: https://packaging.python.org/tutorials/packaging-projects/#uploading-your-project-to-pypi
#
#
# Example for packaging the SteelScript project
#
# export PYPI_GIT_URL="https://github.com/riverbed/steelscript.git"
# export PYPI_REPOSITORY="testpypi"
# export PYPI_USERNAME="maintainer"
# export PYPI_PASSWORD="password"
#
# pypi-package-and-publish.sh 

###################


if [ -z $PYPI_GIT_URL ]; then
    echo "The following environment variables must be set before running the script:"
    echo "PYPI_GIT_URL, for exapmle: https://github.com/riverbed/steelscript.git"
    echo "PYPI_REPOSITORY, for example: testpypi, pypi "
    echo "PYPI_USERNAME, for examplge: maintainer"
    echo "PYPI_PASSWORD"

    exit 1
fi

git clone --recursive $PYPI_GIT_URL project
cd project

python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel

python3 -m pip install --user --upgrade twine
 
if [ $PYPI_REPOSITORY -eq "pypi" ]; then
    echo "Publishing on PyPI";
    python3 -m twine upload dist/* -u $PYPI_USERNAME -p $PYPI_PASSWORD
else
    echo "Publishing on $PYPI_REPOSITORY"
    python3 -m twine upload --repository $PYPI_REPOSITORY dist/*  -u $PYPI_USERNAME -p $PYPI_PASSWORD
fi