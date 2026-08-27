Changelog
=========

This changelog only notes major changes, to notify other developers.

2026-08-26
----------

-  feat: Determine compiled release-level and dataset-level checks' paths based on the release schema, using the new :mod:`pelican.util.schema` module. :issue:`12`
-  fix: ``coherent.value_realistic`` and ``distribution.value_currency`` now check the ``tender``, ``awards`` and ``contracts`` ``items.unit.value`` objects, which were omitted. Bump ``coherent.value_realistic``'s ``version`` to 2.0. :issue:`12`

2026-08-25
----------

-  feat: Add :doc:`restart-time-based-check<tasks/troubleshoot>` command.
-  feat: ``misc.url_availability`` samples unique URL values, so that a repeated URL neither dominates the sample nor is requested twice, and skips if fewer than 100 unique URL values are present. :issue:`6`
-  fix: ``misc.url_availability`` closes the streaming responses to release the HTTP connections.
-  fix: When a message is redelivered, the :ref:`check-data-item` worker skips any item whose checks are committed, to not insert duplicate results. :issue:`173`
-  fix: The :ref:`check-dataset` worker no longer keeps a transaction open while performing checks. :issue:`6`
-  feat: The :ref:`check-dataset` worker processes ``DATASET_PREFETCH_COUNT`` messages at once (2, by default), so that one slow dataset doesn't delay other datasets. The worker claims the dataset atomically before performing checks, using the new :func:`pelican.util.services.claim_dataset_phase` function, so that concurrent messages for the same dataset don't repeat work. :issue:`173`
-  fix: The :ref:`check-time-based` worker claims the dataset atomically before performing checks, so that a redelivered message doesn't insert duplicate results. :issue:`173`
-  fix: Workers no longer set the ``x-consumer-timeout`` queue argument, which RabbitMQ 4.3 rejects for classic queues, since only quorum queues support delivery acknowledgement timeouts. Set ``consumer_timeout = 10800000`` (3 hours) in ``rabbitmq.conf``, if using an older version of RabbitMQ.
-  refactor: Rename the ``PREFETCH_COUNT`` setting to ``DATA_ITEM_PREFETCH_COUNT``, to distinguish it from ``DATASET_PREFETCH_COUNT``.

2026-08-17
----------

-  feat: ``date_time`` now fails on future dates for fields expecting past dates (``date``, ``dateMet``, ``dateModified``, ``datePublished``, ``dateSigned``). Bump its ``version`` to 2.0. :issue:`135`
-  feat: Add ``PREFETCH_COUNT`` setting, to limit the :ref:`check-data-item` worker's threads and database connections.
-  feat: Add :func:`pelican.util.getter.get_organization_identifier` function.
-  fix: ``distribution.buyer`` and ``distribution.buyer_repetition`` now identify buyers by ``buyer.id``, instead of ``buyer.identifier.scheme`` and ``buyer.identifier.id`` (deprecated in OCDS 1.1). Bump their ``version`` to 2.0. :issue:`169`
-  refactor: Rename the ``total_buyer_count`` key to a generic ``total_unique_count`` in the ``meta`` of the ``distribution.buyer`` check.
-  fix: Read the ``documentType``, ``language`` and ``mediaType`` codelists from files instead of GitHub. Retrieve the org-id.guide and OCID prefix codelists once per worker process, instead of once per thread, and retry on connection/server errors and read/request timeouts, in addition to rate limiting. :issue:`48`
-  fix: Workers open one database connection per thread, instead of sharing one connection across threads. :issue:`88`

   -  refactor: Add :func:`pelican.util.services.get_connection`, :func:`~pelican.util.services.execute` and :func:`~pelican.util.services.executemany`.

-  fix: Workers reload exchange rates from the database daily, instead of only at start-up. :issue:`60`

   -  refactor: Replace the ``bootstrap`` and ``import_data`` functions and the global ``rates``, ``bounds`` and ``currencies`` variables in ``pelican.util.currency_converter`` with the :class:`~pelican.util.currency_converter.ExchangeRates` class and :func:`~pelican.util.currency_converter.get_exchange_rates` function.

2023-01-20
----------

