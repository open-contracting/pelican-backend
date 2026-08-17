Add checks
==========

.. toctree::
   :maxdepth: 1

   field
   compiled-release
   dataset
   time-based

Once the check's name and description are added to `Pelican frontend <https://github.com/open-contracting/pelican-frontend>`__, update :doc:`../../checks`:

.. code-block:: bash

   ./manage.py dev updatedocs
