Compiled release-level
======================

Backend
-------

#. Determine the type of check (see :ref:`repository-structure`).
#. Find a check under the corresponding ``contracting_process/resource_level`` sub-directory to copy as a starting point.
#. Add the check to the ``contracting_process/resource_level/definitions.py`` file. For example:

   .. literalinclude:: ../../../contracting_process/resource_level/definitions.py
      :language: python
      :start-at: consistent.number_of_tenderers
      :end-at: consistent.parties_roles

Each check is a function, named ``calculate`` by convention, that:

#. Accepts one argument, named ``item`` by convention
#. Creates an empty ``result`` dict
#. Determines whether the check can be calculated
#. If not, sets ``result["meta"] = {"reason": "..."}`` and returns the ``result`` dict
#. Determines whether the check passes

   .. note::

      Some ID fields allow both integer and string values. When resolving references by comparing IDs, the check should fail if the IDs are different types. It should neither succeed nor N/A (it is likely to N/A if IDs are not coerced to string).

#. Sets these keys on the ``result`` object:

   ``result`` (boolean)
     Whether the check passes
   ``application_count`` (integer)
     The number of times the check was applied (for example, once per array entry)
   ``pass_count`` (integer)
     The number of times the check passed
   ``meta`` (object)
     Any additional data to help interpret the result. For example, some coherence checks store pairs of incoherent dates, like:

     .. code-block:: python

        {
            "path_1": first_date["path"],
            "value_1": first_date["value"],
            "path_2": second_date["path"],
            "value_2": second_date["value"],
        }

#. Returns the ``result`` dict

An empty ``result`` dict looks like:

.. literalinclude:: ../../../tools/checks.py
   :language: python
   :start-after: get_empty_result_resource
   :end-at: }

Example
~~~~~~~

.. literalinclude:: ../../../contracting_process/resource_level/coherent/milestone_status.py
   :language: python

Storage
~~~~~~~

The results for each item are stored in a single row in the ``resource_level_check`` table. A stored ``result`` value looks like (only two entries in the ``checks`` array are shown):

.. code-block:: json

   {                                                                                                      
       "meta": {                                                                                          
           "ocid": "ocds-lcuori-0rw29R-003-2011-1",                                                       
           "item_id": 8477481                                                                             
       },                                                                                                 
       "checks": {                                                                                        
           "coherent.dates": {                                                                            
               "meta": {                                                                                  
                   "reason": "insufficient data for check"                                                
               },                                                                                         
               "value": null,                                                                             
               "result": null,                                                                            
               "version": 1.0,                                                                            
               "pass_count": null,                                                                        
               "application_count": null                                                                  
           },                                                                                             
           "coherent.period": {                                                                           
               "meta": {                                                                                  
                   "failed_paths": [                                                                      
                       {                                                                                  
                           "path": "tender.tenderPeriod",                                                 
                           "result": true                                                                 
                       },                                                                                 
                       {                                                                                  
                           "path": "tender.enquiryPeriod",                                                
                           "result": true                                                                 
                       }                                                                                  
                   ]                                                                                      
               },                                                                                         
               "value": null,                                                                             
               "result": true,                                                                            
               "version": 1.0,                                                                            
               "pass_count": 2,                                                                           
               "application_count": 2                                                                     
           }
       }
   }

Frontend
--------

Pelican frontend automatically supports new compiled release-level checks with known check types.

