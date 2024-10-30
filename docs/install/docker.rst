SteelScript in a Docker
======================================

.. note::

  Go to `SteelScript in GitHub <https://github.com/riverbed/steelscript>`_ for quick starts and more about the latest `SteelScript <https://github.com/riverbed/steelscript>`_ 
  
.. warning::
  
  This documentation has been created for SteelScript 2.0 at the time of Python 2 and 3.8 and has not been updated and reviewed for a while. For latest information about SteelScript that works in containers, on Linux/Mac and Windows, supports Python 3.12+, notebooks and more, please refer to `SteelScript in GitHub <https://github.com/riverbed/steelscript>`_


SteelScript for Python SDK - includes all of the core SteelScript packages in one simple container. 

Quickstart
-----------------

Get Docker installed on your machine, laptop or VM. (Docker website: https://docs.docker.com/get-docker/)

Then the following commands run a SteelScript container and get a fresh workspace waiting. It will pull the latest version and drop you into a bash shell inside a SteelScript workspace.

.. code-block:: bash
  
  docker run -it riverbed/steelscript

Now you can run some examples or start your own interactive Python session from here.
For example:

.. code-block:: bash

  root@ad362292781f:~/steelscript-workspace# steel about

  Installed SteelScript Packages
  Core packages:
    steelscript                               2.0
    steelscript.appresponse                   2.0.1
    steelscript.cmdline                       2.0
    steelscript.netprofiler                   2.0
    steelscript.scc                           2.0
    steelscript.steelhead                     2.0

  Application Framework packages:
    None

Inside that steelscript-workspace directory you will see exxample scripts for our various
packages which you can use right away, or copy to start your own scripts.

SteelScript Notebooks
-------------------------

The Docker containers for Jupyter notebooks have also been updated. Jupyter notebooks are
a really great way to play around and develop in the world of Python. Instructions on how
to get started are on the Docker page `https://hub.docker.com/r/riverbed/steelscript <https://hub.docker.com/r/riverbed/steelscript>`_

