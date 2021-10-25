Time-based
==========

Backend
-------

#. Find a check under the ``time_variance`` directory to copy as a starting point.
#. Add the check to the ``time_variance/definitions.py`` file. For example:

   .. literalinclude:: ../../../time_variance/definitions.py
      :language: python
      :start-after: definitions
      :end-at: phase_stable

Each check is an object (usually a module) that has two attributes: ``filter`` and ``evaluate``.

Pairs of items with the same ocid are read in batches from the dataset and its ancestor. Each item is passed to the ``filter`` function, which:

#. Accepts five arguments: an accumulator, an ancestor's item and its ID, and a dataset's item and its ID
#. Returns whether the check can be calculated against the pair of items (for example, if both are present)

If ``filter`` returns ``True``, the ``evaluate`` function:

#. Accepts five arguments, like ``filter``
#. Determines whether the check passes
#. Returns the accumulator, and whether the check passes

The accumulator is initialized as:

.. literalinclude:: ../../../tools/checks.py
   :language: python
   :start-after: get_empty_result_time_variance_scope
   :end-at: }

``time_variance/processor.py`` then prepares the ``result`` dict. An empty ``result`` dict looks like:

.. literalinclude:: ../../../tools/checks.py
   :language: python
   :start-after: get_empty_result_time_variance
   :end-at: }

Storage
~~~~~~~

The result of each check for a given dataset is stored in a single row in the ``time_variance_level_check`` table.

Frontend
--------

Pelican frontend automatically supports new time-based checks.
