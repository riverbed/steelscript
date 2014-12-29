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

* `pycrypto <http://www.pycrypto.org/>`_ (
  `PyPI <https://pypi.python.org/pypi/crypto>`__
  `downloads <https://github.com/dlitz/pycrypto>`__) -
  Python Cryptography Toolkit

The pycrypto package contains a collection of cryptographic modules
implementing various algorithms and protocols.  The package has a large
portion written in C, thus it must be compiled.  For Linux / Mac, it is
usually sufficient just to ensure that the developer tools are installed.
For Windows, it is best to install the package from pre-compiled
distributions, such as `here <http://www.voidspace.org.uk/python/modules.shtml#pycrypto>`__.

If compiling pycrypto for windows is preferred over downloading pre-built package,
instructions are listed as follows (Assume the Operation System is 64-bit).

* Install the Python 64 bits version, downloaded from `here <http://www.python.org/ftp/python/2.7.1/python-2.7.1.amd64.msi>`__.

* Install the C Compiler for Windows - Microsoft Visual C++ Express Edition 2008. The reason
  is that Python 2.7 was built using the 2008 version.

* Install the Microsoft Windows SDK for Windows 7 and .NET Framework 3.5 SP1, available
  at `here <http://www.microsoft.com/downloads/en/details.aspx?FamilyID=c17ba869-9671-4330-a63e-1fd44e0e2505>`__.
  The ISO file to download (64bit) can be found at `here <http://download.microsoft.com/download/2/E/9/2E911956-F90F-4BFB-8231-E292A7B6F287/GRMSDKX_EN_DVD.iso>`__.
  This is required because the Micorsoft Visual C++ Express Edition 2008 does not contain the 64-bit
  compiler. Don't use the "Microsoft Windows SDK for Windows 7 and .NET Framework 4", because it is not compatible with Microsoft Visual
  C++ Express Edition 2008.

* Include in your Advanced Variables Environment the path of Python binaries. Left click the "Start" tab, 
  right click at "My Computer" icon, then left click "Properties", then click on "Advanced System Settings",
  then click on "Environment Variables. Edit your Path Variable to include two directories:
  ``C:\Python27`` and ``C:\Python27\Scripts``.

* Install Git BASH which can be downloaded from `here <https://msysgit.github.io>`__. Git BASH provides a lightweight
  BASH emulation used to run commands from shell. 

* There is a bug about building 64-bit binaries using Microsoft Visual C++ Express Edition 2008. A diff file
  ``vcvars4.diff`` can be downloaded at `here <http://bugs.python.org/file17959/vcvars4.diff>`__, which fixes the bug. To apply the fix,
  start Git BASH, grab the diff file and apply it to your Python main directory at ``C:\Python27`` by executing the command
  ``patch -p0 <vcvars4.diff``.

* Now it is time to build your pycrypto windows executable (.exe) file. Download the
  pycrypto-2.6.1.tar.gz from `here <https://pypi.python.org/pypi/pycrypto>`__. Unpack it, enter
  the pycrypto-2.6.1 directory and run the command as follows.

  .. code:: bash

    $ python setup.py bdist_wininst

* As a result you will get an executable file created inside the "dist" folder, which can be used to install
  pycrypto package on 64-bit Windows Systems.

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

   Paths to source:
     ~/steelscript/venv/lib/python2.7/site-packages

   (add -v or --verbose for further information)