-  feat: ``coherent.dates`` checks ``contracts.implementation.transactions.date <= date``.
-  feat: Add ``EXTRACTOR_PAGE_SIZE`` setting.
-  feat: Remove contract value histogram and release date timeline from dataset-level reporting.
-  fix: ``consistent.tender_value`` now skips if the ``value`` is non-numeric. :issue:`62`
-  fix: ``reference.contract_in_awards`` now fails if ``awards`` is not set (was skipping). :issue:`9`
-  fix: Cast values as numbers where appropriate. :issue:`75`
-  fix: Use type casting for reference lookups in non-reference checks, to not shadow non-reference issues. :issue:`50`
-  fix: Do not skip a check if a value is blank – only if it is not set.
-  fix: ``application_count`` and ``pass_count`` are ``None`` if not positive.
-  fix: :func:`~pelican.util.getter.deep_get`: Return ``None`` if attempting to cast ``None``.
-  fix: :func:`~pelican.util.getter.get_values`: If ``item`` is ``None``, return ``[]``.
-  refactor: Improve clarity of ``reason`` messages and ``meta`` keys. :issue:`76`

2021-12-02
----------

-  feat: Add ``PELICAN_BACKEND_STEPS`` :class:`setting<pelican.util.settings.Steps`.
-  feat: Add :doc:`restart-dataset-check<tasks/troubleshoot>` command.
-  fix: ``consistent.period_duration_in_days`` now casts durations as numbers. :issue:`26`
-  fix: :func:`~pelican.util.getter.parse_date`, :func:`~pelican.util.getter.parse_datetime`: Parse truncated date/time formats.
-  fix: :func:`~pelican.util.getter.get_values`: Return leaf nodes only.

2021-11-19
----------

-  fix: ``sys.exit()`` in a consumer callback exits the thread, not the process. Because the message isn't acknowledged and ``prefetch_count=1``, RabbitMQ stops delivering messages and the process hangs indefinitely.
-  refactor: Use `yapw <https://yapw.readthedocs.io/en/latest/>`__ for better error handling and signal handling with RabbitMQ.

2021-10-29
----------

-  feat: Determine field-level checks based on release schema. :issue:`12`
-  fix: ``coherent.tender_status`` now fails on non-zero length arrays (was passing if all entries were blank). :commit:`3444ed6`
-  fix: ``coherent.awards_status`` now skips if the ``id`` isn't set (was failing). :commit:`79549e8`
-  fix: ``coherent.awards_status`` now fails if the ``id`` matches an ``awardID`` of ``None`` and values are inconsistent (was passing). :commit:`79549e8`
-  fix: Add missing field-level checks: ``language``, ``contracts.implementation.transactions.amount.amount``, ``contracts.implementation.transactions.amount.currency``. :commit:`2f0fd89`
-  fix: Remove extra field-level checks: ``contracts.implementation``, ``contracts.implementation.transactions.currency``. :commit:`2f0fd89`
-  refactor: Reduce code duplication in field-level checks. :compare:`2df8f95..7ef148f`

2021-10-28
----------

-  fix: Refresh and expire external codelists appropriately. :issue:`31` :issue:`33`
-  fix: ``coherent.milestone_status`` now works (was always skipping).
-  fix: ``coherent.value_realistic`` now uses ``planning.budget.amount`` (was ``planning.budget.value``).
-  fix: ``distribution.value_currency`` now uses ``planning.budget.amount.currency`` (was ``planning.budget.value.currency``).
-  refactor: Re-do the CLI interface. :commit:`ef8a9bf` :commit:`75a3859` :commit:`160aaa8`

2021-10-26
----------

-  feat: ``date_time`` now fails on dates before 1990. :issue:`34`
-  refactor: Re-organize the repository. :compare:`75a3859..7dbecc9` :commit:`9241df5` :commit:`bc4f77d` :commit:`1f5f744` :commit:`160aaa8` :commit:`ae0447d`

2021-10-25
----------

-  fix: ``consistent.parties_role`` now adds ``"reason"`` to ``result["meta"]`` (was added to ``result``).
-  refactor: :commit:`Rewrite how the application is configured<b5de512>`.
-  refactor: Remove search paths and ``COPY`` command from SQL files. See :doc:`tasks/database`.
