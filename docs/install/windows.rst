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
   installer from the Python 2 section (2.7.6 at the time this
   document is written) since SteelScript does not currently support
   Python 3.  Download the installer for your platform (32bit
   vs. 64bit).

2. Install Python `setuptools`_ Simplest approach is to download the
   `ez_setup.py <http://peak.telecommunity.com/dist/ez_setup.py>`_
   script, then double-click the file in your downloads directory.
   This should automatically determine the best installation for your
   configuration.

3. Add Python to your System Path:

   * Navigate to the Environment Variables window via Right-click on
     "My Computer"->Properties->Advanced system settings->Environment
     Variables.

   * Add a new item to the "User variables for USERNAME" section in the top part of
     the window with the following properties (assumes Python from Step 1 was
     installed into the default location).  If you already have an item named "Path"
     there, you can just add a semi-colon (";") and append the following text in the
     dialog box::

        Name: Path
        Value: C:\Python27;C:\Python27\Scripts<br>

4. Open command-line window (Start -> Search -> cmd.exe)

5. Change to your Python Scripts directory and install pip::

      > cd C:\Python27\Scripts
      > easy_install.exe pip
      ...

6. Use pip to install steelscript::

      > cd C:\Python27\Scripts
      > pip.exe install steelscript

7. Install one or more product specific SteelScript modules::

      > pip.exe install steelscript.netprofiler
      > pip.exe install steelscript.netshark

.. _verify-windows:

8. At this point, you should be able to run the examples included in
   the SteelScript package.  Run the ``steel about`` script as a
   simple test::

      C:\Python27\Scripts>steel about

      Installed SteelScript Packages
      Core packages:
        steelscript                               0.9.0
        steelscript.netprofiler                   0.9.0
        steelscript.netshark                      0.9.0

      Application Framework packages:
      None.

      Paths to source:
        C:\Python27\lib\site-packages

      (add -v or --verbose for further information)

9. Make a workspace to copy over the included example scripts and create
   a sandbox to work around with::

      > steel mkworkspace

10. Take a look at your new files and start developing!


Offline Installation
--------------------

For offline installation, ensure you have downloaded python,
setuptools, requests, and steelscript ahead of time and follow steps 1
and 2 above.  With python and setuptools installed install steelscript
using the following steps.  As above, it is usually recommended
to run these commands as administrator.

1. Double click on the ``requests`` package to extract the contents.

2. Install the requests package using the system python.  Open a
   command prompt and type the following commands (change the cd command
   to match the directory requests is extracted into)::

      > cd c:\requests-2.1.0
      > C:\Python27\python setup.py install
      ...

3. Double click on the ``steelscript`` package to extract the contents.
   Extract all product specific packages of interest as well.

4. Install the package using the system python.  Open a
   command prompt and type the following commands (change the cd command
   to match the directory FlyScript is extracted into)::

      > cd c:\steelscript-0.9.0
      > C:\Python27\python setup.py install
      ...
      ...
      Installed c:\Python27\site-packages\steelscript-0.9.0-py2.7.egg
      Processing dependencies for steelscript==0.9.0
      Finished processing dependencies for steelscript==0.9.0

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
