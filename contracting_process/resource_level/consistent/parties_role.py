"""
For each role of each party, there is an organization reference. The roles to test are:

-  procuringEntity
-  tenderer
-  supplier
-  payer
-  payee

The 'buyer' role is not tested, because there can be multiple buyers in the ``parties`` array, but there is only one
``buyer`` field for the primary buyer.

Since the test operates on all organization objects, the test silently ignores any party whose ``id`` field is missing,
as it cannot be referenced.

.. admonition:: Methodology notes

   -  ``id`` values are cast as ``str`` for matching.
"""

from pelican.util.checks import complete_result_resource, get_empty_result_resource
from pelican.util.getter import deep_get, deep_has, get_values

version = 1.0
applicable_roles = {
    "procuringEntity": "tender.procuringEntity.id",
    "tenderer": "tender.tenderers.id",
    "supplier": "awards.suppliers.id",
    "payer": "contracts.implementation.transactions.payer.id",
    "payee": "contracts.implementation.transactions.payee.id",
}


def calculate(item):
    result = get_empty_result_resource(version)

    parties = [
        {"path": v["path"], "id": str(v["value"]["id"]), "role": role}
        for v in get_values(item, "parties")
        if deep_has(v["value"], "id")
        for role in deep_get(v["value"], "roles", list)
        if role in applicable_roles
    ]

    if not parties:
        result["meta"] = {"reason": "no party has an id and an applicable role"}
        return result

    roles = {party["role"] for party in parties}

    references = {role: set(map(str, get_values(item, applicable_roles[role], value_only=True))) for role in roles}

    application_count = 0
    pass_count = 0
    failed_paths = []
    for party in parties:
        passed = party["id"] in references[party["role"]]

        application_count += 1
        if passed:
            pass_count += 1
        else:
            failed_paths.append({"path": party["path"], "role": party["role"], "id": party["id"]})

    return complete_result_resource(result, application_count, pass_count, failed_paths=failed_paths)
