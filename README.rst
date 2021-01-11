Riverbed SteelScript
====================

Riverbed SteelScript is a collection of libraries and scripts written in Python for interacting
with Riverbed solutions and appliances, and other network infrastructure devices.

For a complete guide with installation details, see:

  `https://support.riverbed.com/apis/steelscript <https://support.riverbed.com/apis/steelscript>`_

**Recommendation**: Use SteelScript in a Docker container or directly from the python source code in Github!

Contribute
-----------

Feel free to use, enhance and contribute by creating issues, sending pull requests (PR), extending with new modules ...

Quick Start 
-----------

If you have git and Docker installed.
Open your shell (bash or PowerShell), build SteelScript from the latest source code and run it locally in a Docker container as follows:

.. code:: shell

  # Fetch the code and build a docker image
  git clone https://github.com/riverbed/steelscript.git
  cd steelscript
  docker build --tag steelscript:latest .
  
  # Run the image in an interactive container
  docker run -it steelscript:latest /bin/bash
  
From here you can start to use the SteelScript framework.

You can try some app examples like printing the Host Groups of an AppResponse appliance:

.. code:: shell

  python /examples/appresponse-examples/hostgroup.py appliance-ip-address -u admin -p password --operation=show
  

Python Compatibility Note
-------------------------

The SteelScript 2.x series of packages support Python 3. The 1.8.X series of SteelScript packages are the last to support
Python 2.


Framework
=========

The common module for SteelScript is in the `SteelScript repo <https://github.com/riverbed/steelscript>`__
It contains common code but also it is the entrypoint for Documentation, Build, Test and releases.

Other SteelScript modules have their own repository which
can be found in the `Riverbed GitHub org <https://github.com/riverbed>`__, the name is prefixed by "steelscript".

Modules for Riverbed solutions and appliances:

- `AppResponse <https://github.com/riverbed/steelscript-appresponse>`__
- `NetProfiler <https://github.com/riverbed/steelscript-netprofiler>`__
- `Packets <https://github.com/riverbed/steelscript-packets>`__
- `SteelHead <https://github.com/riverbed/steelscript-steelhead>`__
- `SteelHead Controller (a.k.a SCC) <https://github.com/riverbed/steelscript-scc>`__
- `Wireshark <https://github.com/riverbed/steelscript-wireshark>`__
- `NetShark <https://github.com/riverbed/steelscript-netshark>`__
- `Client Accelerator Controller (a.k.a. SMC) <https://github.com/riverbed/steelscript-client-accelerator-controller>`__

Extra modules

- `Command line Access <https://github.com/riverbed/steelscript-cmdline>`__

Other repos for components and SteelScript extensions:

- `Application Framework <https://github.com/riverbed/steelscript-appfwk>`__
- `- Business hour reporting plugin for Application Framework <https://github.com/riverbed/steelscript-appfwk-business-hours>`__
- `- Stock report demo with Application Framework <https://github.com/riverbed/steelscript-appfwk-business-hours>`__
- `VM Config <https://github.com/riverbed/steelscript-vm-config>`__ 

Folder Structure for Modules
----------------------------

The repos of SteelScript modules have a common structure 

Mandatory:

- README.rst: simple description using reStructured Text (rst) file format
- setup.py: Python setup file containing meta descriptions and requirements. Based on setuptools, distutils, gitpy-versioning (custom versioning tool https://github.com/riverbed/gitpy-versioning) and pytest. Should NOT contain unit test (use Tox and put unit test inside /tests folder instead)
- /docs: Documentation using reStructured Text (rst) file format.
- /steelscript: The actual code, written in Python. Must be Python3 only.
- /tests: Test plans and unit test. Can be organized in subfolders. Test plan are ideally documented and easy to run scripts but can be anything defining a test plan (script, text, ...), for example a python script based on pytest.
- /examples: Python scripts samples showing how to use the module.
- CHANGELOG: Simple text file tracking major changes
- LICENSE: Riverbed Technology copyright, terms and conditions based on MIT

Optional:

- /tox.ini: standardized python testing definition based on `Tox <https://tox.readthedocs.io/en/latest/>`__
- /notebooks: Notebooks based on `Jupyter <https://jupyter.org/>`__

Build
-----

Build are defined in the `SteelScript repo <https://github.com/riverbed/steelscript>`__ 

**Prebuild test-plans validations**

*todo*

Execute test-plans with tox

.. code:: shell

  pip install tox
  tox
 
**Building Docker containers**

3 Dockerfile are available to build different flavors of the SteelScript container image:

- Dockerfile: standard build
- Dockerfile-slim: optimized build
- Dockerfile-notebook: build for demo and learning with Notebooks

In the following code snippet just replace {{version}} with the actual version and run to get it built.

Standard:

.. code:: shell

  docker build --tag steelscript:{{version}} -f Dockerfile .

Slim:

.. code:: shell

  docker build --tag steelscript-slim:{{version}} -f Dockerfile-slim .

Notebook

.. code:: shell

  docker build --tag steelscript-notebook:{{version}} -f Dockerfile-notebook .


Distribution
------------

The recommendation is to use SteelScript in a Docker container or install directly from the python code publicly available in Github.
In the `SteelScripts docs <https://support.riverbed.com/apis/steelscript>`__ there are more details about other installation methods but Docker is the easiest.

The goal is to be able to release each new version (corresponding to a tag in the master branch) at least in a Docker public repository: `SteelScript on Docker Hub <https://hub.docker.com/r/riverbed/steelscript>`__

For contribution for alternative distribution methods and packaging (like pypi, rpm, .deb, rpm, tgz,...), artifacts will be organized inside /packaging and /test subfolders. We might need to dedicate another repo.

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
