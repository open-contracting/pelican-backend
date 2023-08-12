from dataset.consistent import related_process_title

item_test_undefined1 = {"ocid": "0"}

items_test_undefined2 = [
    {"ocid": "0", "tender": {"title": "title0"}},
    {
        "ocid": "1",
        "relatedProcesses": [
            {"scheme": "ocid", "identifier": "10", "title": "title0"},
            {"identifier": "0", "title": "title0"},
            {"scheme": "ocid", "identifier": "0"},
        ],
    },
]


def test_undefined():
    scope = {}
    scope = related_process_title.add_item(scope, item_test_undefined1, 0)
    result = related_process_title.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no pair of related processes sets necessary fields"}

    scope = {}
    scope = related_process_title.add_item(scope, items_test_undefined2[0], 0)
    scope = related_process_title.add_item(scope, items_test_undefined2[1], 1)
    result = related_process_title.get_result(scope)
    assert result["result"] is None
    assert result["value"] is None
    assert result["meta"] == {"reason": "no pair of related processes sets necessary fields"}


items_test_passed = [
    {"ocid": "0", "tender": {"title": "title0"}},
    {
        "ocid": "1",
        "tender": {"title": "title1"},
        "relatedProcesses": [{"scheme": "ocid", "identifier": "0", "title": "title0"}],
    },
    {
        "ocid": "2",
        "tender": {"title": "title2"},
        "contracts": [
            {
                "relatedProcesses": [
                    {"scheme": "ocid", "identifier": "0", "title": "title0"},
                    {"scheme": "ocid", "identifier": "1", "title": "title1"},
                ]
            }
        ],
    },
]


def test_passed():
    scope = {}

    item_id = 0
    for item in items_test_passed:
        scope = related_process_title.add_item(scope, item, item_id)
        item_id += 1

    result = related_process_title.get_result(scope)
    assert result["result"] is True
    assert result["value"] == 100
    assert result["meta"] == {
        "total_processed": 3,
        "total_passed": 3,
        "total_failed": 0,
        "passed_examples": [
            {
                "original_process": {"ocid": "0", "title": "title0"},
                "related_process": {
                    "ocid": "1",
                    "related_ocid": "0",
                    "related_title": "title0",
                    "related_path": "relatedProcesses[0]",
                },
                "result": True,
            },
            {
                "original_process": {"ocid": "0", "title": "title0"},
                "related_process": {
                    "ocid": "2",
                    "related_ocid": "0",
                    "related_title": "title0",
                    "related_path": "contracts[0].relatedProcesses[0]",
                },
                "result": True,
            },
            {
                "original_process": {"ocid": "1", "title": "title1"},
                "related_process": {
                    "ocid": "2",
                    "related_ocid": "1",
                    "related_title": "title1",
                    "related_path": "contracts[0].relatedProcesses[1]",
                },
                "result": True,
            },
        ],
        "failed_examples": [],
    }


items_test_failed = [
    {"ocid": "0", "tender": {"title": "title0"}},
    {
        "ocid": "1",
        "tender": {"title": "title1"},
        "relatedProcesses": [{"scheme": "ocid", "identifier": "0", "title": "title0"}],
    },
    {
        "ocid": "2",
        "tender": {"title": "title2"},
        "contracts": [
            {
                "relatedProcesses": [
                    {"scheme": "ocid", "identifier": "0", "title": "title0"},
                    {"scheme": "ocid", "identifier": "1", "title": "unknown"},
                ]
            }
        ],
    },
]


def test_failed():
    scope = {}

    item_id = 0
    for item in items_test_failed:
        scope = related_process_title.add_item(scope, item, item_id)
        item_id += 1

    result = related_process_title.get_result(scope)
    assert result["result"] is False
    assert result["value"] == 100 * 2 / 3
    assert result["meta"] == {
        "total_processed": 3,
        "total_passed": 2,
        "total_failed": 1,
        "passed_examples": [
            {
                "original_process": {"ocid": "0", "title": "title0"},
                "related_process": {
                    "ocid": "1",
                    "related_ocid": "0",
                    "related_title": "title0",
                    "related_path": "relatedProcesses[0]",
                },
                "result": True,
            },
            {
                "original_process": {"ocid": "0", "title": "title0"},
                "related_process": {
                    "ocid": "2",
                    "related_ocid": "0",
                    "related_title": "title0",
                    "related_path": "contracts[0].relatedProcesses[0]",
                },
                "result": True,
            },
        ],
        "failed_examples": [
            {
                "original_process": {"ocid": "1", "title": "title1"},
                "related_process": {
                    "ocid": "2",
                    "related_ocid": "1",
                    "related_title": "unknown",
                    "related_path": "contracts[0].relatedProcesses[1]",
                },
                "result": False,
            }
        ],
    }
