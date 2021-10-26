Changelog
=========

This changelog only notes major changes, to notify other developers.

2021-10-26
----------

-  refactor: Re-organize the repository. :compare:`75a3859..7dbecc9`

2021-10-25
----------

-  refactor: :commit:`Rewrite how the application is configured<b5de512f3e57a09dfbf55e68eb6f12a29ff4ef6d>`.
-  refactor: Remove search paths and ``COPY`` command from SQL files. See :doc:`tasks/database`.
-  fix: ``consistent.parties_role`` now adds ``"reason"`` to ``result["meta"]`` instead of to ``result``.
