""" Tools for calculating distribution

    CODE.distribution
    https://gitlab.com/datlab/ocp/dqt/wikis/Data-quality-checks/Dataset-level-checks/CODE.distribution

    append_to_scope
    ---------------


    get_result
    ---------------

"""

from tools.checks import get_empty_result_dataset
from tools.getter import get_values

import random

version = 1.0
"""
    author: Iaroslav Kolodka
"""


def add_item(scope, item, item_id, path, important_values=[], samples_num=20):
    """ Universal function for appending to scope

        parametres
        ----------
            scope: dict
            item: dic
            item_id: int
            path: str
            important_values: list
                list of values which will be controlled by rule: 0.01 <= ratio <= 0.99

        returns
        ----------
            scope: dict
                filled scope

    """

    ocids = get_values(item, "ocid", value_only=True)
    if not ocids or ocids[0] is None:
        return scope
    ocid = ocids[0]
    values = get_values(item, path, value_only=True)

    if not values:
        return scope

    if not scope:
        scope = {
            enum: {"count": 0, "examples": []}
            for enum in important_values
        }

    enum = values[0]

    if type(enum) is dict:
        print("fsdfdsf")
    if not enum and type(enum) != str:
        return scope

    if enum not in scope:
        scope.update(
            {
                enum: {
                    "count": 0,
                    "examples": []
                }
            }
        )

    if scope[enum]["count"] < samples_num:
        scope[enum]["examples"].append(
            {
                "item_id": item_id,
                "ocid": ocid
            }
        )
    else:
        rand_int = random.randint(0, scope[enum]["count"])
        if rand_int < samples_num:
            scope[enum]["examples"][rand_int] = {
                "item_id": item_id,
                "ocid": ocid
            }

    scope[enum]["count"] += 1

    return scope


def get_result(scope, important_values=[]):
    """ Universal function for getting distribution result

        parametres
        ----------
            scope: dict
            important_values: list
                list of values which will be controlled by rule: 0.01 <= ratio <= 0.99

        returns
        ----------
            result: dict
                distribution result

    """
    result = get_empty_result_dataset(version)

    if not scope:
        result["meta"] = {
            "reason": "no data items were processed"
        }
        return result

    enumes_amount = sum([scope[enum]["count"] for enum in scope])

    if enumes_amount == 0:
        result["meta"] = {
            "reason": "there is not a single tender with valid enumeration item"
        }
        return result

    passed = True
    for enum, value in scope.items():
        ratio = value["count"] / enumes_amount
        value["share"] = ratio
        if enum in important_values:
            if 0.001 > ratio or ratio > 0.99:
                passed = False

    result["result"] = passed
    result["value"] = 100 if passed else 0
    result["meta"] = {
        "shares": scope
    }
    return result
