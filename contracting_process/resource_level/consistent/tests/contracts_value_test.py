from contracting_process.resource_level.consistent.contracts_value \
    import calculate

item_test_undefined_no_contracts = {
    'contracts': [

    ]
}

item_test_undefined_no_awards = {
    'contracts': [
        {
            'awardID': 0
        }
    ],
    'awards': [

    ]
}

item_test_undefined_same_id = {
    'contracts': [
        {
            'awardID': 0
        }
    ],
    'awards': [
        {
            'id': 0
        },
        {
            'id': 0
        }
    ]
}

item_test_undefined_missing_fields = {
    'contracts': [
        {
            'awardID': 0
        }
    ],
    'awards': [
        {
            'id': 0
        }
    ]
}

item_test_undefined_bad_currency = {
    'contracts': [
        {
            'awardID': 0,
            'value': {
                'currency': 'HAL',
                'amount': 100
            }
        }
    ],
    'awards': [
        {
            'id': 0,
            'value': {
                'currency': 'USD',
                'amount': 100
            }
        }
    ]
}


def test_undefined():
    result = calculate(item_test_undefined_no_contracts)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no contracts"}

    result = calculate(item_test_undefined_no_awards)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "there are no awards"}

    result = calculate(item_test_undefined_bad_currency)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "non-existing currencies"}

    result = calculate(item_test_undefined_same_id)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "multiple awards with the same id"}

    result = calculate(item_test_undefined_missing_fields)
    assert result["result"] is None
    assert result["application_count"] is None
    assert result["pass_count"] is None
    assert result["meta"] == {"reason": "amount or currency is not set"}

item_test_passed = {
    'contracts': [
        {
            'awardID': 'str',
            'value': {
                'currency': 'USD',
                'amount': 100
            }
        },
        {
            'awardID': 'str',
            'value': {
                'currency': 'USD',
                'amount': 25
            }
        }
    ],
    'awards': [
        {
            'id': 'str',
            'value': {
                'currency': 'USD',
                'amount': 100
            }
        }
    ]
}


def test_passed():
    result = calculate(item_test_passed)
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] == [
        {
            'awardID': 'str',
            'awards.value': {
                'amount': 100,
                'currency': 'USD'
            },
            'contracts.value_sum': 125
        }
    ]

item_test_failed = {
    'contracts': [
        {
            'awardID': 'str',
            'value': {
                'currency': 'USD',
                'amount': -100
            }
        },
        {
            'awardID': 'str',
            'value': {
                'currency': 'USD',
                'amount': -51
            }
        }
    ],
    'awards': [
        {
            'id': 'str',
            'value': {
                'currency': 'USD',
                'amount': -100
            }
        }
    ]
}


def test_failed():
    result = calculate(item_test_failed)
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == [
        {
            'awardID': 'str',
            'awards.value': {
                'amount': -100,
                'currency': 'USD'
            },
            'contracts.value_sum': -151
        }
    ]


item_test_passed_multiple_awards = {
    'contracts': [
        {
            'awardID': 0,
            'value': {
                'currency': 'USD',
                'amount': 100
            }
        },
        {
            'awardID': 0,
            'value': {
                'currency': 'USD',
                'amount': 25
            }
        },
        {
            'awardID': 1,
            'value': {
                'currency': 'USD',
                'amount': 10
            }
        }
    ],
    'awards': [
        {
            'id': 0,
            'value': {
                'currency': 'USD',
                'amount': 100
            }
        },
        {
            'id': 1,
            'value': {
                'currency': 'USD',
                'amount': 10
            }
        }
    ]
}


def test_passed_multiple_awards():
    result = calculate(item_test_passed_multiple_awards)
    assert result["result"] is True
    assert result["application_count"] == 2
    assert result["pass_count"] == 2
    assert result["meta"] == [
        {
            'awardID': 0,
            'awards.value': {
                'amount': 100,
                'currency': 'USD'
            },
            'contracts.value_sum': 125
        },
        {
            'awardID': 1,
            'awards.value': {
                'amount': 10,
                'currency': 'USD'
            },
            'contracts.value_sum': 10
        }
    ]

item_test_failed_multiple_awards = {
    'contracts': [
        {
            'awardID': 0,
            'value': {
                'currency': 'USD',
                'amount': 100
            }
        },
        {
            'awardID': 0,
            'value': {
                'currency': 'USD',
                'amount': 25
            }
        },
        {
            'awardID': 1,
            'value': {
                'currency': 'USD',
                'amount': 1
            }
        }
    ],
    'awards': [
        {
            'id': 0,
            'value': {
                'currency': 'USD',
                'amount': 100
            }
        },
        {
            'id': 1,
            'value': {
                'currency': 'USD',
                'amount': 20
            }
        }
    ]
}


def test_failed_multiple_awards():
    result = calculate(item_test_failed_multiple_awards)
    assert result["result"] is False
    assert result["application_count"] == 2
    assert result["pass_count"] == 1
    assert result["meta"] == [
        {
            'awardID': 0,
            'awards.value': {
                'amount': 100,
                'currency': 'USD'
            },
            'contracts.value_sum': 125
        },
        {
            'awardID': 1,
            'awards.value': {
                'amount': 20,
                'currency': 'USD'
            },
            'contracts.value_sum': 1
        }
    ]
