Changelog
=========

This changelog only notes major changes, to notify other developers.

2023-01-19
----------

-  feat: ``coherent.dates`` checks ``contracts.implementation.transactions.date <= date``.
-  feat: Add ``EXTRACTOR_PAGE_SIZE`` setting.
-  fix: ``consistent.tender_value`` now skips if the ``value`` is non-numeric. :issue:`62`
-  fix: Cast values as numbers where appropriate. :issue:`75`

   -  ``coherent.procurement_method_vs_number_of_tenderers``: ``tender.numberOfTenderers``

-  fix: Use type casting for reference lookups in non-reference checks, to not shadow non-reference issues. :issue:`50`
-  fix: Do not skip a check if a value is blank – only if it is not set.
-  fix: ``application_count`` and ``pass_count`` are ``None`` if not positive.
-  fix: :func:`~tools.getter.get_values`: If ``item`` is ``None``, return ``[]``.
-  refactor: Improve clarity of ``reason`` messages and ``meta`` keys. :issue:`76`

2021-12-02
----------

-  feat: Add ``PELICAN_BACKEND_STEPS`` :class:`setting<tools.settings.Steps`.
-  feat: Add :doc:`restart-dataset-check<tasks/troubleshoot>` command.
-  fix: ``consistent.period_duration_in_days`` now casts durations as numbers. :issue:`26`
-  fix: :func:`~tools.getter.parse_date`, :func:`~tools.getter.parse_datetime`: Parse truncated date/time formats.
-  fix: :func:`~tools.getter.get_values`: Return leaf nodes only.

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
