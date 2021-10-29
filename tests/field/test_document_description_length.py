from contracting_process.field_level.checks.document_description_length import calculate
from tests import is_subset_dict


def test_passed():
    result = calculate({"description": "short"}, "description")
    assert is_subset_dict({"result": True}, result)

    result = calculate({"description": "".join("_" for _ in range(0, 250))}, "description")
    assert is_subset_dict({"result": True}, result)


def test_failed():
    data = {"description": "".join("_" for _ in range(0, 251))}
    result = calculate(data, "description")
    assert is_subset_dict(
        {
            "result": False,
            "value": len(data["description"]),
            "reason": "description exceeds max length of 250 characters",
        },
        result,
    )
