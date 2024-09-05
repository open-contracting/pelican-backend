from dataset.distribution import buyer

item_unset = {"ocid": "0"}


def test_undefined():
    scope = {}
    result = buyer.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no compiled releases set necessary fields"}

    scope = {}
    scope = buyer.add_item(scope, item_unset, 0)
    result = buyer.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no compiled releases set necessary fields"}


items_test_undefined_multiple1 = [
    {
        "ocid": "0",
    },
    {"ocid": "1", "buyer": {}},
    {"ocid": "2", "buyer": {"identifier": {}}},
    {"ocid": "3", "buyer": {"identifier": {"scheme": None, "id": None}}},
    {"ocid": "4", "buyer": {"identifier": {"scheme": "ICO", "id": None}}},
    {"ocid": "5", "buyer": {"identifier": {"scheme": None, "id": "5"}}},
]

items_test_undefined_multiple2 = [
    {"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": "0"}}} for _ in range(buyer.min_items - 1)
]


def test_undefined_multiple():
    scope = {}

    for item_id, item in enumerate(items_test_undefined_multiple1):
        scope = buyer.add_item(scope, item, item_id)

    result = buyer.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no compiled releases set necessary fields"}

    scope = {}

    for item_id, item in enumerate(items_test_undefined_multiple2):
        scope = buyer.add_item(scope, item, item_id)

    result = buyer.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "fewer than 1000 occurrences of necessary fields"}


items_test_failed1 = [
    {"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": num}}} for num in range(buyer.min_items)
]

items_test_failed2 = [
    {"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": num}}} for num in range(buyer.min_items)
]
items_test_failed2.extend(
    [{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": -1}}} for _ in range(buyer.min_items)]
)


def test_failed():
    scope = {}

    for item_id, item in enumerate(items_test_failed1):
        scope = buyer.add_item(scope, item, item_id)

    result = buyer.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert result["meta"]["total_ocid_count"] == buyer.min_items
    assert result["meta"]["total_buyer_count"] == buyer.min_items
    assert result["meta"]["counts"]["1"]["total_ocid_count"] == buyer.min_items
    assert result["meta"]["counts"]["1"]["total_buyer_count"] == buyer.min_items
    assert len(result["meta"]["examples"]) == buyer.sample_size

    scope = {}

    for item_id, item in enumerate(items_test_failed2):
        scope = buyer.add_item(scope, item, item_id)

    result = buyer.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 0
    assert result["meta"]["total_ocid_count"] == 2 * buyer.min_items
    assert result["meta"]["total_buyer_count"] == buyer.min_items + 1
    assert result["meta"]["counts"]["1"]["total_ocid_count"] == buyer.min_items
    assert result["meta"]["counts"]["1"]["total_buyer_count"] == buyer.min_items
    assert result["meta"]["counts"]["100+"]["total_ocid_count"] == buyer.min_items
    assert result["meta"]["counts"]["100+"]["total_buyer_count"] == 1
    assert len(result["meta"]["examples"]) == buyer.sample_size


items_test_passed_multiple = []
items_test_passed_multiple.extend(
    [{"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": item_id}}} for item_id in range(100)]
)
items_test_passed_multiple.extend(
    [
        {"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": item_id}}}
        for _ in range(1, 3)
        for item_id in range(100, 200)
    ]
)
items_test_passed_multiple.extend(
    [
        {"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": item_id}}}
        for _ in range(3, 24)
        for item_id in range(200, 300)
    ]
)
items_test_passed_multiple.extend(
    [
        {"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": item_id}}}
        for _ in range(24, 75)
        for item_id in range(300, 400)
    ]
)
items_test_passed_multiple.extend(
    [
        {"ocid": "0", "buyer": {"identifier": {"scheme": "ICO", "id": item_id}}}
        for _ in range(75, 176)
        for item_id in range(400, 500)
    ]
)


def test_passed_multiple():
    scope = {}

    for item_id, item in enumerate(items_test_passed_multiple):
        scope = buyer.add_item(scope, item, item_id)

    result = buyer.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert result["meta"]["total_ocid_count"] == 100 * 176
    assert result["meta"]["counts"]["1"]["total_ocid_count"] == 100 * 1
    assert result["meta"]["counts"]["2_20"]["total_ocid_count"] == 100 * 2
    assert result["meta"]["counts"]["21_50"]["total_ocid_count"] == 100 * 21
    assert result["meta"]["counts"]["51_100"]["total_ocid_count"] == 100 * 51
    assert result["meta"]["counts"]["100+"]["total_ocid_count"] == 100 * 101
    assert len(result["meta"]["examples"]) == buyer.sample_size
