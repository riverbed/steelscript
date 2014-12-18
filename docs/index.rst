Riverbed SteelScript for Python
===============================

Welcome, this is the documentation for Riverbed SteelScript for Python
and the SteelScript Application Framework.  The core SteelScript is a
collection of Python modules that build upon REST APIs and other
interfaces to interact with Riverbed appliances and software.
The Application Framework is a Django-based web application infrastructure
that makes it easy to built web applications mashing up configuration
and statistics from throughout your network.

Quick Start
-----------

If you already have pip, just run the following (in a
`virtualenv <http://www.virtualenv.org/>`_)::

   $ pip install steelscript
   $ steel install

Not sure about pip, but you know you have Python?

1. Download :download:`steel_bootstrap.py`

2. Run it (in a `virtualenv <http://www.virtualenv.org/>`_)::

      $ python steel_bootstrap.py install

SteelScript Application Framework
---------------------------------

The SteelScript Application Framework makes it easy to create a fully
custom web application that mashes up data from multiple sources.  It comes
pre-configured with several reports for NetProfiler and NetShark.

Once you have the base ``steelscript`` package installed, getting started
is just a few commands away::

   $ steel install --appfwk
   $ steel appfwk mkproject

This will populate a local directory with all the files you need to run
the server in "dev" mode on your local system.

For more details, see the :doc:`complete documentation <appfwk/overview>`.

SteelScript SteelHead
---------------------

The SteelScript SteelHead offers a set of interfaces to control and work
with a SteelHead appliance. It comes pre-configured with a couple of example
scripts showing how to interact with a SteelHead appliance using interfaces
provided in this package.

Once you have the base ``steelscript`` package installed, getting started
is just one command away::

   $ steel install --steelhead

For more details, see the :doc:`complete documentation <steelhead/overview>`.

Documentation
-------------

* :doc:`toc`
* :doc:`Installation <install/toc>`

  * :doc:`Core Install Linux / Mac <install/linuxmac>`
  * :doc:`Core Install Windows <install/windows>`
  * :doc:`Install Application Framework <install/appfwk>`
  * :doc:`Install SteelScript SteelHead <install/steelhead>`

* :doc:`steel`

* Tutorials

  * :doc:`netprofiler/tutorial`
  * :doc:`netshark/tutorial`
  * :doc:`cmdline/tutorial`
  * :doc:`steelhead/tutorial`

* Core modules

  * :doc:`common/overview`
  * :doc:`netprofiler/overview`
  * :doc:`netshark/overview`

* :doc:`appfwk/overview`
* :doc:`vmconfig/overview`

* :doc:`cmdline/overview`
* :doc:`steelhead/overview`

License
-------

This Riverbed SteelScript for Python documentation is provided "AS IS"
and without any warranty or indemnification.  Any sample code or
scripts included in the documentation are licensed under the terms and
conditions of the MIT License.  See the :doc:`license` page for more
information.


.. toctree::
    :hidden:

    toc
