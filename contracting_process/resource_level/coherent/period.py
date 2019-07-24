from tools.checks import get_empty_result_resource
from tools.getter import get_values

from datetime import datetime

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    period_paths = ['tender.tenderPeriod', 
                    'tender.enquiryPeriod',
                    'tender.awardPeriod',
                    'tender.contractPeriod',
                    'award.contractPeriod',
                    'contract.period']

    application_count = None
    pass_count = None
    for path in period_paths:
        periods = get_values(item, path)

        if not periods:
            continue

        for index in range(0, len(periods)):
            period = periods[index]

            # missing dates
            if not period['startDate'] or not period['endDate']:
                continue
            
            startDate = parse_datetime(period['startDate'])
            endDate = parse_datetime(period['endDate'])

            # ill-formatted dates
            if not startDate or not endDate:
                continue

            passed = startDate <= endDate

            if application_count:
                application_count += 1
            else:
                application_count = 1

            if pass_count:
                pass_count = pass_count + 1 if passed else pass_count
            else:
                pass_count = 1 if passed else 0

            # initializing meta
            if not result['meta']:
                result['meta'] = []

            # filling in the path of the processed period
            result['meta'].append({'path': path, 'index': index, 'result': passed})

    result['application_count'] = application_count
    result['pass_count'] = pass_count

    if application_count and pass_count:
        result['result'] = application_count == pass_count
    else:
        result['meta'] = {'reason': 'incomplete data for check'}

    return result

'''
the following are valid dates according to ocds:

‘2014-10-21T09:30:00Z’ - 9:30 am on the 21st October 2014, UTC
‘2014-11-18T18:00:00-06:00’ - 6pm on 18th November 2014 CST (Central Standard Time)
'''
def parse_datetime(str_datetime):
    try:
        return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        pass

    if len(str_datetime) != 25:
        return None

    str_timezone = str_datetime[19:].replace(':','')
    str_datetime = str_datetime[:19] + str_timezone

    try:       
        return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%s%z')
    except ValueError:
        return None
    

