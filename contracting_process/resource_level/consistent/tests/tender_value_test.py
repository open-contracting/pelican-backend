from contracting_process.resource_level.consistent.tender_value import \
    calculate

item_test_undefined1 = {
    "tender": {

    },
    "planning": {
        "budget": {

        }
    }
}

item_test_undefined2 = {
    "tender": {
        "value": {

        }
    },
    "planning": {
        "budget": {
            "amount": {

            }
        }
    }
}

item_test_undefined3 = {
    "tender": {
        "value": {
            "amount": 100.0,
            "currency": None
        }
    },
    "planning": {
        "budget": {
            "amount": {
                "amount": 100.0,
                "currency": "USD"
            }
        }
    }
}


def test_undefined():
    empty_result = calculate(item_test_undefined1)
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "values are not set"}

    result = calculate(item_test_undefined2)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "amount or currency is not set"}

    result = calculate(item_test_undefined3)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "amount or currency is null"}


item_test_unsupported_currencies = \
    {
        "tender": {
            "value": {
                "amount": 100.0,
                "currency": "HAL"
            }
        },
        "planning": {
            "budget": {
                "amount": {
                    "amount": 100.0,
                    "currency": "USD"
                }
            }
        }
    }


def test_unsupported_currencies():
    result = calculate(item_test_unsupported_currencies)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {
        "reason": "unsupported currency",
        "tender.value": item_test_unsupported_currencies["tender"]["value"],
        "planning.budget.amount": item_test_unsupported_currencies["planning"]["budget"]["amount"]
    }


item_test_currency_conversion = {
    "tender": {
        "value": {
            "amount": 100.0,
            "currency": "CZK"
        }
    },
    "planning": {
        "budget": {
            "amount": {
                "amount": 100.0,
                "currency": "JPY"
            }
        }
    },
    "date": "2007-08-03T22:00:00+01:00"
}


def test_currency_conversion():
    result = calculate(item_test_currency_conversion)
    assert result["result"] is not None
    assert result["application_count"] is not None
    assert result["pass_count"] is not None
    assert result["meta"]["tender.value"] == item_test_currency_conversion["tender"]["value"]
    assert result["meta"]["planning.budget.amount"] == item_test_currency_conversion["planning"]["budget"]["amount"]


item_test_zero_amount = {
    "tender": {
        "value": {
            "amount": 100.0,
            "currency": "CZK"
        }
    },
    "planning": {
        "budget": {
            "amount": {
                "amount": 0.0,
                "currency": "CZK"
            }
        }
    }
}


def test_zero_amount():
    result = calculate(item_test_zero_amount)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == \
        {"reason": "amount is equal to zero",
         "tender.value": item_test_zero_amount["tender"]["value"],
         "planning.budget.amount": item_test_zero_amount["planning"]["budget"]["amount"]}


item_test_different_signs = {
    "tender": {
        "value": {
            "amount": 100.0,
            "currency": "CZK"
        }
    },
    "planning": {
        "budget": {
            "amount": {
                "amount": -100.0,
                "currency": "CZK"
            }
        }
    }
}


def test_different_signs():
    result = calculate(item_test_different_signs)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == \
        {"reason": "amounts have different signs",
         "tender.value": item_test_different_signs["tender"]["value"],
         "planning.budget.amount": item_test_different_signs["planning"]["budget"]["amount"]}


item_test_passed1 = {
    "tender": {
        "value": {
            "amount": 100.0,
            "currency": "CZK"
        }
    },
    "planning": {
        "budget": {
            "amount": {
                "amount": 148.0,
                "currency": "CZK"
            }
        }
    }
}

item_test_passed2 = {
    "tender": {
        "value": {
            "amount": -100.0,
            "currency": "CZK"
        }
    },
    "planning": {
        "budget": {
            "amount": {
                "amount": -50.0,
                "currency": "CZK"
            }
        }
    }
}


def test_passed():
    result = calculate(item_test_passed1)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "tender.value": item_test_passed1["tender"]["value"],
        "planning.budget.amount": item_test_passed1["planning"]["budget"]["amount"]
    }

    result = calculate(item_test_passed2)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == {
        "tender.value": item_test_passed2["tender"]["value"],
        "planning.budget.amount": item_test_passed2["planning"]["budget"]["amount"]
    }


item_test_failed1 = {
    "tender": {
        "value": {
            "amount": 500.0,
            "currency": "CZK"
        }
    },
    "planning": {
        "budget": {
            "amount": {
                "amount": 249.0,
                "currency": "CZK"
            }
        }
    }
}

item_test_failed2 = {
    "tender": {
        "value": {
            "amount": -500.0,
            "currency": "CZK"
        }
    },
    "planning": {
        "budget": {
            "amount": {
                "amount": -751.0,
                "currency": "CZK"
            }
        }
    }
}


def test_failed():
    result = calculate(item_test_failed1)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "tender.value": item_test_failed1["tender"]["value"],
        "planning.budget.amount": item_test_failed1["planning"]["budget"]["amount"]
    }

    result = calculate(item_test_failed2)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {
        "tender.value": item_test_failed2["tender"]["value"],
        "planning.budget.amount": item_test_failed2["planning"]["budget"]["amount"]
    }
