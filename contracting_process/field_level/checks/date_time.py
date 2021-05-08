from datetime import datetime

from tools.checks import get_empty_result_field
from tools.helpers import parse_date

lower_bound_date = datetime(1970, 1, 1).date()
upper_bound_date = datetime(2050, 1, 1).date()

name = "date_time"


def calculate(data, key):
    result = get_empty_result_field(name)

    value = data[key]
    if type(value) != str:
        result["result"] = False
        result["value"] = value
        result["reason"] = "incorrect date format"
        return result

    date = parse_date(value)
    if not date:
        result["result"] = False
        result["value"] = value
        result["reason"] = "incorrect date format"
        return result

    if date > upper_bound_date or date < lower_bound_date:
        result["result"] = False
        result["value"] = value
        result["reason"] = "date is out of range"
        return result

    result["result"] = True
    return result
