from currency_converter import CurrencyConverter

from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import parse_date

version = 1.0


cc = CurrencyConverter("http://www.ecb.int/stats/eurofxref/eurofxref-hist.zip", fallback_on_wrong_date=True)


def calculate(item):
    result = get_empty_result_resource(version)

    tender_value = get_values(item, 'tender.value')
    planning_budget_amount = get_values(item, 'planning.budget.amount')

    # path not found
    if not tender_value or not planning_budget_amount:
        result['meta'] = {'reason': 'values are not set'}
        return result

    tender_value = tender_value[0]['value']
    planning_budget_amount = planning_budget_amount[0]['value']

    # missing amount or currency fields
    if 'amount' not in tender_value or 'currency' not in tender_value or \
       'amount' not in planning_budget_amount or 'currency' not in planning_budget_amount:

        result['meta'] = {'reason': 'amount or currency is not set'}
        return result

    # None fields
    if tender_value['amount'] is None or tender_value['currency'] is None or \
       planning_budget_amount['amount'] is None or planning_budget_amount['currency'] is None:

        result['meta'] = {'reason': 'amount or currency is null'}
        return result

    # unsupported currencies
    if tender_value['currency'] not in cc.currencies or planning_budget_amount['currency'] not in cc.currencies:
        result['meta'] = {
            'reason': 'unsupported currency', 'tender.value': tender_value,
            'planning.budget.amount': planning_budget_amount}
        return result

    # currency conversion if necessary
    if tender_value['currency'] == planning_budget_amount['currency']:
        tender_value_amount = tender_value['amount']
        planning_budget_amount_amount = planning_budget_amount['amount']
    else:
        ref_date = parse_date(get_values(item, 'date')[0]['value'])
        tender_value_amount = cc.convert(tender_value['amount'], tender_value['currency'], 'USD', date=ref_date)
        planning_budget_amount_amount = cc.convert(planning_budget_amount['amount'], planning_budget_amount['currency'],
                                                   'USD', date=ref_date)

    # amount is equal to zero
    if tender_value_amount == 0 or planning_budget_amount_amount == 0:
        result['meta'] = {
            'reason': 'amount is equal to zero', 'tender.value': tender_value,
            'planning.budget.amount': planning_budget_amount}
        return result

    # different signs
    if (tender_value_amount > 0 and planning_budget_amount_amount < 0) or \
       (tender_value_amount < 0 and planning_budget_amount_amount > 0):

        result['meta'] = {'reason': 'amounts have different signs',
                          'tender.value': tender_value, 'planning.budget.amount': planning_budget_amount}
        return result

    ratio = abs(tender_value_amount - planning_budget_amount_amount) / abs(tender_value_amount)
    passed = ratio <= 0.5

    result['result'] = passed
    result['application_count'] = 1
    result['pass_count'] = 1 if passed else 0
    result['meta'] = {'tender.value': tender_value, 'planning.budget.amount': planning_budget_amount}

    return result
