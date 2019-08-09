from datetime import datetime

from tools.helpers import parse_date

lower_bound_date = datetime(1970, 1, 1).date()
upper_bound_date = datetime(2050, 1, 1).date()


def date_realistic(data, key):
    value = data[key]
    if type(value) != str:
        return {
            "result": False,
            "value": value,
            "reason": "incorrect date format"
        }
    date = parse_date(value)
    if not date:
        return {
            "result": False,
            "value": value,
            "reason": "incorrect date format"
        }
    if date > upper_bound_date or date < lower_bound_date:
        return {"result": False,
                "value": value,
                "reason": "date is out of range"}
    return {"result": True}
