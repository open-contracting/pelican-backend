from contracting_process.resource_level.coherent.procurement_method_vs_number_of_tenderers import calculate

item_unset_procurement_method = {"tender": {"numberOfTenderers": 1}}
item_unset_number_of_tenderers = {"tender": {"procurementMethod": "direct"}}
item_non_direct = {"tender": {"procurementMethod": "limited", "numberOfTenderers": 1}}


def test_undefined():
    empty_result = calculate({})
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "numberOfTenderers is non-numeric"}

    empty_result = calculate(item_unset_procurement_method)
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "procurementMethod is not direct"}

    empty_result = calculate(item_unset_number_of_tenderers)
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "numberOfTenderers is non-numeric"}

    empty_result = calculate(item_non_direct)
    assert type(empty_result) == dict
    assert empty_result["result"] is None
    assert empty_result["application_count"] is None
    assert empty_result["pass_count"] is None
    assert empty_result["meta"] == {"reason": "procurementMethod is not direct"}


item_ok_1 = {"tender": {"numberOfTenderers": 1, "procurementMethod": "direct"}}

item_ok_2 = {"tender": {"numberOfTenderers": 0, "procurementMethod": "direct"}}


def test_ok():
    result = calculate(item_ok_1)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] is None

    result = calculate(item_ok_2)
    assert type(result) == dict
    assert result["result"] is True
    assert result["application_count"] == 1
    assert result["pass_count"] == 1
    assert result["meta"] is None


item_failed_1 = {"tender": {"numberOfTenderers": 2, "procurementMethod": "direct"}}


def test_failed():
    result = calculate(item_failed_1)
    assert type(result) == dict
    assert result["result"] is False
    assert result["application_count"] == 1
    assert result["pass_count"] == 0
    assert result["meta"] == {"numberOfTenderers": 2}
