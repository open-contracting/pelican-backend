
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
        if 'startDate' in period['value']:
            start_date = parse_datetime(period['value']['startDate'])
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0) if start_date else None
        else:
            start_date = None

        if 'endDate' in period['value']:
            end_date = parse_datetime(period['value']['endDate'])
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0) if end_date else None
        else:
            end_date = None

        if 'maxExtentDate' in period['value']:
            max_extent_day = parse_datetime(period['value']['maxExtentDate'])
            max_extent_day = max_extent_day.replace(hour=0, minute=0, second=0, microsecond=0) if max_extent_day else None
        else:
            max_extent_day = None

        duration_in_days = period['value']['durationInDays'] if 'durationInDays' in period['value'] else None

        # this check cannot be applied
        if start_date is None or duration_in_days is None or (end_date is None and max_extent_day is None):
            continue

        passed = False
        if end_date is not None:
            passed = (end_date - start_date).days == duration_in_days
        else:
            passed = (max_extent_day - start_date).days == duration_in_days

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
