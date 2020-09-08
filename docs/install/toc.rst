SteelScript Installation
========================

SteelScript is provided as open source on GitHub (https://github.com/riverbed).
Installation of SteelScript varies depending on the platform you are using.
Start with the specific instructions for :doc:`Docker <docker>`, 
:doc:`Linux or Mac OS <linuxmac>` or :doc:`Windows <windows>` for greater detail.

Installing SteelScript SteelHead package requires executing the command ``steel install --steelhead``.
But it might take a few more steps, see :doc:`SteelHead Installation Instructions <steelhead>` for more details.  

Python Compatibility Note
-------------------------

SteelScript requires Python 3, starting with version 2.0 libraries. The 1.8.x series
of SteelScript packages are the last to support Python 2.x. The steelscript-netshark library
was not upgraded beyond 1.8.x, as the NetShark product is now end-of-availability and
end-of-support and existing users are recommended to transition to AppResponse.

GitHub master branches are now Python 3 only. Older versions compatible with Python 2 can
still be downloaded from the Python Package Index (PyPI) by specifying a version lower than 2.0,
like so:
"pip install steelscript<2.0"

The SteelScript App Framework is not support beyond Python 2.

.. toctree::

   docker
   linuxmac
   windows
   steelhead
