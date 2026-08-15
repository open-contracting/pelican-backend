Set up the database
===================

To use the default settings, create a ``pelican_backend`` database and use its ``public`` schema.

To use another schema, you can set the ``PGOPTIONS`` environment variable when running ``psql`` commands, for example:

.. code-block:: bash

   env PGOPTIONS=--search_path=development psql DATABASE -f FILE

Create the btree_gin extension:

.. code-block:: bash

   psql pelican_backend -c "CREATE EXTENSION btree_gin";

Run migrations
--------------

Run the files in the ``pelican/migrations/`` directory in numerical order. For example:

.. code-block:: bash

   psql -v ON_ERROR_STOP=1 pelican_backend $(printf -- '-f %s ' pelican/migrations/*.sql)

To update an existing database, run only the files that it hasn't run yet.

Change the schema
-----------------

.. admonition:: One-time setup

   Install `pg-diff <https://michaelsogos.github.io/pg-diff/>`__:

   .. code-block:: bash

      npm install -g pg-diff-cli

#. Ensure the ``pelican_backend`` database is fully migrated.
#. Create the ``pelican_backend_dev`` database, and run all migrations:

   .. code-block:: bash

      dropdb --if-exists pelican_backend_dev
      createdb pelican_backend_dev
      psql pelican_backend_dev -c "CREATE EXTENSION btree_gin"
      psql -v ON_ERROR_STOP=1 pelican_backend_dev $(printf -- '-f %s ' pelican/migrations/*.sql)

#. Make changes to the ``pelican_backend_dev`` database, using ``psql``.
#. Write the patch, replacing ``NAME`` with a short name, like ``not_null``:

   .. code-block:: bash

      pg-diff -c development NAME

   pg-diff compares the ``pelican_backend_dev`` database to the ``pelican_backend`` database, as configured by the ``pg-diff-config.json`` file, and writes a SQL file to ``pelican/migrations/``.

   .. attention::

      pg-diff writes no ``DROP`` statements for tables, views, functions and aggregates that are missing from the ``pelican_backend_dev`` database. Write those yourself.

#. Edit the file, keeping only the relevant statements. Depending on the change, pg-diff writes:

   -  ``"public".`` schema qualifiers. Remove them. Otherwise, the statements fail in a database that uses another schema.
   -  ``ALTER TABLE IF EXISTS``. Replace it with ``ALTER TABLE ONLY``. Otherwise, if the table is missing, the statement is skipped, without error.
   -  ``OWNER TO`` statements, which name the owner in your local database. Remove them.
   -  ``DROP INDEX`` and ``CREATE INDEX`` statements that recreate an unchanged index, if a column's definition changed. Remove them.

   .. tip::

      For a new table, write the statements yourself, following the ``001_base.sql`` file. Instead of a ``bigserial`` column, pg-diff writes a ``CREATE SEQUENCE`` statement, whose sequence isn't owned by the column, and is therefore left behind if the table is dropped.

#. Run the migration, and check that no differences remain. For example:

   .. code-block:: bash

      psql -v ON_ERROR_STOP=1 pelican_backend -f pelican/migrations/20260814182412168_NAME.sql
      pg-diff -c development check

   The second command should report:

   .. code-block:: none

      No patch has been created because no differences have been found!

Load exchange rates
-------------------

Populating exchange rates from scratch will take a long time and use a lot of fixer.io's quota.

Instead, load a file:

.. code-block:: sql

   psql pelican_backend -c "\copy exchange_rates (valid_on, rates) from 'pelican/static/exchange_rates_dump.csv' delimiter ',' csv header;"

.. note::

   The :ref:`extract-kingfisher-process` worker fetches missing exchange rates when it receives a message. To avoid duplication across processes and/or threads, you can run the :ref:`manage-update-exchange-rates` command periodically.

Dump exchange rates
-------------------

.. code-block:: sql

   psql pelican_backend -c "\copy exchange_rates to '/path/to/exchange_rates_dump.csv' csv header;"

Reset the database
------------------

Truncate all tables in the database. For example:

.. code-block:: bash

   psql pelican_backend -f pelican/static/truncate.sql
