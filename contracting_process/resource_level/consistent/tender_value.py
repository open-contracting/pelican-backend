
from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import parse_date
from tools.currency_converter import convert, currency_available

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
    if "amount" not in tender_value or "currency" not in tender_value or \
       "amount" not in planning_budget_amount or "currency" not in planning_budget_amount:

        result["meta"] = {"reason": "amount or currency is not set"}
        return result

    # None fields
    if tender_value["amount"] is None or tender_value["currency"] is None or \
       planning_budget_amount["amount"] is None or planning_budget_amount["currency"] is None:

        result["meta"] = {"reason": "amount or currency is null"}
        return result

    # unsupported currencies
    if not currency_available(tender_value["currency"]) or not currency_available(planning_budget_amount["currency"]):
        result["meta"] = {
            "reason": "unsupported currency", "tender.value": tender_value,
            "planning.budget.amount": planning_budget_amount}
        return result

    # currency conversion if necessary
    if tender_value["currency"] == planning_budget_amount["currency"]:
        tender_value_amount = tender_value["amount"]
        planning_budget_amount_amount = planning_budget_amount["amount"]
    else:
        ref_date = parse_date(get_values(item, "date", value_only=True)[0])
        tender_value_amount = convert(tender_value["amount"], tender_value["currency"], "USD", ref_date)
        planning_budget_amount_amount = convert(planning_budget_amount["amount"], planning_budget_amount["currency"],
                                                "USD", ref_date)

    # amount is equal to zero
    if tender_value_amount == 0 or planning_budget_amount_amount == 0:
        result["meta"] = {
            "reason": "amount is equal to zero", "tender.value": tender_value,
            "planning.budget.amount": planning_budget_amount}
        return result

    # different signs
    if (tender_value_amount > 0 and planning_budget_amount_amount < 0) or \
       (tender_value_amount < 0 and planning_budget_amount_amount > 0):

        result["meta"] = {"reason": "amounts have different signs",
                          "tender.value": tender_value, "planning.budget.amount": planning_budget_amount}
        return result

    ratio = abs(tender_value_amount - planning_budget_amount_amount) / abs(tender_value_amount)
    passed = ratio <= 0.5

    result["result"] = passed
    result["application_count"] = 1
    result["pass_count"] = 1 if passed else 0
    result["meta"] = {"tender.value": tender_value, "planning.budget.amount": planning_budget_amount}

    return result
