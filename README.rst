Riverbed SteelScript
====================

Riverbed SteelScript is a collection of libraries and scripts written in Python for interacting
with Riverbed solutions and appliances, and other network infrastructure devices.

Quick Start 
-----------

If you have git and Docker installed.
Open your shell (bash or PowerShell), build SteelScript from the latest source code and run it locally in a Docker container as follows:

.. code:: shell

  # Build a docker image from latest code
  docker build --tag steelscript:latest https://github.com/riverbed/steelscript.git
  
  # Run the image in an interactive container
  docker run -it steelscript:latest /bin/bash
  
From here you can start to use the SteelScript framework.

You can try some app examples like printing the Host Groups of an AppResponse appliance:

.. code:: shell

  python examples/appresponse-examples/print_hostgroups-formatted.py {appresponse fqdn or IP address} -u {admin account} -p {password}
  

Get the licenses and services of a Client Accelerator Controller appliance:

.. code:: shell
   
   python examples/cacontroller-examples/cacontroller-rest_api.py {client accelerator controller fqdn or IP address} --access_code {access_code}

List the devices from NetIM Core:

.. code:: shell
   
   python examples/netim-examples/print-netim-devices-raw.py {netim core fqdn or IP address} --username {account} --password {password}


Contribute
-----------

Feel free to use, enhance and contribute by creating issues, sending pull requests (PR), extending with new modules ...


Python Compatibility Note
-------------------------

The SteelScript 2.x series of packages support Python 3. The 1.8.X series of SteelScript packages are the last to support
Python 2.

For a complete guide with installation details, see:

  `https://support.riverbed.com/apis/steelscript <https://support.riverbed.com/apis/steelscript>`_


Framework
=========

The common module for SteelScript is in the `SteelScript repo <https://github.com/riverbed/steelscript>`__
It contains common code but also it is the entrypoint for Documentation, Build, Test and releases.

Other SteelScript modules have their own repository which
can be found in the `Riverbed GitHub org <https://github.com/riverbed>`__, the name is prefixed by "steelscript".

Modules for Riverbed products and appliances:

- `SteelHead <https://github.com/riverbed/steelscript-steelhead>`__
- `SteelHead Controller (a.k.a SCC) <https://github.com/riverbed/steelscript-scc>`__
- `Client Accelerator Controller (formerly called SteelHead Mobile controller, SMC or SCCM) <https://github.com/riverbed/steelscript-client-accelerator-controller>`__
- `NetIM <https://github.com/riverbed/steelscript-netim>`__
- `NetProfiler <https://github.com/riverbed/steelscript-netprofiler>`__
- `AppResponse <https://github.com/riverbed/steelscript-appresponse>`__
- `Wireshark <https://github.com/riverbed/steelscript-wireshark>`__
- `NetShark <https://github.com/riverbed/steelscript-netshark>`__
- SteelConnect-CX
- SteelConnect-EX

Extra modules

- `Packets <https://github.com/riverbed/steelscript-packets>`__
- `Command line Access <https://github.com/riverbed/steelscript-cmdline>`__

Other repos for components and SteelScript extensions:

- `Application Framework <https://github.com/riverbed/steelscript-appfwk>`__
- `- Business hour reporting plugin for Application Framework <https://github.com/riverbed/steelscript-appfwk-business-hours>`__
- `- Stock report demo with Application Framework <https://github.com/riverbed/steelscript-appfwk-business-hours>`__
- `VM Config <https://github.com/riverbed/steelscript-vm-config>`__ 

Folder Structure for Modules
----------------------------

The repos of SteelScript modules have a common structure 

.. code-block:: raw
   
   steelscript-module-name     # for example: steelscript-appresponse
   ├── README.rst
   ├── LICENSE
   ├── CHANGELOG
   ├── .gitignore
   ├── docs
   ├── examples
   ├── steelscript
   │   ├── __init__.py          # default content: __import__("pkg_resources").declare_namespace(__name__)
   │   └── module-name          # for example: appresponse
   │       ├── core
   │       │   └── __init__.py
   │       ├── commands
   │       │   └── __init__.py
   │       └── __init__.py
   ├── tests
   ├── setup.py
   ├── notebooks
   └── tox.ini
 

Mandatory:

- README.rst: simple description using reStructured Text (rst) file format
- LICENSE: Riverbed Technology copyright, terms and conditions based on MIT
- CHANGELOG: Simple text file tracking major changes
- /docs: Documentation using reStructured Text (rst) file format.
- /examples: Python scripts samples showing how to use the module.
- /steelscript: The actual code, written in Python. Must be Python3 only.
- /tests: Test plans and unit test. Can be organized in subfolders. Test plan are ideally documented and easy to run scripts but can be anything defining a test plan (script, text, ...), for example a python script based on pytest.
- setup.py: Python setup file containing meta descriptions and requirements. Based on setuptools, distutils, gitpy-versioning (custom versioning tool https://github.com/riverbed/gitpy-versioning) and pytest. Should NOT contain unit test (use Tox and put unit test inside /tests folder instead)


Optional:

- /tox.ini: standardized python testing definition based on `Tox <https://tox.readthedocs.io/en/latest/>`__
- /notebooks: Notebooks based on `Jupyter <https://jupyter.org/>`__

Build
-----

Builds are defined in the `SteelScript repo <https://github.com/riverbed/steelscript>`__ 

**Prebuild test-plans validations**

*todo*

Execute test-plans with tox

.. code:: shell

  pip install tox
  tox
 
**Building Docker containers**

Some Dockerfile are provided to build different flavors of the SteelScript container image:

- Dockerfile: standard build
- Dockerfile.slim: optimized build
- Dockerfile.notebook: build for demo and learning with Notebooks

Standard:

.. code:: shell

  docker build --tag steelscript -f Dockerfile .

Slim:

.. code:: shell

  docker build --tag steelscript.slim -f Dockerfile.slim .

Notebook

.. code:: shell

  docker build --tag steelscript.notebook -f Dockerfile.notebook .


Distribution
------------

The recommendation is to use SteelScript in a Docker container or install directly from the python code publicly available in Github.
In the `SteelScripts docs <https://support.riverbed.com/apis/steelscript>`__ there are more details about other installation methods but Docker is the easiest.

The goal is to be able to release each new version (corresponding to a tag in the master branch) at least in a Docker public repository: `SteelScript on Docker Hub <https://hub.docker.com/r/riverbed/steelscript>`__

For contribution for alternative distribution methods and packaging (like pypi, rpm, .deb, rpm, tgz,...), artifacts will be organized inside /packaging and /test subfolders. We might need to dedicate another repo.

License
=======

Copyright (c) 2021 Riverbed Technology, Inc.

SteelScript is licensed under the terms and conditions of the MIT License
accompanying the software ("License").  SteelScript is distributed "AS
IS" as set forth in the License. SteelScript also includes certain third
party code.  All such third party code is also distributed "AS IS" and is
licensed by the respective copyright holders under the applicable terms and
conditions (including, without limitation, warranty and liability disclaimers)
identified in the license notices accompanying the software.
