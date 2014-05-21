Riverbed SteelScript for Python
===============================

Welcome, this is the documentation for Riverbed SteelScript for Python.
SteelScript is a collection of Python modules that build upon
REST APIs and other interfaces to interact with Riverbed appliances
and software.

Quick Start
-----------

If you already have pip, just run the following (in a
`virtualenv <http://www.virtualenv.org/>`_):

.. code:: bash

   $ pip install steelscript
   $ steel install

Not sure about pip, but you know you have Python?

1. Download :download:`steel_bootstrap.py`

2. Run it (in a `virtualenv <http://www.virtualenv.org/>`_):

   .. code:: bash

      $ python steel_bootstrap.py install

SteelScript Application Framework
---------------------------------

The SteelScript Application Framework makes it easy to create a fully
custom web application that mashes up data from multiple sources.  It comes
pre-configured with several reports for NetProfiler and NetShark.

Once you have the base ``steelscript`` package installed, getting started
is just a few commands away:

.. code:: bash

   $ steel install --appfwk
   $ steel appfwk mkproject

This will populate a local directory with all the files you need to run
the server in "dev" mode on your local system.

For more details, see the :doc:`complete documentation <appfwk/overview>`.

Documentation
-------------

* Installation

  * :doc:`Quick Guide <install/quick>`
  * :doc:`Linux / Mac <install/linuxmac>`
  * :doc:`Windows <install/windows>`

* Tutorials

* Core modules

  * :doc:`common/overview`
  * :doc:`netprofiler/overview`
  * :doc:`netshark/overview`

* :doc:`appfwk/overview`
* :doc:`vmconfig/overview`
* :doc:`toc`


.. _license

License
-------

.. container:: license

   This Riverbed SteelScript for Python documentation is provided "AS
   IS" and without any warranty or indemnification.  In no event shall
   Riverbed be liable for any claim, damages or other liability,
   whether in an action of contract, tort or otherwise, arising from,
   out of or in connection with this documentation.  Without limiting
   the foregoing, Riverbed is not obligated to provide any support for
   any questions or issues arising out of or in connection with your
   use of this documentation or any concepts or technology described
   herein.

   Any sample code or scripts included in the documentation are licensed
   under the following license terms:

.. container:: copyright

   Copyright (c) 2014 Riverbed Technology, Inc.

   Permission is hereby granted, free of charge, to any person obtaining
   a copy of this software and associated documentation files (the
   "Software"), to deal in the Software without restriction, including
   without limitation the rights to use, copy, modify, merge, publish,
   distribute, sublicense, and/or sell copies of the Software, and to
   permit persons to whom the Software is furnished to do so, subject to
   the following conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
   LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
   OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
   WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
