import functools

from contracting_process.resource_level.consistent.parties_role import \
    calculate
from tools.checks import get_empty_result_resource

version = "1.0"

calculate_prepared = functools.partial(
    calculate,
    path='tender.tenderers',
    role='tenderer'
)


item_with_no_correct_parties = {
    "parties": [
        {
            "id": "7rBOL0",  # no roles
            "name": "Secretaria de Desarrollo Economico",
            "address": {
                "streetAddress": "Edificio San José,3 piso Boulevard KUWAIT "
            },
            "identifier": {"scheme": "HN-ONCAE-CE"},
            "contactPoint": {}
        },
        {
            "id": "0rw29R-7rBOL0",  # empty list of roles
            "name": "Unidad Central",
            "roles": [],
            "memberOf": [
                {"id": "7rBOL0", "name": "Secretaria de Desarrollo Economico"}
            ],
        }
    ]
}


def test_on_inaction():
    expecting_result = get_empty_result_resource(version)
    expecting_result["reason"] = "There are no parties with set role and id"
    result = calculate_prepared(item_with_no_correct_parties)
    assert expecting_result == result
