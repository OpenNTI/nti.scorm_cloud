=================
 nti.scorm_cloud
=================

.. image:: https://travis-ci.org/NextThought/nti.scorm_cloud.svg?branch=master
    :target: https://travis-ci.org/NextThought/nti.scorm_cloud

.. image:: https://coveralls.io/repos/github/NextThought/nti.scorm_cloud/badge.svg?branch=master
    :target: https://coveralls.io/github/NextThought/nti.scorm_cloud?branch=master


The SCORM Cloud Client Library for Python is a Python module used to integrate the SCORM Cloud web services API into a Python application. Currently, the library does not cover all possible SCORM Cloud web services API calls, but it does cover the most important basics. You can find out more about the SCORM Cloud web services API and the available services and calls by reading the [online documentation](http://cloud.scorm.com/doc/web-services/api.html).

To use the library, simply drop the *client.py* file into your project and import the classes as appropriate. You might also consider adding this repository as a Git submodule, allowing you to easily stay up-to-date. If you path your submodule as scormcloud, you can add imports more clearly:

    from nti.scorm_cloud.client import ...

If you'd like to see the library in action, we have a [sample application](https://github.com/RusticiSoftware/SCORMCloud_PythonDemoApp) which demonstrates the basic functionality.

Version Notice
This is the active development branch for version 2 of the library. It is *incompatible* with [version 1](https://github.com/RusticiSoftware/SCORMCloud_PythonLibrary/tree/1.x), which is still available. If you have existing code using version 1 of the library, be sure to use the library code on the 1.x branch or be aware that you will have to spend some time replacing code that touches the SCORM Cloud library.
