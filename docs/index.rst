Pelican backend
===============

.. include:: ../README.rst

.. warning::

   The content from the `GitHub wiki <https://github.com/open-contracting/pelican-backend/wiki>`__ has not yet been migrated. (:issue:`3`)

Word choice
-----------

To avoid ambiguity:

- "collection" refers to the collection in Kingfisher Process, and "dataset" refers to the extracted collection in Pelican backend.
- "compiled release" refers to the ``data`` value of the compiled release in Kingfisher Process, and "item" refers to its corresponding row in the ``data_item`` table in Pelican backend.

In the code and database, "resource" is used for "compiled release" (or "item"), and "time variance" is used for "time-based". In the documentation, we use the latter words to be consistent with the user interface and with other tools.

We use "extract" instead of "import", like in the Extract-Transform-Load pattern.

.. toctree::
   :caption: Contents
   :maxdepth: 2

   tasks/index
   reference/index
   contributing/index
   changelog
