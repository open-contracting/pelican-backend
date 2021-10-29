Changelog
=========

This changelog only notes major changes, to notify other developers.

2021-10-28
----------

-  fix: Refresh and expire external codelists appropriately. :issue:`31` :issue:`33`
-  fix: ``coherent.milestone_status`` now works (was always N/A).
-  fix: ``coherent/value_realistic`` now uses ``planning.budget.amount`` (was ``planning.budget.value``).
-  fix: ``distribution.value_currency`` now uses ``planning.budget.amount.currency`` (was ``planning.budget.value.currency``).
-  refactor: Re-do the CLI interface. :commit:`ef8a9bf` :commit:`75a3859` :commit:`160aaa8`

2021-10-26
----------

-  feat: ``date_time`` now fails on dates before 1990. :issue:`34`
-  refactor: Re-organize the repository. :compare:`75a3859..7dbecc9` :commit:`9241df5` :commit:`bc4f77d` :commit:`1f5f744` :commit:`160aaa8`

2021-10-25
----------

-  fix: ``consistent.parties_role`` now adds ``"reason"`` to ``result["meta"]`` (was added to ``result``).
-  refactor: :commit:`Rewrite how the application is configured<b5de512>`.
-  refactor: Remove search paths and ``COPY`` command from SQL files. See :doc:`tasks/database`.
