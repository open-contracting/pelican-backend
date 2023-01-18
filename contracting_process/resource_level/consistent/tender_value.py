from tools.checks import complete_result_resource_pass_fail, get_empty_result_resource
from tools.currency_converter import convert
from tools.getter import deep_get, get_values, parse_date

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    tender_value = get_values(item, "tender.value", value_only=True)
    planning_budget_amount = get_values(item, "planning.budget.amount", value_only=True)

    # path not found
    if not tender_value or not planning_budget_amount:
        result["meta"] = {"reason": "values are not set"}
        return result

    tender_value = tender_value[0]
    planning_budget_amount = planning_budget_amount[0]

    # missing amount or currency fields
    if (
        "amount" not in tender_value
        or "currency" not in tender_value
        or "amount" not in planning_budget_amount
        or "currency" not in planning_budget_amount
    ):

        result["meta"] = {"reason": "amount or currency is not set"}
        return result

    tender_value_amount = deep_get(tender_value, "amount", force=float)
    planning_budget_amount_amount = deep_get(planning_budget_amount, "amount", force=float)

    # None fields
    if (
        tender_value_amount is None
        or tender_value["currency"] is None
        or planning_budget_amount_amount is None
        or planning_budget_amount["currency"] is None
    ):

        result["meta"] = {"reason": "amount is not a number or currency is null"}
        return result

    # currency conversion if necessary
    if tender_value["currency"] != planning_budget_amount["currency"]:
        ref_date = parse_date(get_values(item, "date", value_only=True)[0])
        tender_value_amount = convert(tender_value_amount, tender_value["currency"], "USD", ref_date)
        planning_budget_amount_amount = convert(
            planning_budget_amount_amount, planning_budget_amount["currency"], "USD", ref_date
        )

    # non-convertible values
    if tender_value_amount is None or planning_budget_amount_amount is None:
        result["meta"] = {
            "reason": "values are not convertible",
            "tender.value": tender_value,
            "planning.budget.amount": planning_budget_amount,
        }
        return result

    # amount is equal to zero
    if tender_value_amount == 0 or planning_budget_amount_amount == 0:
        result["meta"] = {
            "reason": "amount is equal to zero",
            "tender.value": tender_value,
            "planning.budget.amount": planning_budget_amount,
        }
        return result

    # different signs
    if (tender_value_amount > 0 and planning_budget_amount_amount < 0) or (
        tender_value_amount < 0 and planning_budget_amount_amount > 0
    ):

        result["meta"] = {
            "reason": "amounts have different signs",
            "tender.value": tender_value,
            "planning.budget.amount": planning_budget_amount,
        }
        return result

    ratio = abs(tender_value_amount - planning_budget_amount_amount) / abs(tender_value_amount)

    result["meta"] = {"tender.value": tender_value, "planning.budget.amount": planning_budget_amount}

    return complete_result_resource_pass_fail(result, ratio <= 0.5)
