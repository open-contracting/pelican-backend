from datetime import datetime


def parse_datetime(str_datetime):
    '''
    the following are valid dates according to ocds:

    ‘2014-10-21T09:30:00Z’ - 9:30 am on the 21st October 2014, UTC
    ‘2014-11-18T18:00:00-06:00’ - 6pm on 18th November 2014 CST (Central Standard Time)
    '''
    if str_datetime is None:
        return None

    try:
        return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        pass

    if len(str_datetime) != 25:
        return None

    str_timezone = str_datetime[19:].replace(':', '')
    str_datetime = str_datetime[:19] + str_timezone

    try:
        return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        return None
