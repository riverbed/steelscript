SteelScript Installation - Windows
==================================

This page provides step-by-step instructions for installing
SteelScript and associated modules on Windows.

Dependencies
------------

* Python version 2.6.x or 2.7.x - see `python.org <http://python.org/download/>`_
* Python `setuptools <https://pypi.python.org/pypi/setuptools>`_

.. _installsys-windows:

Online Installation
-------------------

If your machine has access to the internet, then follow these steps.
It is usually easiest to install as administrator:

1. If you don't yet have Python installed on your system, download
   Python from `python.org`_.  Be sure to pick the
   installer from the Python 2 section (2.7.11 at the time this
   document is written) since SteelScript does not currently support
   Python 3.  Download the installer for your platform (32bit
   vs. 64bit).

2. Double-click the Python installer and follow the instructions.

   * Installing for all users is usually a good choice unless there are
     permissions issues with your machine.
   * Choose the default folder for installation
   * On the Customize Python screen, make sure "pip" and the "Add python.exe to
     Path" are set to install.

3. Open command-line window (Start -> Search -> cmd.exe)

4. Use pip to install the SteelScript package::

      > pip.exe install steelscript

5. Install one or more product specific SteelScript packages::

      > pip.exe install steelscript.netprofiler
      > pip.exe install steelscript.netshark
      > pip.exe install steelscript.wireshark

.. _verify-windows:

6. At this point, you should be able to run the examples included in
   the SteelScript packages.  Run the ``steel about`` script as a
   simple test::

      C:\Python27\Scripts>steel about

      Installed SteelScript Packages
      Core packages:
        steelscript                               1.0.1
        steelscript.netprofiler                   1.0.2
        steelscript.netshark                      1.0
        steelscript.wireshark                     1.0.1

      Application Framework packages:
        None

      REST tools and libraries:
        None

      Paths to source:
        C:\Python27\lib\site-packages

      (add -v or --verbose for further information)

7. Make a workspace to copy over the included example scripts and create
   a sandbox to work around with::

      > steel mkworkspace

8. Take a look at your new files and start developing!


Offline Installation
--------------------

For offline installation, you will still need to have Python installed
on your Windows machine as described in steps 1 and 2 above.  You will
also need a machine that has internet access in order to collect the
SteelScript packages and their dependencies as described below:

1. From a machine which has internet access and Python installed as described
   above, create a new temporary directoy and collect the packages with the
   following commands from a cmd.exe prompt::

   > mkdir steelscript-packages
   > cd steelscript-packages
   > pip install --download . --no-use-wheel steelscript
   > pip install --download . --no-use-wheel steelscript.netprofiler
   > pip install --download . --no-use-wheel steelscript.netshark
   > pip install --download . --no-use-wheel steelscript.wireshark

2. Zip up this directory and transfer the zip file to your offline machine.

3. On the offline machine, unzip the file to some location.

4. Open a cmd.exe shell, cd into this unzipped directory, and install the
   packages::

   > cd steelscript-packages
   > pip install --no-index --find-links . steelscript
   > pip install --no-index --find-links . steelscript.netprofiler
   > pip install --no-index --find-links . steelscript.netshark
   > pip install --no-index --find-links . steelscript.wireshark

5. :ref:`Verify <verify-windows>` your installation with ``steel.py about``

Upgrade
-------

If you need to upgrade SteelScript package to a newer version, and you are
offline, simply repeat the above installation steps.  This will install the
latest version alongside the older version.  Normally you do not need to delete
the older version.

With internet access, any package can be updated with ``pip install -U <package>``
as follows::

    > pip.exe install -U steelscript

The ``-U`` stands for upgrade -- this will check for a more recent version
of the named package, and if available, it will download it and update.
