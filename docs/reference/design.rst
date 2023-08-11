Check design
============

Goals
-----

Pelican is focused on data quality. It supports an interrogation of the quality of a dataset, rather than an exploration of the data that it contains. As such, it is not designed to support many features that are more appropriate to exploration.

It is also focused on *intrinsic* quality rather than *extrinsic* quality. That said, it can include intrinsic metrics that are easy to calculate (like the number of contracting processes) to support extrinsic metrics (like the proportion of all contracts covered by the dataset).

Levels
------

Quality checks are grouped into four levels, based on the subject they are measuring:

Field-level
  A single field's value
Compiled release-level
  A single contracting process
Dataset-level
  A collection of contracting processes
Time-based
  Two collections at different times

Monetary values
---------------

To compare and sum amounts, all amounts are converted to USD. This conversion does not take inflation into account: EUR in 2010 is converted to USD in 2010. As such, checks against datasets covering periods of high inflation might produce incorrect results. Relevant checks are:

coherent/value_realistic
  Each monetary value is between -5 billion USD and +5 billion USD.
distribution/value
  The sum of the top 1% of tender/award/contract values doesn't exceed 50% of the sum of all such values.

Compiled release-level consistency checks compare tender, award, contract and transaction amounts. These amounts are expected to cover a short period, such that incorrect results are unlikely, especially given the generous margins.
