SteelScript Application Framework Installation
==============================================

The SteelScript Application Framework is distributed entirely as
Python packages via the Python Package Index `PyPI
<https://pypi.python.org/pypi>`_.  This makes it easy to install
and upgrade the base framework pacakge as well as any plugins.

Quick Install
-------------

Checklist:

1. ``steelscript`` installed (if not see :doc:`/install/toc`)

2. Running Linux / Mac (for Windows, see :ref:`appfwk_install_detailed` below)

3. Developer tools installed (gcc/g++ or the like)

If you can check off all of the above, simply run (in a `virtualenv
<http://www.virtualenv.org/>`_):

.. code:: bash

   $ steel install --appfwk

This will install all the additional packages related to the
Application Framework.  It may take some time, often 10 minutes or so,
it has to compile NumPy and Pandas packages.  (Tail the log in
~/.steelscript/steel.log if you want to see what's happening behind
the scenes).

.. _appfwk_install_detailed:

Detailed Installation
---------------------

If you're familiar with ``pip`` and Python package
installation, the latest stable versions of these packages are hosted
on `PyPI`_ - the Python Package Index.

The following packages are related to the Application Framework:

* ``steelscript.appfwk``
  (`PyPI <https://pypi.python.org/pypi/steelscript.appfwk>`__,
  `GitHub
  <https://github.com/riverbed/steelscript-appfwk/releases>`__) -
  the core modules and data files for the Application Framework

* ``steelscript.wireshark``
  (`PyPI <https://pypi.python.org/pypi/steelscript.wireshark>`__,
  `GitHub
  <https://github.com/riverbed/steelscript-wireshark/releases>`__) -
  extensions to analyze PCAP files using Wireshark / tshark

* ``steelscript.appfwk.business-hours``
  (`PyPI <https://pypi.python.org/pypi/steelscript.appfwk.business-hours>`__,
  `GitHub
  <https://github.com/riverbed/steelscript-appfwk-business-hours/releases>`__) -
  adds support for running any report over business hours only

The primary package is ``steelscript-appfwk``.  Installing this will
pull in a number of dependencies.  The exact dependencies will change
over time as new features are added.  When installing via ``pip``,
the dependencies will be installed automatically.

Note that the base packages such as ``steelscript.netprofiler`` and
``steelscript.netshark`` include support for the Application
Framework.

There are two package dependencies that deserve special attention:

* `NumPy <http://www.numpy.org/>`_ (
  `PyPI <https://pypi.python.org/pypi/numpy>`__
  `downloads <http://sourceforge.net/projects/numpy/files/>`__) -
  scientific computing with Python

* `Python Pandas <http://pandas.pydata.org/>`_ (
  `PyPI <https://pypi.python.org/pypi/pandas/0.13.1/>`__
  `Windows binaries <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pandas>`__) -
  Python Data Analysis Library

These packages are heavily used for data tables and manipulation.
Both packages have large portions written in C for performance, thus
they must be compiled.  For Linux / Mac, it is usually sufficient just
to ensure that the developer tools are installed.  For Windows, there
are two ways to install these packages.  One way is to install
the Microsoft Visual C++ Compiler for Python 2.7 which you can download
from `here <http://aka.ms/vcpython27>`__. This package
compiles the source code of the `numpy` and `pandas` packages.  Another way
is to install these packages from pre-compiled distributions (see their respective web sites).

.. note::

   Installing numpy and pandas packages can often take a
   significant amount of time (~10 minutes).  During compilation
   it is normal to see numerous warnings go by.

Other than the special cases described above, the installation is identical
to installation for core SteelScript.  Follow the directions described in
one of the guides below to install ``steelscript`` along with any
product specific packages.   Then install ``steelscript.appfwk`` in the
same manner:

* :doc:`/install/toc`
* :doc:`/install/linuxmac`
* :doc:`/install/windows`

You can check your installation using ``steel about``:

.. code-block:: bash

   $ steel about

   Installed SteelScript Packages
   Core packages:
     steelscript                               0.6.0.post43
     steelscript.netprofiler                   0.6.0.post23
     steelscript.netshark                      0.6.0.post21
     steelscript.wireshark                     0.0.1

   Application Framework packages:
     steelscript.appfwk                        0.1.0.post34
     steelscript.appfwk.business-hours         0.1.0.post17

   Paths to source:
     /Users/admin/env/ss/lib/python2.7/site-packages
