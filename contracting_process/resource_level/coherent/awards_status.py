
from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    values = get_values(item, 'awards')
    awards = [
        v for v in values
        if 'status' in v['value'] and
        v['value']['status'] in ['pending', 'cancelled', 'unsuccessful']
    ]

    if len(awards) == 0:
        result['meta'] = {
            'reason': 'there are no awards with check-specific properties'
        }
        return result
    
    values = get_values(item, 'contracts.awardID')
    contracts_awardID = [
        v['value'] for v in values
        if v['value'] is not None
    ]

    application_count = 0
    pass_count = 0
    result['meta'] = {'processed_awards': []}
    for award in awards:
        passed = award['value']['id'] not in contracts_awardID
        result['meta']['processed_awards'].append(
            {
                'path': award['path'],
                'id': award['value']['id'],
                'result': passed
            }
        )
        application_count += 1
        pass_count = pass_count + 1 if passed else pass_count

    result['result'] = application_count == pass_count
    result['application_count'] = application_count
    result['pass_count'] = pass_count

    return result
