
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
                    "status": "notMet"
                }
            }
        ]
    },
    "planning": {
        "milestones": [
            {
                "title": "some_milestone",
                "properties": {
                    "status": "notMet"
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
                        "status": "notMet"
                    }
                }
            ],
            "implementation": {
                "milestones": [
                    {
                        "title": "some_milestone",
                        "properties": {
                            "status": "notMet"
                        }
                    }
                ]
            }
        }
    ],
}


def test_no_Milestones():
    result = get_empty_result_resource(version)
    result["result"] = None
    result["application_count"] = 0
    result["pass_count"] = 0
    result["meta"] = {}
    assert calculate(item_without_milestones) == result


def test_on_empty_Milestone():
    result = get_empty_result_resource(version)
    result["result"] = False
    result["application_count"] = 1
    result["pass_count"] = 0
    result["meta"] = {"references": []}
    result["meta"]["references"] = [
        {
            "result": False,
            "status": None,
            "path": "tender.milestones[0]"
        }
    ]
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
