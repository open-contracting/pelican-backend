
from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import convert, parse_datetime

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    contracts = get_values(item, 'contracts')
    awards_id = get_values(item, 'awards.id')
    awards_id = [str(id['value']) for id in awards_id]

    result['application_count'] = 0
    result['pass_count'] = 0
    result['meta'] = {'contracts': []}
    for contract in contracts:
        # testing whether there are any transactions for the current contract
        if (
            'implementation' not in contract['value'] or
            'transactions' not in contract['value']['implementation'] or
            not contract['value']['implementation']['transactions']
        ):
            continue

        transactions = contract['value']['implementation']['transactions']

        # checking if referenced award exists and is the only one
        if awards_id.count(str(contract['value']['awardID'])) != 1:
            continue

        # checking whether all check-specific fields are set
        if (
            'value' not in contract['value'] or
            'currency' not in contract['value']['value'] or
            'amount' not in contract['value']['value'] or
            contract['value']['value']['amount'] is None or
            contract['value']['value']['currency'] is None or
            any(
                [
                    'value' not in transaction or
                    'currency' not in transaction['value'] or
                    'amount' not in transaction['value'] or
                    transaction['value']['amount'] is None or
                    transaction['value']['currency'] is None
                    for transaction in transactions
                ]
            )
        ):
            continue

        # checking whether all values have the same currency set, otherwise going for conversion
        conversion_failed = False
        currency_used = None
        contract_amount = 0
        transactions_amount_sum = 0
        currencies = [contract['value']['value']['currency']]
        currencies.extend([transaction['value']['currency'] for transaction in transactions])
        if len(set(currencies)) == 1:
            currency_used = currencies[0]
            contract_amount = contract['value']['value']['amount']
            transactions_amount_sum = sum(
                [transaction['value']['amount'] for transaction in transactions]
            )
        else:
            currency_used = 'USD'
            contract_amount = convert(
                contract['value']['value']['amount'],
                contract['value']['value']['currency'],
                currency_used,
                parse_datetime(item['date'])
            )

            if contract_amount is None:
                conversion_failed = True

            for transaction in transactions:
                amount = convert(
                    transaction['value']['amount'],
                    transaction['value']['currency'],
                    currency_used,
                    parse_datetime(item['date'])
                )

                if amount is None:
                    conversion_failed = True
                    break

                transactions_amount_sum += amount

        if conversion_failed:
            continue

        # contract is applicable for this check
        passed = transactions_amount_sum <= contract_amount

        result['application_count'] += 1
        result['pass_count'] = result['pass_count'] + 1 if passed else result['pass_count']
        result['meta']['contracts'].append(
            {
                'path': contract['path'],
                'contract_amount': contract_amount,
                'transactions_amount_sum': transactions_amount_sum,
                'currency': currency_used
            }
        )

    if result['application_count'] == 0:
        result['application_count'] = None
        result['pass_count'] = None
        result['meta'] = {'reason': 'there are no values with check-specific properties'}
    else:
        result['result'] = result['application_count'] ==  result['pass_count']

    return result
