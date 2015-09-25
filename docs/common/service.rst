:py:mod:`steelscript.common.service`
====================================

.. automodule:: steelscript.common.service

:py:class:`Service` Objects
---------------------------

.. autoclass:: Service
   :members:

   .. automethod:: __init__

Authentication
--------------

Most REST resource calls require authentication.  Devices will support one
or more authentication methods.  The following methods may be supported:

* :py:const:`Auth.OAUTH` - OAuth 2.0 based authentication using an access code.  The
  access code is used to retrieve an access token which is used
  in subsequent REST calls.

* :py:const:`Auth.COOKIE` - session based authentication via HTTP Cookies.  The initial
  authentication uses username and password.  On success, an HTTP
  Cookie is set and used for subsequent REST calls.

* :py:const:`Auth.BASIC` - simple username/password based HTTP Basic authentication.

When a Service object is created, the user may either pass an authentication
object to the constructor, or later passed to the :py:meth:`Service.authenticate()`
method.

:py:class:`UserAuth` Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: UserAuth
   :members:

   .. automethod:: __init__

:py:class:`OAuth` Objects
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OAuth
   :members:

   .. automethod:: __init__
