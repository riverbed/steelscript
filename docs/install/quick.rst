SteelScript Installation - Quick Guide
======================================

This page provides instructions for installing SteelScript and associated
modules for those that have experience with Python and package installation.

See the step by step installation guides for
:doc:`Linux/Mac <install_linuxmac>` and :doc:`Windows <install_windows>` for
detailed instructions.

Dependencies
------------

* Python version 2.6.x or 2.7.x - see `<http://www.python.org>`_
* Python `setuptools <https://pypi.python.org/pypi/setuptools>`_
* `pip <http://pip.readthedocs.org/en/latest/installing.html>`_ - the Python package installer
* Python `requests library <https://pypi.python.org/pypi/requests>`_

Installation via pip
--------------------

First install pip, if not already installed:

.. code-block:: bash

   $ easy_install pip

Then, install `steelscript.common
<https://github.com/riverbed/steelscript.common/releases>`_
as well as one or more product specific SteelScript modules:

.. code-block:: bash

   $ pip install steelscript.common
   $ pip install steelscript.netprofiler
   $ pip install steelscript.netshark

See `<http://github.com/riverbed>`_ for a complete list of additional SteelScript
packages available.

Start coding!

Download and Install
--------------------

The latest version of SteelScript can also be downloaded from `GitHub
<http://github.com/riverbed>`_.  This way the SDK can be installed
offline for environments that may not have internet access.

First, ensure that the dependencies listed above are downloaded and installed.

Download the `steelscript.common`_ package along with any other product
specific packages of interest:

* `steelscript.common <https://github.com/riverbed/steelscript.common/releases>`_
* `steelscript.netprofiler <https://github.com/riverbed/steelscript.netprofiler/releases>`_
* `steelscript.netshark <https://github.com/riverbed/steelscript.netshark/releases>`_

Upload to the target machine and install:

.. code-block:: bash

   $ pip install steelscript.common-0.6.0.tar.gz
   $ pip install steelscript.netprofiler-0.6.0.tar.gz
   $ pip install steelscript.netshark-0.6.0.tar.gz

Directory Layout
----------------

After installation, the steelscript package will be available to use
in Python via ``import steelscript``.  Examples and documentation are
also installed, but may be in different locations depending on your
specific environment.  Typical locations for each operating system are
as follows:

==========  =================================================================================== =======================
OS          Documentation                                                                       Scripts
==========  =================================================================================== =======================
Linux       ``/usr/local/share/doc/steelscript``                                                ``/usr/local/bin``
Mac         ``/System/Library/Frameworks/Python.framework/Versions/2.7/share/doc/steelscript``  ``/usr/local/bin``
Windows     ``C:\Python27\share\doc``                                                           ``C:\Python27\Scripts``
==========  =================================================================================== =======================

Upgrade and Uninstalling
------------------------

If you need to upgrade the SteelScript package to a newer version, and
you are offline, simply repeat the above installation steps.  This
will install the latest version alongside the older version.  Normally
you do not need to delete the older version.

With internet access, updates are as simple as:

.. code-block:: bash

   $ pip install -U steelscript.common

Repeat the above for each product specific SteelScript package,

If you need to completely uninstall the SteelScript package, you must
first find complete installation directory.  You can get this
directory from the flyscript-about.py command (shown above), or you
can run python:

.. code-block:: bash

   $ python
   >>> import steelscript.common
   >>> help(steelscript.common)

This will display the path to the package __init__.py file.  Delete
the entire directory leading up to steelscript/__init__.py.

Repeat as needed for additional SteelScript product packages.
