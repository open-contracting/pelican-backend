
from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import convert, currency_available, parse_datetime

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    contracts = get_values(item, 'contracts')
    contracts = [c['value'] for c in contracts if c['value']]

    if not contracts:
        result['meta'] = {'reason': 'there are no contracts'}
        return result

    awards = get_values(item, 'awards')
    awards = [a['value'] for a in awards if a['value']]

    relevant_contracts = []
    for contract in contracts:
        matching_awards = [a for a in awards if contract['awardID'] == a['id']]

        # matching award can be only one
        if len(matching_awards) != 1:
            result['meta'] = {'reason': 'contract.awardID is not identity \
                    mapping to award.id'}
            return result

        matching_award = matching_awards[0]

        # value and amount fields set
        if 'value' not in contract or 'value' not in matching_award or \
                'currency' not in contract['value'] or \
                'amount' not in contract['value'] or \
                'currency' not in matching_award['value'] or \
                'amount' not in matching_award['value'] or \
                contract['value']['currency'] is None or \
                contract['value']['amount'] is None or \
                matching_award['value']['currency'] is None or \
                matching_award['value']['amount'] is None:

            result['meta'] = {'reason': 'value or amount fields not set'}
            return result

        # checking for non-existing currencies
        if not currency_available(contract['currency']) or \
                not currency_available(matching_award['currency']):

            result['meta'] = {'reason': 'non-existing currencies'}
            return result

        # converting values if necessary
        contract_value_amount = None
        award_value_amount = None
        if contract['value']['currency'] == \
                matching_award['value']['currency']:
            contract_value_amount = contract['value']['amount']
            award_value_amount = matching_award['value']['amount']
        else:
            contract_value_amount = convert(
                contract['value']['amount'],
                contract['value']['currency'],
                'USD', parse_datetime(item['date'])
            )
            award_value_amount = convert(
                matching_award['value']['amount'],
                matching_award['value']['currency'],
                'USD', parse_datetime(item['date'])
            )

        # checking for non-convertible values
        if contract_value_amount is None or award_value_amount is None:
            result['meta'] = {'reason': 'non-convertible values'}
            return result

        # amount is equal to zero
        if contract_value_amount == 0 or award_value_amount == 0:
            result['meta'] = {'reason': 'value.amount equal to zero'}
            return result

        # different signs
        if (contract_value_amount > 0 and award_value_amount < 0) or \
                (contract_value_amount < 0 and award_value_amount > 0):
            result['meta'] = {'reason': 'different signs for value.amount(s)'}
            return result

    result_result = True
    for award in awards:
        matching_contracts = [
            c for c in contracts if c['awardID'] == award['id']
        ]

        # no matching contracts
        if len(matching_contracts) == 0:
            continue

        award_value_amount = None
        contracts_value_amount_sum = None
        if all([award['value']['currency'] == c['value']['currency']
                for c in matching_contracts]):
            award_value_amount = award['value']['amount']
            contracts_value_amount_sum = sum(
                [c['value']['amount'] for c in matching_contracts]
            )
        else:
            award_value_amount = convert(
                award['value']['amount'], award['value']['currency'],
                'USD', parse_datetime(item['date'])
            )
            contracts_value_amount_sum = sum(
                [
                    convert(
                        c['value']['amount'], c['value']['currency'],
                        'USD', parse_datetime(item['date'])
                    )
                    for c in matching_contracts
                ]
            )

        ratio = abs(award_value_amount - contracts_value_amount_sum) \
            / abs(award_value_amount)
        passed = ratio <= 0.5

        result_result = result_result and passed
        result['meta'].append(
            [
                'awardID': award['id'],
                'awards.value': award['value'],
                'contracts.value_sum': contracts_value_amount_sum
            ]
        )

    result['result'] = result_result
    return result
