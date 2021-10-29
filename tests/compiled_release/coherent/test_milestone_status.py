from contracting_process.resource_level.coherent.milestone_status import calculate
from tools.checks import get_empty_result_resource

version = 1.0

item_unset = {"id": "1"}
item_with_empty_milestone = {"id": "1", "tender": {"milestones": [{}]}}
item_with_all_milestones_locations = {
    "id": "1",
    "tender": {
        "milestones": [
            {
                "title": "some_milestone",
                "status": "notMet",
            }
        ]
    },
    "planning": {
        "milestones": [
            {
                "title": "some_milestone",
                "status": "notMet",
            }
        ]
    },
    "contracts": [
        {
            "milestones": [
                {
                    "title": "some_milestone",
                    "status": "notMet",
                }
            ],
            "implementation": {
                "milestones": [
                    {
                        "title": "some_milestone",
                        "status": "notMet",
                    }
                ]
            },
        }
    ],
}
item_with_few_milestones_in_one_location = {
    "id": "1",
    "contracts": [
        {
            "milestones": [
                {
                    "title": "some_milestone",
                    "status": "notMet",
                },
                {
                    "title": "some_another_milestone",
                    "status": "notMet",
                },
            ]
        },
        {
            "milestones": [
                {
                    "title": "some_milestone",
                    "status": "notMet",
                },
                {
                    "title": "some_another_milestone",
                    "status": "notMet",
                },
            ]
        },
    ],
}
item_with_incorrect_milestones__invalid_schema = {
    "id": "1",
    "tender": {
        "milestones": [
            {"title": "some_milestone", "status": "scheduled", "dateMet": {"some": "thing"}},
            {"title": "some_milestone", "status": "scheduled", "dateMet": {}},
        ]
    },
    "planning": {
        "milestones": [
            {
                "title": "some_milestone",
                "status": None,
            },
            {
                "title": "some_milestone",
                "status": "met",
            },
        ]
    },
    "contracts": [
        {
            "milestones": [
                {
                    "title": "some_milestone",
                    "status": "notMet",
                }
            ],
            "implementation": {
                "milestones": [
                    {
                        "title": "some_milestone",
                        "status": "notMet",
                    }
                ]
            },
        }
    ],
}


def test_no_milestones():
    result = get_empty_result_resource(version)
    result["result"] = None
    result["application_count"] = 0
    result["pass_count"] = 0
    result["meta"] = {}
    assert calculate(item_unset) == result


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
        {"result": True, "status": "notMet", "path": "planning.milestones[0]"},
        {"result": True, "status": "notMet", "path": "tender.milestones[0]"},
        {"result": True, "status": "notMet", "path": "contracts[0].milestones[0]"},
        {"result": True, "status": "notMet", "path": "contracts[0].implementation.milestones[0]"},
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
        {"result": True, "status": "notMet", "path": "contracts[0].milestones[0]"},
        {"result": True, "status": "notMet", "path": "contracts[0].milestones[1]"},
        {"result": True, "status": "notMet", "path": "contracts[1].milestones[0]"},
        {"result": True, "status": "notMet", "path": "contracts[1].milestones[1]"},
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
        {"result": False, "status": "scheduled", "path": "tender.milestones[0]"},
        {"result": True, "status": "scheduled", "path": "tender.milestones[1]"},
        {"result": True, "status": "notMet", "path": "contracts[0].milestones[0]"},
        {"result": True, "status": "notMet", "path": "contracts[0].implementation.milestones[0]"},
    ]
    assert calculate(item_with_incorrect_milestones__invalid_schema) == result
