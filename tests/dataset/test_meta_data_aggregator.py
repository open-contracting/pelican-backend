from dataset.meta_data_aggregator import add_item, get_result
from pelican.util.currency_converter import bootstrap

bootstrap()


items_test_compiled_releases = [
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00"},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00"},
    {"ocid": "1", "date": "2019-01-10T22:00:00+01:00"},
]


def test_compiled_releases():
    scope = {}
    for item_id in range(len(items_test_compiled_releases)):
        scope = add_item(scope, items_test_compiled_releases[item_id], item_id)
    result = get_result(scope)

    assert result["compiled_releases"]["total_unique_ocids"] == 2
    assert sum(result["tender_lifecycle"].values()) == 0


items_test_tender_lifecycle = [
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "tender": {}},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "tender": {}, "planning": {}},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "contracts": [{}, {}, {}]},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "awards": [{}, {}, {}]},
    {"ocid": "0", "date": "2019-01-10T22:00:00+01:00", "contracts": [{"implementation": {}}]},
]


def test_tender_lifecycle():
    scope = {}
    for item_id in range(len(items_test_tender_lifecycle)):
        scope = add_item(scope, items_test_tender_lifecycle[item_id], item_id)
    result = get_result(scope)

    assert result["compiled_releases"]["total_unique_ocids"] == 1
    assert result["tender_lifecycle"] == {"planning": 1, "tender": 2, "award": 3, "contract": 4, "implementation": 1}
