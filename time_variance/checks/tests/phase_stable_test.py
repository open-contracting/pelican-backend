from time_variance.checks import phase_stable
from tools.checks import get_empty_result_time_variance_scope

ancestor_empty = {"ocid": "3"}

new_empty = {"ocid": "3"}

ancestor_tender = {"ocid": "3", "tender": {"title": "sdfds"}}

new_tender = {"ocid": "3", "tender": {"title": "sdfds"}}

ancestor_planning = {"ocid": "3", "planning": {"rationale": ""}}

new_planning = {"ocid": "3", "planning": {"rationale": ""}}

ancestor_awards = {"ocid": "3", "awards": [{"rationale": ""}]}

new_awards = {
    "ocid": "3",
    "awards": [
        {"rationale": ""},
        {"rationale": ""},
    ],
}

ancestor_awards_big = {
    "ocid": "3",
    "awards": [
        {"rationale": ""},
        {"rationale": ""},
        {"rationale": ""},
    ],
}

ancestor_contracts = {"ocid": "3", "contracts": [{"rationale": ""}]}

new_contracts = {
    "ocid": "3",
    "contracts": [
        {"rationale": ""},
        {"rationale": ""},
    ],
}

ancestor_contracts_big = {
    "ocid": "3",
    "contracts": [
        {"rationale": ""},
        {"rationale": ""},
        {"rationale": ""},
    ],
}


def test_filter():
    scope = get_empty_result_time_variance_scope()
    assert phase_stable.filter(scope, ancestor_empty, 1, None, None) is True
    assert phase_stable.filter(scope, ancestor_tender, 1, None, None) is True
    assert phase_stable.filter(scope, ancestor_planning, 1, None, None) is True


def test_evaluate_tender():
    scope = get_empty_result_time_variance_scope()
    scope, result = phase_stable.evaluate(scope, ancestor_empty, 1, new_empty, 2)
    assert result is True

    scope, result = phase_stable.evaluate(scope, ancestor_tender, 1, new_empty, 2)
    assert result is False

    scope, result = phase_stable.evaluate(scope, ancestor_tender, 1, new_tender, 2)
    assert result is True


def test_evaluate_planning():
    scope = get_empty_result_time_variance_scope()
    scope, result = phase_stable.evaluate(scope, ancestor_empty, 1, new_empty, 2)
    assert result is True

    scope, result = phase_stable.evaluate(scope, ancestor_planning, 1, new_empty, 2)
    assert result is False

    scope, result = phase_stable.evaluate(scope, ancestor_planning, 1, new_planning, 2)
    assert result is True


def test_evaluate_awards():
    scope = get_empty_result_time_variance_scope()
    scope, result = phase_stable.evaluate(scope, ancestor_empty, 1, new_empty, 2)
    assert result is True

    scope, result = phase_stable.evaluate(scope, ancestor_awards, 1, new_empty, 2)
    assert result is False

    scope, result = phase_stable.evaluate(scope, ancestor_awards, 1, new_awards, 2)
    assert result is True

    scope, result = phase_stable.evaluate(scope, ancestor_awards_big, 1, new_awards, 2)
    assert result is False


def test_evaluate_contracts():
    scope = get_empty_result_time_variance_scope()
    scope, result = phase_stable.evaluate(scope, ancestor_empty, 1, new_empty, 2)
    assert result is True

    scope, result = phase_stable.evaluate(scope, ancestor_contracts, 1, new_empty, 2)
    assert result is False

    scope, result = phase_stable.evaluate(scope, ancestor_contracts, 1, new_contracts, 2)
    assert result is True

    scope, result = phase_stable.evaluate(scope, ancestor_contracts_big, 1, new_contracts, 2)
    assert result is False
