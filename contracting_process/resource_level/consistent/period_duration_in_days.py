
from tools.checks import get_empty_result_resource
from tools.helpers import parse_datetime
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    period_paths = [
        'tender.tenderPeriod',
        'tender.enquiryPeriod',
        'tender.awardPeriod',
        'tender.contractPeriod',
        'awards.contractPeriod',
        'contracts.period'
    ]

    periods = [
        period
        for path in period_paths
        for period in get_values(item, path)
    ]

    result['application_count'] = 0
    result['pass_count'] = 0
    result['meta'] = {'periods': []}
    for period in periods:
        start_date = parse_datetime(period['value']['startDate']) if 'startDate' in period['value'] else None
        end_date = parse_datetime(period['value']['endDate']) if 'endDate' in period['value'] else None
        max_extent_day = parse_datetime(period['value']['maxExtentDate']) if 'maxExtentDate' in period['value'] else None
        duration_in_days = period['value']['durationInDays'] if 'durationInDays' in period['value'] else None

        # this check cannot be applied
        if start_date is None or duration_in_days is None or (end_date is None and max_extent_day is None):
            continue

        passed = False
        if end_date is not None:
            passed = passed or (end_date - start_date).days == duration_in_days
        if max_extent_day is not None:
            passed = passed or (max_extent_day - start_date).days == duration_in_days

        result['application_count'] += 1
        result['pass_count'] = result['pass_count'] + 1 if passed else result['pass_count']
        result['meta']['periods'].append(
            {
                'path': period['path'],
                'result': passed
            }
        )

    if result['application_count'] == 0:
        result['application_count'] = None
        result['pass_count'] = None
        result['meta'] = {'reason': 'there are no values with check-specific properties'}
    else:
        result['result'] = result['application_count'] == result['pass_count']

    return result
