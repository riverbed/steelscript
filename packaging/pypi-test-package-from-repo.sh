#!/bin/bash
# Riverbed Community Toolkit
#
# Test a PyPI Package existing in a PyPI repository
# Ref: https://packaging.python.org/tutorials/packaging-projects/#uploading-your-project-to-pypi
#
# Example testing a package of the SteelScript project publish on testpypi repo
#
# export PYPI_PACKAGE_URL="https://test.pypi.org/steelscript"
# export PYPI_PACKAGE="example-pkg-YOUR-USERNAME-HERE"
# 
# pypi-test-package-from-repo.sh 
#

if [ -z $PYPI_PACKAGE_URL ]; then
    echo "The following environment variables must be set before running the script:"
    echo "PYPI_PACKAGE_URL, for example: https://test.pypi.org/steelscript"
    echo "PYPI_PACKAGE, for example: example-pkg-YOUR-USERNAME-HERE "
    exit 1
fi

python3 -m pip install --index-url $PYPI_PACKAGE_URL --no-deps $PYPI_PACKAGE
