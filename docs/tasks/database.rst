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

To update an existing database, run only the unapplied migrations.

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
#. Write the migration, replacing ``NAME`` with a short name, like ``not_null``:

   .. code-block:: bash

      pg-diff -c development NAME

   pg-diff compares the ``pelican_backend_dev`` database to the ``pelican_backend`` database, as configured by the ``pg-diff-config.json`` file, and writes a SQL file to ``pelican/migrations/``.

   .. attention::

      pg-diff writes no ``DROP`` statements for tables, views, functions and aggregates that were dropped from the ``pelican_backend_dev`` database. Write those manually.

#. Edit the migration, keeping only the relevant statements. Depending on the change, pg-diff writes:

   -  ``"public".`` schema qualifiers. Remove them; otherwise, the statements fail if a deployment uses another schema.
   -  ``DROP INDEX`` and ``CREATE INDEX`` statements for unchanged indexes on altered columns. Remove them; otherwise, unchanged indexes are recreated unnecessarily.
   -  ``OWNER TO`` statements for new objects, naming the owner in your local database. Remove them; otherwise, the statements fail in other databases.
   -  ``IF EXISTS`` and ``IF NOT EXISTS`` clauses. Remove them; otherwise, a statement is silently skipped if the database isn't in the expected state.
   -  ``CREATE SEQUENCE`` statements for new ``bigserial`` columns. Remove them, and replace each column definition, like ``id int8 NOT NULL DEFAULT nextval('table_column_seq'::regclass)``, with ``id bigserial``; otherwise, the sequence isn't owned by the column, and is orphaned if the table is dropped.

   Optionally, remove all SQL comments and ``COMMENT ON`` statements.

#. Run the migration, and check that no differences remain. For example:

   .. code-block:: bash

      psql -v ON_ERROR_STOP=1 pelican_backend -f pelican/migrations/20260814182412168_NAME.sql
      pg-diff -c development check

   The second command should output:

   .. code-block:: none

      No patch has been created because no differences have been found!

.. _load-exchange-rates:

Load exchange rates
-------------------

Populating exchange rates from scratch will take a long time and use a lot of fixer.io's quota.

Instead, load a file:

.. code-block:: sql

   psql pelican_backend -c "\copy exchange_rates (valid_on, rates) from 'pelican/static/exchange_rates_dump.csv' delimiter ',' csv header;"

Then, schedule the :ref:`manage-update-exchange-rates` command to update the rates daily, after 00:05 UTC, `when fixer.io publishes the previous day's rates <https://fixer.io/faq>`__.

.. note::

   If the ``FIXER_IO_API_KEY`` environment variable is set, the :ref:`extract-kingfisher-process` worker also retrieves any missing rates when it receives a message.

Dump exchange rates
-------------------

.. code-block:: sql

   psql pelican_backend -c "\copy exchange_rates to '/path/to/exchange_rates_dump.csv' csv header;"

Reset the database
------------------

Truncate all tables in the database. For example:

.. code-block:: bash

   psql pelican_backend -f pelican/static/truncate.sql
