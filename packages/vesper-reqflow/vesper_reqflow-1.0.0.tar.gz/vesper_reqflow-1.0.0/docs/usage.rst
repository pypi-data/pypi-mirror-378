Usage
=====

Basic Commands
--------------

Check status:

.. code-block:: bash

   apitester status

Send a GET request:

.. code-block:: bash

   apitester request send GET https://httpbin.org/get

Send a POST request with JSON body:

.. code-block:: bash

   apitester request send POST https://httpbin.org/post --body '{"key": "value"}'

Template Management
-------------------

Save a request template:

.. code-block:: bash

   apitester template save my-template GET https://api.example.com/users

List templates:

.. code-block:: bash

   apitester template list

Execute a template:

.. code-block:: bash

   apitester template execute my-template

Environment Management
----------------------

Set environment variables:

.. code-block:: bash

   apitester env set API_KEY "your-api-key"
   apitester env set BASE_URL "https://api.example.com"

List environment variables:

.. code-block:: bash

   apitester env list

History
-------

View request history:

.. code-block:: bash

   apitester history list
