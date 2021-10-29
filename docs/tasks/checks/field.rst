Field-level
===========

Backend
-------

#. Determine the type of check (see :ref:`repository-structure`).
#. Find a check under the corresponding ``contracting_process/field_level`` sub-directory to copy as a starting point.
#. Assign the check to fields in the ``contracting_process/field_level/definitions.py`` file. For example:

   .. literalinclude:: ../../../contracting_process/field_level/definitions.py
      :language: python
      :start-at: parties.contactPoint.email
      :end-at: parties.contactPoint.faxNumber

   .. note::

      Coverage checks are performed for all fields listed in ``definitions``.

Each check is a function, named ``calculate`` by convention, that:

#. Accepts two arguments (e.g. ``{"email": "invalid"}`` and ``email``), named ``item`` and ``key`` by convention
#. Creates an empty ``result`` dict
#. Determines whether the check passes
#. If it passes, sets ``result["result"] = True``
#. If it fails, sets ``result["result"] = False`` as well as the ``value`` and ``reason`` keys
#. Returns the ``result`` dict

.. note::

   The ``field_coverage_check`` and ``field_quality_check`` functions handle most of this logic, such that you only need to implement whether the check passes.

An empty ``result`` dict looks like:

.. literalinclude:: ../../../tools/checks.py
   :language: python
   :start-after: _empty_field_result
   :end-at: }

Example
~~~~~~~

.. literalinclude:: ../../../contracting_process/field_level/checks/exists.py
   :language: python

Storage
~~~~~~~

The results for each item are stored in a single row in the ``field_level_check`` table. A stored ``result`` value looks like (only one entry in the ``checks`` array is shown):

.. code-block:: json

   {                                                                                               
       "meta": {                                                                                   
           "ocid": "ocds-lcuori-0rw29R-003-2011-1",                                                
           "item_id": 8477481                                                                      
       },                                                                                          
       "checks": {                                                                                 
           "id": [                                                                                 
               {                                                                                   
                   "path": "id",                                                                   
                   "quality": {                                                                    
                       "check_results": null,                                                      
                       "overall_result": null                                                      
                   },                                                                              
                   "coverage": {                                                                   
                       "check_results": [                                                          
                           {                                                                       
                               "name": "exists",                                                   
                               "result": true,                                                     
                               "value": null,                                                      
                               "reason": null,                                                     
                               "version": 1.0                                                      
                           },                                                                      
                           {                                                                       
                               "name": "non_empty",                                                
                               "result": true,                                                     
                               "value": null,                                                      
                               "reason": null,                                                     
                               "version": 1.0                                                      
                           }                                                                       
                       ],                                                                          
                       "overall_result": true                                                      
                   }                                                                               
               }                                                                                   
           ]
       }
   }

Frontend
--------

Pelican frontend automatically supports new field-level checks.
