SteelScript SteelHead Installation
==================================

The SteelScript SteelHead Package is distributed entirely as
Python packages via the Python Package Index `PyPI
<https://pypi.python.org/pypi>`_.  This makes it easy to install
and upgrade the steelhead pacakge.

Quick Install
-------------

Checklist:

1. ``steelscript`` installed (if not see :doc:`/install/toc`)

2. Running Linux / Mac (for Windows, see :ref:`steelhead_install_detailed` below)

3. Developer tools installed (gcc/g++ or the like)

If you can check off all of the above, simply run (in a `virtualenv
<http://www.virtualenv.org/>`_):

.. code:: bash

   $ steel install --steelhead

This will install all the additional packages related to the
package of SteelScript SteelHead.

.. _steelhead_install_detailed:

Detailed Installation
---------------------

If you're familiar with ``pip`` and Python package
installation, the latest stable versions of these packages are hosted
on `PyPI`_ - the Python Package Index.

The following packages are related to the SteelScript SteelHead:

* ``steelscript.steelhead``
  (`PyPI <https://pypi.python.org/pypi/steelscript.steelhead>`__,
  `GitHub
  <https://github.com/riverbed/steelscript-steelhead/releases>`__) -
  the core modules and data files for the SteelScript SteelHead

* ``steelscript.cmdline``
  (`PyPI <https://pypi.python.org/pypi/steelscript.cmdline>`__,
  `GitHub
  <https://github.com/riverbed/steelscript-cmdline/releases>`__) -
  python modules for interacting with transport types, such as telnet and ssh. 

The primary package is ``steelscript.steelhead``.  Installing this will
pull in a number of dependencies.  The exact dependencies will change
over time as new features are added.  When installing via ``pip``,
the dependencies will be installed automatically.

.. _pycrypto:

There is one package dependency that deserves special attention:

* `Pycrypto <http://www.pycrypto.org/>`_ (
  `PyPI <https://pypi.python.org/pypi/crypto>`__
  `downloads <https://github.com/dlitz/pycrypto>`__) -
  Python Cryptography Toolkit

The Pycrypto package contains a collection of cryptographic modules
implementing various algorithms and protocols.  The package has a large
portion written in C, thus it must be compiled.  For Linux / Mac, it is
usually sufficient just to ensure that the developer tools are installed.
For Windows, it is recommended to install a special compiler,
Microsoft Visual C++ Compiler for Python 2.7, which you can download from
`here <http://aka.ms/vcpython27>`__.  This package provides the means
to compile the Pycrypto package from source.  Alternatively, you can
install the package from pre-compiled distributions, available from
`here <http://www.voidspace.org.uk/python/modules.shtml#pycrypto>`__.
Once the compiler or Pycrypto is installed, executing again the command
``steelscript install --steelhead`` will install all packages related
to the SteelScript Steelhead.

Other than the special case described above, the installation is identical
to installation for core SteelScript.  Follow the directions described in
one of the guides below to install ``steelscript`` along with any
product specific packages.   Then install ``steelscript.steelhead`` in the
same manner:

* :doc:`/install/toc`
* :doc:`/install/linuxmac`
* :doc:`/install/windows`

You can check your installation using ``steel about``:

.. code-block:: bash

   $ steel about

   Installed SteelScript Packages
   Core packages:
     steelscript                               0.9.6
     steelscript.cmdline                       0.5.0
     steelscript.netprofiler                   0.9.4
     steelscript.netshark                      0.9.4
     steelscript.steelhead                     0.5.0
     steelscript.wireshark                     0.9.4

   Application Framework packages:
     steelscript.appfwk                        0.9.7.1
     steelscript.appfwk.business-hours         0.9.6

   REST tools and libraries:
     None

   Paths to source:
     ~/steelscript/venv/lib/python2.7/site-packages

   (add -v or --verbose for further information)
