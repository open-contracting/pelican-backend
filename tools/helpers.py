
import re
import random
from datetime import datetime
from decimal import Decimal


def parse_datetime(str_datetime):
    '''
    the following are valid dates according to ocds:

    ‘2014-10-21T09:30:00Z’ - 9:30 am on the 21st October 2014, UTC
    ‘2014-11-18T18:00:00-06:00’ - 6pm on 18th November 2014 CST (Central Standard Time)
    '''
    if str_datetime is None or not isinstance(str_datetime, str):
        return None

    # limit to microseconds
    str_datetime = re.sub(
        r'(?<=T\d\d:\d\d:\d\d\.)(\d+)',
        lambda m: m.group(1)[:6],
        str_datetime
    )

    str_datetime = str_datetime.replace("Z", "+00:00")

    try:
        return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        pass

    try:
        return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        pass

    if len(str_datetime) < 25:
        return None

    str_timezone = str_datetime[-6:].replace(':', '')
    str_datetime = str_datetime[:-6] + str_timezone

    try:
        return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        pass

    try:
        return datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        pass

    return None


def parse_date(str_date):
    '''
    Parse string to valid date.
    '''
    if str_date is None or not isinstance(str_date, str):
        return None

    try:
        return datetime.strptime(str_date[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


def is_subset_dict(subset, superset):
    return subset.items() <= superset.items()


class ReservoirSampler:
    def __init__(self, samples_cap):
        if samples_cap < 1:
            raise ValueError("samples_cap must be a positive integer")

        self._samples_cap = samples_cap
        self._samples = []
        self._index = 0

    def process(self, value):
        if self._index < self._samples_cap:
            self._samples.append(value)
        else:
            r = random.randint(0, self._index)
            if r < self._samples_cap:
                self._samples[r] = value

        self._index += 1

    def retrieve_samples(self):
        return self._samples
