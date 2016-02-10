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

Get started with App Framework by downloading and running a Virtual
Machine with it pre-installed and configured.  The latest links
and guides can be found on our 
`Splash site <https://splash.riverbed.com/docs/DOC-4860>`_.

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
  * :doc:`steelhead/tutorial`
  * :doc:`scc/tutorial`

* Device modules

  * :doc:`netprofiler/overview`
  * :doc:`netshark/overview`
  * :doc:`steelhead/overview`
  * :doc:`scc/overview`

* App Framework and VM

  * :doc:`appfwk/overview`
  * :doc:`vmconfig/overview`

* Library modules

  * :doc:`common/overview`
  * :doc:`cmdline/overview`

* REST tools and libraries

  * `reschema <reschema/index.html>`__
  * `Sleepwalker <Sleepwalker/index.html>`__

License
-------

This Riverbed SteelScript for Python documentation is provided "AS IS"
and without any warranty or indemnification.  Any sample code or
scripts included in the documentation are licensed under the terms and
conditions of the MIT License.  See the :doc:`license` page for more
information.

.. toctree::
   :hidden:
   :numbered:
   :maxdepth: 3

   install/toc
   steel
   common/toc
   netprofiler/toc
   netshark/toc
   steelhead/toc
   scc/toc
   appfwk/toc
   cmdline/toc
   vmconfig/toc
   reschema/toc
   sleepwalker/toc
