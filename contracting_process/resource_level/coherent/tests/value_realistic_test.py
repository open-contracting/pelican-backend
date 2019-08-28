from contracting_process.resource_level.coherent.value_realistic import calculate
from tools.checks import get_empty_result_resource
from tools.bootstrap import bootstrap

version = 1.0
bootstrap('test', 'value_realistic_test')

"""
author: Iaroslav Kolodka

The file contains tests for contracting_process.resource_level.coherent.value.calculate.

- item_with_valid_value_in_USD
- item_with_valid_value_in_EUR
- item_with_invalid_value_in_USD
- item_with_invalid_value_in_HUF
- vitem_with_valid_value_in_non_eisting_currency

"""

item_with_valid_value_in_USD = {
    "date": "2019-01-10T22:00:00+01:00",
    "tender": {
        "value": {
            "amount": "1000",
            "currency": "USD"
        }
    }
}

item_with_valid_value_in_EUR = {
    "date": "2019-01-10T22:00:00+01:00",
    "tender": {
        "value": {
            "amount": "1000",
            "currency": "EUR"
        }
    }
}

item_with_invalid_value_in_USD = {
    "date": "2019-01-10T22:00:00+01:00",
    "tender": {
        "value": {
            "amount": "9222333444555",
            "currency": "EUR"
        }
    }
}

item_with_invalid_value_in_HUF = {
    "date": "2019-01-10T22:00:00+01:00",
    "tender": {
        "value": {
            "amount": "4999888000",
            "currency": "GBP"
        }
    }
}

item_with_valid_value_in_non_eisting_currency = {
    "date": "2019-01-10T22:00:00+01:00",
    "tender": {
        "value": {
            "amount": "3000",
            "currency": "WWW"
        }
    }
}


def test():
    result1 = result_initialiser(version, True, 1, 1, {
        "result": True,
        "amount": "1000",
        "currency": "USD",
        "path": "tender.value"
    })
    result2 = result_initialiser(version, True, 1, 1, {
        "result": True,
        "amount": "1000",
        "currency": "EUR",
        "path": "tender.value"
    })
    result3 = result_initialiser(version, False, 1, 0, {
        "result": False,
        "amount": "9222333444555",
        "currency": "EUR",
        "path": "tender.value"
    })
    result4 = result_initialiser(version, False, 1, 0, {
        "result": False,
        "amount": "4999888000",
        "currency": "GBP",
        "path": "tender.value"
    })
    result5 = result_initialiser(version, None, 0, 0)
    assert calculate(item_with_valid_value_in_USD) == result1
    assert calculate(item_with_valid_value_in_EUR) == result2
    assert calculate(item_with_invalid_value_in_USD) == result3
    assert calculate(item_with_invalid_value_in_HUF) == result4
    assert calculate(item_with_valid_value_in_non_eisting_currency) == result5


def result_initialiser(version: float, res: bool, app_count: int, pass_count: int, meta=None) -> dict:
    """
    Function create empty result and intialise it by parametres.

    Parameters
    ----------
    version : float
        Version of empty result
    res : bool
        if all tests were successed
    app_count : int
        application count
    pass_count : int
        pass count
    meta : dict or list of dicts
        metadata

    Returns
    -------
    dict
        Filled result

    """
    result = get_empty_result_resource(version)
    result["result"] = res
    result["application_count"] = app_count
    result["pass_count"] = pass_count
    if meta:
        result["meta"] = {"references": []}
        result["meta"]["references"].append(meta)
    return result
