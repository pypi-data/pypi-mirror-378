Installation
============

Requirements
------------

* Python 3.8 or higher
* Redis server (optional, for caching and history)

Install from PyPI
-----------------

.. code-block:: bash

   pip install vesper-reqflow

Install from Source
-------------------

.. code-block:: bash

   git clone https://github.com/VesperAkshay/ReqFlow.git
   cd ReqFlow
   pip install -e .[dev]

Docker Installation
-------------------

.. code-block:: bash

   docker run -it apitester/cli:latest

Development Installation
------------------------

For development with all dependencies:

.. code-block:: bash

   pip install vesper-reqflow[dev,ai]
