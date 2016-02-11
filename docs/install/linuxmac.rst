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

You must already have Python and the setuptools package installed on your
system to continue.  If not, please install Python from `python.org`_ or ask
your system administrator to install it for you.

You can check that Python is installed and running the appropriate version:

.. code-block:: bash

   $ python -V
   Python 2.7.3

.. _installsys-linuxmac-online:

Online Installation - Virtualenv
--------------------------------

This is the recommended approach when your target system has access to the
internet.  If access is limited, see below for
:ref:`installsys-linuxmac-offline` instructions.

These steps will install steelscript inside an isolated python environment
called a ``virtualenv``.  The great thing about virtualenv's are how they can
allow you to experiment and upgrade packages without worrying about overwriting
any system requirements, and you can create as many as you'd like in order to
separate different projects from one another.

1.  Install Virtualenv using one of the following methods::

       $ sudo easy_install virtualenv


    On a Ubuntu or Debian flavor of Linux, you can use your package manager::

       $ sudo apt-get install python-virtualenv


    For Red Hat or CentOS flavors::

       $ sudo yum install python-virtualenv

.. _installsys-linuxmac-mkvirtualenv:

2. Now create a fresh virtualenv to install the packages into.  Let's create a
   working folder to hold all of your steelscript projects inside too, we will
   create this folder in your home directory::

       $ cd ~
       $ mkdir steelscript
       $ cd steelscript
       $ virtualenv venv
       New python executable in venv/bin/python
       Installing setuptools, pip...done.


3. Whenever you want to work on a steelscript project, you will need
   to run the following command to activate this virtualenv in your
   shell session::

       $ . ~/steelscript/venv/bin/activate
       (venv)$

   .. note::
      Note how your prompt changes to include the name of the virtual environment.
      You can also confirm you are working within the new environment
      by checking which python executable is in your path::

          (venv)$ which python
          ~/steelscript/venv/bin/python


4. Since virtualenv comes with a built-in pip installer, we can easily
   install the base steelscript package ``steelscript``::

       (venv)$ pip install steelscript

   This package provides the common functions used by all other
   SteelScript product specific modules.  Additional Python
   dependencies such as Python requests will also be installed too.


5. Included in this package was a new script called :doc:`steel </steel>` which can
   install the rest of our core packages::

      $ steel install
      Checking if pip is installed...done
      Package steelscript already installed
      Installing steelscript.netprofiler...done
      Installing steelscript.netshark...done
      Installing steelscript.wireshark...done

   See `<http://github.com/riverbed>`_ for a complete list of
   additional SteelScript packages available.

.. _verify-linuxmac:

5. Verify your installation by running a simple test::

      $ steel about

      Installed SteelScript Packages
      Core packages:
        steelscript                               1.0
        steelscript.netprofiler                   1.0
        steelscript.netshark                      1.0
        steelscript.wireshark                     1.0

      Application Framework packages:
        None

      REST tools and libraries:
        None

      Paths to source:
        ~/steelscript/venv/lib/python2.7/site-packages

      (add -v or --verbose for further information)

6. Make a workspace to copy over the included example scripts and create
   a sandbox to work around with::

      $ steel mkworkspace

7. Take a look at your new files and start developing!


.. _installsys-linuxmac-offline:

Offline Installation via pip
----------------------------

Use this method to install SteelScript when the target system:

* does *not* have direct access to the internet
* does have the ``pip`` command available

The ``pip`` package tool has a helpful utility to download packages
and their dependencies instead of directly installing them.

.. _upload-packages:

1. Make an archive directory::

       $ mkdir steelscript_packages

2. Create a local archive of the core steelscript package and its
   dependencies::

       $ pip install -d steelscript_packages steelscript

   Inside the folder ``steelscript_packages`` you should see
   archives for ``steelscript``, ``requests``, and ``importlib``.

3. Add any additional steelscript packages of interest.  The following
   will download both the netprofiler and netshark packages to the
   same archive directory along with ``virtualenv``::

       $ pip install --no-use-wheel -d steelscript_packages steelscript.netprofiler
       $ pip install --no-use-wheel -d steelscript_packages steelscript.netshark
       $ pip install --no-use-wheel -d steelscript_packages virtualenv

   .. note::
       The ``--no-use-wheel`` option makes sure the packages can be installed
       on a barebones system that may not have ``pip`` available.

4. Add any other packages of interest you may need using the same approach
   above with a ``pip install`` and the ``-d`` option.

5. Tar up the packages directory::

       $ tar cvzf steelscript_packages.tar.gz steelscript_packages

6. Transfer it to your target system using whatever approach you choose
   (scp, usb key, share drive, floppy ...).

.. _installsys-linuxmac-manual-venv:

7. (Optional) Depending on your system requirements, you can create a
   virtualenv in this system as well and install the packages into that, as
   :ref:`described above <installsys-linuxmac-mkvirtualenv>`.  Start off by
   getting the package installed onto the system::

      $ sudo pip install --no-index -f steelscript_packages virtualenv

   If ``pip`` is not available on the target system, then install the
   package manually::

      $ pip install steelscript_packages/virtualenv*

   From here you can setup a working directory, create your virtualenv,
   and activate it for the remaining steps (just omit ``sudo`` from the
   rest of the commands!)

8. Use ``pip`` to install the base steelscript package, telling it
   to use ``steelscript_packages`` as the place to find relevant files::

      $ sudo pip install --no-index -f steelscript_packages steelscript

   Repeat that command replacing the last ``steelscript`` name with the
   name of any extra packages you want included.  Don't worry about
   steelscript packages, those can be installed with the following::

      $ sudo steel install --pip-options="--no-index -f pkgs"

   .. note::
      Omit ``sudo`` if you are using virtualenv, as admin
      privileges are not required

9. :ref:`Verify your installation <verify-linuxmac>` with ``steel about``

Manual Installation without pip
-------------------------------

Use this method to install SteelScript when the target system:

* does *not* have direct access to the internet
* does *not* have the ``pip`` command available

Follow the instructions from :ref:`installsys-linuxmac-offline`, to create
the archive directory and transfer it over to the system.  Creating a virtualenv
is still optional, but recommended.

In case you would prefer to install system wide, then extract the steelscript_packages.tar.gz file, and manually install each package one by one::

    $ tar xvzf steelscript_packages.tar.gz
    $ cd steelscript_packages


Repeat the following steps for each the following packages, in order:

1. importlib
2. requests
3. steelscript
4. steelscript.netprofiler
5. steelscript.netshark

Replace ``<packagename>`` below with the filename from the tarball::

    $ tar xvzf <packagename>.tar.gz
    $ cd <packagename>
    $ python setup.py install


:ref:`Verify your installation <verify-linuxmac>` with ``steel about``


Upgrading SteelScript
---------------------

If you'd like to upgrade SteelScript package to a newer released version, and
you are offline, simply repeat the above installation steps.  This will install
the latest version alongside the older version.  Normally you do not need to
delete the older version.

In other cases, you can simply use the built in :doc:`steel </steel>` to
update the packages for you::

    $ steel install --upgrade

This will check for a more recent version of all the installed SteelScript
packages and install newer versions if available.
