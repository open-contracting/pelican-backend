Set up the database
===================

To use the default settings, create a ``pelican_backend`` database and use its ``public`` schema.

To use another schema, you can set the ``PGOPTIONS`` environment variable when running ``psql`` commands, for example:

.. code-block:: bash

   env PGOPTIONS=--search_path=development psql DATABASE -f FILE

Run migrations
--------------

Run the files in the ``pelican/migrations/`` directory in numerical order. For example:

.. code-block:: bash

   psql pelican_backend -f pelican/migrations/*.sql

..
   Bash filename expansion is alphabetically sorted.
   https://www.gnu.org/software/bash/manual/bash.html#Filename-Expansion

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

   psql pelican_backend -f pelican/migrations/truncate.sql
