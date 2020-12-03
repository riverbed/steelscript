#!/bin/bash
# Riverbed Community Toolkit
# sanity-check-001.sh
#
# Sanity check for PyPI Distribution
# Check Latest SteelScritpt PyPi packages installation
#
# Usage
# - setup the target env.
# - run sanity-check-001.sh

pip install steelscript steelscript.appresponse sleepwalker steelscript-cmdline steelscript.netprofiler  steelscript.scc steelscript.steelhead steelscript.wireshark

apt-get update && apt-get install -y libpcap-dev --no-install-recommends
pip install -c requirements.txt --use-feature=2020-resolver steelscript.packets 

# Checks

## check dependencies
pip list

# check steelscript starts
steel
