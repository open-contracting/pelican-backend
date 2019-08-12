
from contracting_process.resource_level.consistent.org_ref_name_consistent import \
    calculate
from tools.checks import get_empty_result_resource

version = "1.0"


def initialize_for_ok(result):
    result.result = True
    result.value = "abc"
    # result.meta = 
    result.aplication_count = 1
    result.pass_count = 1


def test_ok():
    result = get_empty_result_resource(version)
    initialize_for_ok(result)
    assert calculate({}) == result
