
from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    values = get_values(item, 'contracts')
    contracts = [
        v for v in values
        if 'status' in v['value'] and
        v['value']['status'] in ['pending', 'cancelled']
    ]

    if len(contracts) == 0:
        result['meta'] = {
            'reason': 'there are no contracts with check-specific properties'
        }
        return result

    application_count = 0
    pass_count = 0
    result['meta'] = {'processed_contracts': []}
    for contract in contracts:
        passed = None
        transactions_length = None

        if (
            'implementation' in contract['value'] and
            'transactions' in contract['value']['implementation'] and
            len(contract['value']['implementation']['transactions']) > 0
        ):
            passed = False
            transactions_length = len(
                contract['value']['implementation']['transactions']
            )
        else:
            passed = True
            transactions_length = 0

        result['meta']['processed_contracts'].append(
            {
                'path': contract['path'],
                'transactions_length': transactions_length,
                'result': passed
            }
        )

        application_count += 1
        pass_count = pass_count + 1 if passed else pass_count

    result['result'] = application_count == pass_count
    result['application_count'] = application_count
    result['pass_count'] = pass_count

    return result
