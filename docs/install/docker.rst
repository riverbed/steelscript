SteelScript Installation - Docker
=================================

Install Docker on your laptop or on any VM, then run the following commands to get
a fresh workspace waiting::

$docker pull riverbed/steelscript:latest
$docker run -it riverbed/steelscript

root@ad362292781f:~/steelscript-workspace# steel about

Installed SteelScript Packages
Core packages:
  steelscript                               2.0
  steelscript.appresponse                   2.0.1
  steelscript.cmdline                       2.0
  steelscript.netprofiler                   2.0
  steelscript.packets                       2.0
  steelscript.scc                           2.0
  steelscript.steelhead                     2.0
  steelscript.wireshark                     2.0

Application Framework packages:
  None

Inside that steelscript-workspace directory you will see exxample scripts for our various
packages which you can use right away, or copy to start your own scripts.

SteelScript Notebooks
-------------------------

The Docker containers for Jupyter notebooks have also been updated. Jupyter notebooks are
a really great way to play around and develop in the world of Python. Instructions on how
to get started are on the Docker page `https://hub.docker.com/r/riverbed/steelscript <https://hub.docker.com/r/riverbed/steelscript>`_


.. toctree::

   docker
   linuxmac
   windows
   steelhead
