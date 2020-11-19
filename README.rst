Riverbed SteelScript
====================

This is the top-level directory for the Riverbed SteelScript for
Python, a collection of libraries and scripts in Python for interacting
with Riverbed devices and other network infrastructure.

For a complete guide with installation details, see:

  `https://support.riverbed.com/apis/steelscript <https://support.riverbed.com/apis/steelscript>`_

Contribute
-----------

Feel free to use, enhance and contribute by creating issues, sendind pull requests (PR), ...

Quick Start 
-----------

If you have git and Docker installed.
Open your shell (bash or PowerShell), build SteelScript from the latest source code and run it locally in a Docker container as follows:

.. code:: shell

  git clone https://github.com/riverbed/steelscript.git
  cd steelscript
  docker build --tag steelscript:latest .
  
  docker run -it steelscript:latest /bin/bash

Python Compatibility Note
-------------------------

The SteelScript 2.x series of packages support Python 3. The 1.8.X series of SteelScript packages are the last to support
Python 2.  

License
=======

Copyright (c) 2020 Riverbed Technology, Inc.

SteelScript is licensed under the terms and conditions of the MIT License
accompanying the software ("License").  SteelScript is distributed "AS
IS" as set forth in the License. SteelScript also includes certain third
party code.  All such third party code is also distributed "AS IS" and is
licensed by the respective copyright holders under the applicable terms and
conditions (including, without limitation, warranty and liability disclaimers)
identified in the license notices accompanying the software.
