# Riverbed SteelScript

[![Documentation Status](https://readthedocs.org/projects/steelscript/badge/?version=latest)](https://steelscript.readthedocs.io/en/latest/?badge=latest)

Riverbed SteelScript is a collection of libraries and scripts written in Python for interacting with Riverbed solutions and appliances, and other network infrastructure devices.

## Quick Start

Here are 4 things you can do to start quick and easy with SteelScript.

<details>
  <summary>Try examples just with git and Docker</summary>

### Quick Start SteelScript examples in a container

If you have [git](https://git-scm.com/downloads) and [Docker](https://www.docker.com/get-started) installed, for example on a Linux machine in your lab.

Open your shell (bash or PowerShell), build SteelScript from the latest source code and run it locally in a Docker container as follows:

#### Build and run SteelScript in a container

Build a docker image:

```shell
# Build a docker image from latest code
docker build --tag steelscript:latest https://github.com/riverbed/steelscript.git
```

Run SteelScript in a container:

```shell
# Run the image in an interactive container
docker run -it steelscript:latest /bin/bash
```

#### Try examples

You can try some script examples.


1. **AppResponse example**, print the Host Groups:

```shell
python examples/steelscript-appresponse/print_hostgroups-formatted.py {appresponse fqdn or IP address} -u {admin account} -p {password}
```

2. **Client Accelerator Controller example**, get the licenses and services:

```shell
python examples/steelscript-cacontroller/cacontroller-rest_api.py {client accelerator controller fqdn or IP address} --access_code {access_code}
```

3. **NetIM example**, list the Devices:

```shell   
python examples/steelscript-netim/print-netim-devices-raw.py {netim core fqdn or IP address} --username {account} --password {password}
```

4. **NetProfiler example**, get the list of the Ports Top Talkers:

```shell
python examples/steelscript-netprofiler/top_ports.py {netprofiler fqdn or IP address} -u {admin account} -p {password}
```

</details>

<details>
  <summary>Try SteelScript notebooks, just with git and Docker</summary>

### Quick Start SteelScript notebooks in a container 

If you have [git](https://git-scm.com/downloads) and [Docker](https://www.docker.com/get-started) installed.
You can build a steelscript container image that includes the Jupyter server and allows to run notebooks.

Build both steelscript bash imags and notebook image:

```shell
# Build the steelscript base image
docker build --tag steelscript:latest https://github.com/riverbed/steelscript.git

# Build the steelscript image for Jupyter Notebook
docker build --tag steelscript.notebook -f Dockerfile.notebook https://github.com/riverbed/steelscript.git
```

Run a container with the steelscript.notebook image. It contains the Jupyter Notebook server and will be listening on port 8888 by default.

```shell
# Start the steelscript.notebook container with built-in Jupyter Notebook
docker run --init --rm -p 8888:8888 --name=steelscript.notebook steelscript.notebook
```

In the output, grab the url containing the *token*, for example *http://127.0.0.1:8888/tree?token=123456* , and open it in your browser to log into the Jupyter web-console.

From there, in the *Notebooks* folder you can find some notebooks based on SteelScript:

* **AppResponse**: [01-appresponse-hostgroups.ipynb](https://github.com/riverbed/steelscript-appresponse/blob/master/notebooks/01-appresponse-hostgroups.ipynb)
* *work in progress* NetProfiler

</details>

<details>
  <summary>Try SteelScript notebooks in your own SteelScript environment, just with python, pip, git and vscode</summary>

### Quick Start SteelScript notebooks in your environment

If you have all the tools ready:
1. [Python](https://www.python.org/downloads) and pip
2. [git](https://git-scm.com/downloads)
3. [Visual Studio Code](https://code.visualstudio.com)
   
Download a notebook for SteelScript, open it in Visual Studio Code and your good to go:

* *work in progress* [Steelscript](https://github.com/riverbed/Riverbed-Community-Toolkit/SteelScript) in the [Riverbed Community Toolkit](https://github.com/riverbed/Riverbed-Community-Toolkit)
* **AppResponse**: [Hostgroups](https://github.com/riverbed/steelscript-appresponse/blob/master/notebooks/01-appresponse-hostgroups.ipynb)

> Jupyter Notebook files have .ipynb extension, [more about Jupyter Notebook](https://jupyter.org)

</details>

<details>
  <summary>Just install SteelScript modules in your Python environment, with pip and git</summary>

### Quick Start SteelScript in your environment

If you have all the tools installed in your environment: [Python](https://www.python.org/downloads), pip, and [git](https://git-scm.com/downloads)

Then, open your shell (bash or PowerShell) to install SteelScript and modules (directly from the latest source code):

```shell
# Install SteelScript and modules
pip install git+https://github.com/riverbed/steelscript
pip install git+https://github.com/riverbed/steelscript-appresponse
pip install git+https://github.com/riverbed/steelscript-netim
pip install git+https://github.com/riverbed/steelscript-netprofiler
pip install git+https://github.com/riverbed/steelscript-steelhead
pip install git+https://github.com/riverbed/steelscript-scc
# ... and others check the list on https://github.com/orgs/riverbed/repositories?q=steelscript
```

> Find all the steelscript modules: [steelscript repositories](https://github.com/orgs/riverbed/repositories?q=steelscript)

</details>

## Get SteelScript

SteelScript and modules are distributed via [Riverbed on GitHub](https://github.com/riverbed). The main repository is [SteelScript](https://github.com/riverbed/steelscript).

To use SteelScript, it is recommended to either build your own SteelScript container or install the SteelScript modules in your own Python environment directly from the source on GitHub main repository. Refer to the quickstarts in the section above - *the guide needs update*.

> [!NOTE]
> Other distributions have not been maintained and contain outdated versions of SteelScript: [*outdated* SteelScript on Dockerhub](https://hub.docker.com/r/riverbed/steelscript), [*outdated* SteelScript in pypi](https://pypi.org/search/?q=steelscript), ...

## Guide

> [!NOTE]
> The [SteelScript guide](https://support.riverbed.com/apis/steelscript) needs a good refresh. The source is there: [*outdated* source in docs subfolder](docs)

## About SteelScript

### The Framework

The common module for SteelScript is in the [SteelScript repository](https://github.com/riverbed/steelscript). It contains common code but also it is the entrypoint for Documentation, Build, Test and releases.

Other SteelScript modules have their own repository. The repository name is prefixed by "steelscript": [List of SteelScript repositories](https://github.com/orgs/riverbed/repositories?q=steelscript)

#### Modules for Riverbed products and appliances:

- [AppResponse](https://github.com/riverbed/steelscript-appresponse)
- [NetIM](https://github.com/riverbed/steelscript-netim)
- [NetProfiler](https://github.com/riverbed/steelscript-netprofiler)
- [SteelHead](https://github.com/riverbed/steelscript-steelhead)
- [SteelHead Controller](https://github.com/riverbed/steelscript-scc), also called SCC
- [Client Accelerator Controller (CAC)](https://github.com/riverbed/steelscript-client-accelerator-controller), formerly called SteelHead Mobile controller, SMC or SCCM

#### Extra modules

- [Wireshark](https://github.com/riverbed/steelscript-wireshark)
- [NetShark](https://github.com/riverbed/steelscript-netshark)
- [Packets](https://github.com/riverbed/steelscript-packets)
- [Command line Access](https://github.com/riverbed/steelscript-cmdline)

#### Other repos for components and SteelScript extensions:

> [!NOTE]
> The following have known issues and maintenance is pending

- *pending mantenance* [Application Framework](https://github.com/riverbed/steelscript-appfwk)
- *pending mantenance* [Business hour reporting plugin for Application Framework](https://github.com/riverbed/steelscript-appfwk-business-hours)
- *pending mantenance* [Stock report demo with Application Framework](https://github.com/riverbed/steelscript-appfwk-business-hours)
- *pending mantenance* [VM Config](https://github.com/riverbed/steelscript-vm-config)

<details>
  <summary>More about SteelScript</summary>

### Folder Structure for Modules

SteelScript is based on Python 3.
The repos of SteelScript modules have a common structure 

```
   steelscript-module-name        # for example: steelscript-appresponse
   ├── README.md or README.rst    # Markdown is preferred (.md) and reStructuredText (.rst)
   ├── LICENSE
   ├── CHANGELOG
   ├── .gitignore
   ├── docs
   ├── steelscript
   │   ├── __init__.py
   │   └── module-name            # for example: appresponse
   │       ├── core
   │       │   └── __init__.py
   │       ├── commands
   │       │   └── __init__.py
   │       └── __init__.py
   ├── tests
   ├── setup.py
   ├── examples
   ├── notebooks
   └── tox.ini
```

Mandatory:

- README.md (or README.rst): README in Markdown (.md) or reStructuredText (.rst) format. Markdown is preferred.
- LICENSE: Riverbed Technology copyright, terms and conditions based on MIT
- CHANGELOG: Simple text file tracking major changes
- /docs: Documentation using reStructured Text (rst) file format.
- /examples: Python scripts samples showing how to use the module (only .py files)
- /steelscript: The actual code, written in Python (Python 3).
- /tests: Test plans and unit test. Can be organized in subfolders. Test plan are ideally documented and easy to run scripts but can be anything defining a test plan (script, text, ...), for example a Python script based on pytest.
- setup.py: Python setup file containing meta descriptions and requirements. Based on setuptools, distutils and pytest. Should NOT contain unit test (use Tox and put unit test inside /tests folder instead)


Optional:

- /notebooks: Notebooks based on [Jupyter](https://jupyter.org)
- /tox.ini: standardized python testing definition based on [Tox](https://tox.readthedocs.io/en/latest)


> Contributions for alternative distribution methods and packaging (like pypi, rpm, .deb, rpm, tgz, ...) can be organized inside the `/packaging` folder in the main [SteelScript repository](https://github.com/riverbed/steelscript)

### Build

Builds are defined in the [SteelScript repository](https://github.com/riverbed/steelscript)

#### Prebuild test-plans validations

Execute test-plans with tox

```shell
  pip install tox
  tox
```  
 
#### Building Docker containers

Some Dockerfile are provided to build different flavors of the SteelScript container image:

- Dockerfile: standard build
- Dockerfile.slim: optimized build
- Dockerfile.notebook: build for demo and learning with Notebooks
- Dockerfile.dev: build development and testing container from master or fork/branch


<details>
  <summary>Build snippets</summary>

##### Standard:

```shell
  docker build --tag steelscript -f Dockerfile .
```  

##### Slim:

```shell
  docker build --tag steelscript.slim -f Dockerfile.slim .
```  

##### Notebook

```shell
  docker build --tag steelscript.notebook -f Dockerfile.notebook .
```

</details>

<details>
  <summary>Dev snippets</summary>

##### Dev from master

```shell
  git clone https://github.com/riverbed/steelscript --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-netprofiler --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-wireshark --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-cmdline --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-scc --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-appresponse --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-netim --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-client-accelerator-controller --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-steelhead --depth 1 --recurse-submodules
  git clone https://github.com/riverbed/steelscript-packets.git --depth 1 --recurse-submodules

  docker build --tag steelscript.dev --progress=plain -f steelscript/Dockerfile.dev .
```

##### Dev from your_fork/your_branch

```shell
  git clone https://github.com/your_fork/steelscript --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-netprofiler --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-wireshark --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-cmdline --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-scc --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-appresponse --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-netim --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-client-accelerator-controller --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-steelhead --depth 1 --recurse-submodules -b your_branch
  git clone https://github.com/your_fork/steelscript-packets.git --depth 1 --recurse-submodules -b your_branch

  docker build --tag steelscript.dev --progress=plain -f steelscript/Dockerfile.dev .
```  

</details>

</details>

##  Contribute

Feel free to use, enhance and contribute by creating issues, sending pull requests (PR), extending with new modules ...

## License

Copyright (c) 2021-2024 Riverbed Technology, Inc.

SteelScript is licensed under the terms and conditions of the MIT License
accompanying the software ("License").  SteelScript is distributed "AS
IS" as set forth in the License. SteelScript also includes certain third
party code.  All such third party code is also distributed "AS IS" and is
licensed by the respective copyright holders under the applicable terms and
conditions (including, without limitation, warranty and liability disclaimers)
identified in the license notices accompanying the software.
