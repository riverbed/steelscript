SteelScript Installation - Linux / Mac
======================================

This page provides step-by-step instructions for installing
SteelScript and associated modules in the system-wide site-packages
directory on a Linux or Mac.  This will make SteelScript available to
all users.

Dependencies
------------

* Python version 2.6.x or 2.7.x - see `python.org <http://python.org/download/>`_
* Python `setuptools <https://pypi.python.org/pypi/setuptools>`_

Python
------

You must already have Python installed on your system to continue.
If not, please install Python from `python.org`_
or ask your system adminstrator to install Python.  You will need
either Python 2.6.x or 2.7.x to use the FlyScript SDK.

Check that Python is installed and running the approriate version:

.. code-block:: bash

   $ python -V
   Python 2.7.3

.. _installsys-linuxmac-online:

Online Installation
-------------------

Use this method if the target system has access to the internet.  If
access is limited, see below for :ref:`installsys-linuxmac-offline` instructions.

1. Install the ``pip`` utility via easy_install:

.. code-block:: bash

   $ sudo easy_install pip

   ``pip`` is manages Python package installation and upgrade.

2. (optional) Take a look at `virtualenv <http://www.virtualenv.org/>`_ - a
   tool that provides isolated Python environments.  This allows you
   to install packages without admin privileges.

3. Install `steelscript.common
   <https://github.com/riverbed/steelscript.common/releases>`_:

   .. code-block:: bash

      $ sudo pip install steelscript.common

   .. note::
      Omit ``sudo`` if you are using virtualenv, as admin
      privileges are not required

   This package provides the common functions used by all other
   SteelScript product specific modules.  Additional Python
   dependencies such as Python requests may also be installed
   if it not already present.

4. Install one or more product specific SteelScript modules:

   .. code-block:: bash

      $ sudo pip install steelscript.netprofiler
      $ sudo pip install steelscript.netshark

   See `<http://github.com/riverbed>`_ for a complete list of
   additional SteelScript packages available.

.. _verify-linuxmac:

5. Verify your installation by running a simple test (note, you may
   have to refresh your path with `rehash` if the command is not
   found):

   .. code-block:: bash

      $ steelscript_about.py

      Package 'steelscript' version 0.6.0-2-g4b83 installed

      Path to source:
        /ws/steelscript.netshark/steelscript

      Modules provided:
        steelscript.shark

      Python information:
      Version      : 2.7.3
      Version tuple: ('2', '7', '3')
      Compiler     : GCC 4.2.1 Compatible Apple Clang 4.1 ((tags/Apple/clang-421.11.66))
      Build        : ('default', 'Nov 17 2012 19:54:34')
      Architecture : ('64bit', '')

      Platform information:
      Darwin-12.5.0-x86_64-i386-64bit
      system   : Darwin
      node     : mbpro
      release  : 12.5.0
      version  : Darwin Kernel Version 12.5.0: Sun Sep 29 13:33:47 PDT 2013; root:xnu-2050.48.12~1/RELEASE_X86_64
      machine  : x86_64
      processor: i386

.. _installsys-linuxmac-offline:

Manual Installation via pip
---------------------------

Use this method to install SteelScript when the target system:

* does *not* have direct access to the internet
* does have the ``pip`` command available

Using ``pip`` is the preferred approach, as it will make upgrade
easier down the road.

Essentially you must transfer the necessary packages and dependencies
to the target system manually and then install each package
separately.

.. _upload-packages:

1. Upload the following packages to the target system:

   Required:

   * `requests <https://github.com/kennethreitz/requests/archive/v2.2.1.tar.gz>`_
   * `steelscript.common <https://github.com/riverbed/steelscript.common/releases>`_

   Optional product specific packages:

   * `steelscript.netprofiler <https://github.com/riverbed/steelscript.netprofiler/releases>`_
   * `steelscript.netshark <https://github.com/riverbed/steelscript.netshark/releases>`_

2. Use ``pip`` to install each tarball:

   .. code-block:: bash

      $ sudo pip install requests-0.2.1.tar.gz
      $ sudo pip install steelscript.common-0.7.tar.gz

   Repeat for each product specific steelscript package as well.

   .. note::
      Omit ``sudo`` if you are using virtualenv, as admin
      privileges are not required

3. :ref:`Verify <verify-linuxmac>` your installation with ``steelscript_about.py``

Manual Installation without pip
-------------------------------

Use this method to install SteelScript when the target system:

* does *not* have direct access to the internet
* does *not* have the ``pip`` command available

1. Upload the packages to the target system as described in above in
   :ref:`Step 1 <upload-packages>`.

2. Create a suitable working directory and extract all packages:

   .. code-block:: bash

      $ mkdir /steelscript
      $ tar xvzf requsts-0.2.1.tar.gz
      $ tar xvzf steelscript.common-0.7.tar.gz

   Extract all packages that were downloaded, including the product
   specific packages.

3. Next, install each package in order:

   .. code-block:: bash

      $ cd /steelscript/requests-0.2.1
      $ python setup.py install

      $ cd /steelscript/steelscript.common-0.7
      $ python setup.py install

   Repeat for each package extracted.

4. :ref:`Verify <verify-linuxmac>` your installation with ``steelscript_about.py``

Upgrade
-------

If you need to upgrade SteelScript package to a newer version, and you are
offline, simply repeat the above installation steps.  This will install the
latest version alongside the older version.  Normally you do not need to delete
the older version.

With internet access, any package can be updated with ``pip install -U <package>``
as follows:

.. code-block:: bash

    $ pip install -U steelscript.common

The ``-U`` stands for upgrade -- this will check for a more recent version
of the named package, and if available, it will download it and update.
