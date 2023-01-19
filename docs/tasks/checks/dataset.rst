Dataset-level
=============

Backend
-------

#. Determine the type of check (see :ref:`repository-structure`).
#. Find a check under the corresponding ``dataset`` sub-directory to copy as a starting point.
#. Add the check to the ``dataset/definitions.py`` file. For example:

   .. literalinclude:: ../../../dataset/definitions.py
      :language: python
      :start-at: distribution.main_procurement_category
      :end-at: unique.tender_id

Each check is an object (usually a module) that has two attributes: ``add_item`` and ``get_result``.

Items are read in batches. Each item is passed to the ``add_item`` function, which:

#. Accepts three arguments: an accumulator (a dict), the item, and the item's ID
#. Determines whether the check can be calculated against the item
#. If not, returns the unchanged accumulator
#. Updates the accumulator
#. Returns the updated accumulator

Once all items are read, the ``get_result`` function:

#. Accepts the accumulator
#. Creates an empty ``result`` dict
#. Determines whether the check can be calculated against the accumulator
#. If not, sets ``result["meta"] = {"reason": "..."}`` and returns the ``result`` dict
#. Determines whether the check passes

   .. note::

      Some ID fields allow both integer and string values. When resolving references by comparing IDs, the check should fail if the IDs are different types. It should neither succeed nor N/A (it is likely to N/A if IDs are not coerced to string).

#. Sets these keys on the ``result`` object:

   ``result`` (boolean)
     Whether the check passes
   ``value`` (float)
     A number from 0 to 100
   ``meta``
     Any additional data to help interpret the result, like examples

#. Returns the ``result`` dict

An empty ``result`` dict looks like:

.. literalinclude:: ../../../pelican/util/checks.py
   :language: python
   :start-after: get_empty_result_dataset
   :end-at: }

Storage
~~~~~~~

The result of each check for a given dataset is stored in a single row in the ``dataset_level_check`` table.

Frontend
--------

#. Update ``frontend/src/components/DatasetLevelSection.vue`` and register the check.
#. Register the check in ``frontend/src/plugins/datasetMixins.js``.

