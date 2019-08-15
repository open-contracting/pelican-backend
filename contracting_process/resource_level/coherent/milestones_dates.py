
from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import parse_date

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    first_dates = []
    first_dates.extend(get_values(item, 'planning.milestones.dateModified'))
    first_dates.extend(get_values(item, 'planning.milestones.dateMet'))
    first_dates.extend(get_values(item, 'tender.milestones.dateModified'))
    first_dates.extend(get_values(item, 'tender.milestones.dateMet'))
    first_dates.extend(get_values(item, 'contracts.milestones.dateModified'))
    first_dates.extend(get_values(item, 'contracts.milestones.dateMet'))
    first_dates.extend(get_values(item, 'contracts.implementation.milestones.dateModified'))
    first_dates.extend(get_values(item, 'contracts.implementation.milestones.dateMet'))

    pairs = [
        (first_date, second_date)
        for first_date in first_dates
        for second_date in get_values(item, 'date')
    ]

    failed_paths = []
    result['application_count'] = 0
    result['pass_count'] = 0
    for first_date, second_date in pairs:
        first_date_parsed = parse_date(first_date['value'])
        second_date_parsed = parse_date(second_date['value'])

        if first_date_parsed is None or second_date_parsed is None:
            continue

        result['application_count'] += 1

        if first_date_parsed <= second_date_parsed:
            result['pass_count'] += 1
        else:
            failed_paths.append(
                {
                    'path_1': first_date['path'],
                    'value_1': first_date['value'],
                    'path_2': second_date['path'],
                    'value_2': second_date['value'],
                }
            )

    if result['application_count'] == 0:
        result['application_count'] = None
        result['pass_count'] = None
        result['meta'] = {
            'reason': 'insufficient data for check'
        }
    else:
        result['result'] = result['application_count'] == result['pass_count']
        if not result['result']:
            result['meta'] = {
                'failed_paths': failed_paths
            }

    return result
