import math

from tools.checks import field_quality_check

name = "number_checks"


def test(value):
    if type(value) == complex:
        return False, "not a real number"
    try:
        number = float(value)
    except ValueError:
        return False, "can't convert to float"
    if not math.isfinite(number):
        return False, "not a finite number"

    # Range tests for coherence.
    return number >= 0, "less than 0"


calculate = field_quality_check(name, test)
