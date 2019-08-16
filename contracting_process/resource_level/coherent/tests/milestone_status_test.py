
from contracting_process.resource_level.coherent.milestone_status import \
    calculate
from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0

item_without_milestones = {
    "id": "sdfsdf",
    "name": "sdasdad"
}

item_with_empty_milestone = {
    "id": "sdfsdf",
    "name": "sdasdad",
    "tender": {
        "milestones": [
            {

            }
        ]
    }
}


item_with_all_milestones_locations = {
    "id": "sdfsdf",
    "name": "sdasdad",
    "tender": {
        "milestones": [
            {
                "title": "some_milestone",
                "properties": {
                    "status": "notMet",
                }
            }
        ]
    },
    "planning": {
        "milestones": [
            {
                "title": "some_milestone",
                "properties": {
                    "status": "notMet",
                }
            }
        ]
    },
    "contracts": [
        {
            "milestones": [
                {
                    "title": "some_milestone",
                    "properties": {
                        "status": "notMet",
                    }
                }
            ],
            "implementation": {
                "milestones": [
                    {
                        "title": "some_milestone",
                        "properties": {
                            "status": "notMet",
                        }
                    }
                ]
            }
        }
    ]
}

item_with_few_milestones_in_one_location = {
    "id": "sdfsdf",
    "name": "sdasdad",
    "contracts": [
        {
            "milestones": [
                {
                    "title": "some_milestone",
                    "properties": {
                        "status": "notMet",
                    }
                },
                {
                    "title": "some_another_milestone",
                    "properties": {
                        "status": "notMet",
                    }
                }
            ]
        },
        {
            "milestones": [
                {
                    "title": "some_milestone",
                    "properties": {
                        "status": "notMet",
                    }
                },
                {
                    "title": "some_another_milestone",
                    "properties": {
                        "status": "notMet",
                    }
                }
            ]
        }
    ],
}


item_with_incorrect_milestones = {
    "id": "sdfsdf",
    "name": "sdasdad",
    "tender": {
        "milestones": [
            {
                "title": "some_milestone",
                "properties": {
                    "status": "scheduled",
                    "dateMet": {
                        "some": "thing"
                    }
                }
            },
            {
                "title": "some_milestone",
                "properties": {
                    "status": "scheduled",
                    "dateMet": {}
                }
            }
        ]
    },
    "planning": {
        "milestones": [
            {
                "title": "some_milestone",
                "properties": {
                    "status": None,
                }
            },
            {

                "title": "some_milestone",
                "properties": {
                    "status": "met",
                }
            }
        ]
    },
    "contracts": [
        {
            "milestones": [
                {
                    "title": "some_milestone",
                    "properties": {
                        "status": "notMet",
                    }
                }
            ],
            "implementation": {
                "milestones": [
                    {
                        "title": "some_milestone",
                        "properties": {
                            "status": "notMet",
                        }
                    }
                ]
            }
        }
    ]
}


def test_no_milestones():
    result = get_empty_result_resource(version)
    result["result"] = None
    result["application_count"] = 0
    result["pass_count"] = 0
    result["meta"] = {}
    assert calculate(item_without_milestones) == result


def test_on_empty_milestone():
    result = get_empty_result_resource(version)
    result["result"] = None
    result["application_count"] = 0
    result["pass_count"] = 0
    result["meta"] = {"references": []}
    assert calculate(item_with_empty_milestone) == result


def test_on_true_result():
    result = get_empty_result_resource(version)
    result["result"] = True
    result["application_count"] = 4
    result["pass_count"] = 4
    # result[]
    result["meta"] = {"references": []}
    result["meta"]["references"] = [
        {
            "result": True,
            "status": "notMet",
            "path": "planning.milestones[0]"
        },
        {
            "result": True,
            "status": "notMet",
            "path": "tender.milestones[0]"
        },
        {
            "result": True,
            "status": "notMet",
            "path": "contracts[0].milestones[0]"
        },
        {
            "result": True,
            "status": "notMet",
            "path": "contracts[0].implementation.milestones[0]"
        }
    ]
    assert calculate(item_with_all_milestones_locations) == result


def test_on_few_milestones_in_one_location():
    result = get_empty_result_resource(version)
    result["result"] = True
    result["application_count"] = 4
    result["pass_count"] = 4
    # result[]
    result["meta"] = {"references": []}
    result["meta"]["references"] = [
        {
            "result": True,
            "status": "notMet",
            "path": "contracts[0].milestones[0]"
        },
        {
            "result": True,
            "status": "notMet",
            "path": "contracts[0].milestones[1]"
        },
        {
            "result": True,
            "status": "notMet",
            "path": "contracts[1].milestones[0]"
        },
        {
            "result": True,
            "status": "notMet",
            "path": "contracts[1].milestones[1]"
        }
    ]
    assert calculate(item_with_few_milestones_in_one_location) == result


def test_on_false_result():
    result = get_empty_result_resource(version)
    result["result"] = False
    result["application_count"] = 4
    result["pass_count"] = 3
    # result[]
    result["meta"] = {"references": []}
    result["meta"]["references"] = [
        {
            "result": False,
            "status": "scheduled",
            "path": "tender.milestones[0]"
        },
        {
            "result": True,
            "status": "scheduled",
            "path": "tender.milestones[1]"
        },
        {
            "result": True,
            "status": "notMet",
            "path": "contracts[0].milestones[0]"
        },
        {
            "result": True,
            "status": "notMet",
            "path": "contracts[0].implementation.milestones[0]"
        }
    ]
    assert calculate(item_with_incorrect_milestones) == result
