"""
For each award, the sum of its contracts' values isn't less than 50%, or more than 150%, of the award's value, after
conversion to USD if necessary.

Since the test operates on all award and contract values, the test silently ignores:

1. any contract whose ``awardID`` doesn't match the ``id`` of exactly one award
2. if an amount is missing, zero or non-numeric
3. if a currency is missing or unknown
4. if the two amounts aren't both positive or both negative
5. if currency conversion is necessary and the release date is invalid, before 1999, or in the future
"""

import datetime
from collections import Counter, defaultdict

from pelican.util.checks import complete_result_resource, get_empty_result_resource
from pelican.util.currency_converter import convert
from pelican.util.getter import deep_get, deep_has

version = 1.0


def _get_amount(item, no_conversion, amount, currency, date):
    if no_conversion:
        return amount
    elif date is not None:
        return convert(amount, currency, "USD", date)


def calculate(item):
    result = get_empty_result_resource(version)

    date = deep_get(item, "date", datetime.datetime)

    awards = deep_get(item, "awards")
    if not awards:
        result["meta"] = {"reason": "no award is set"}
        return result

    contracts = deep_get(item, "contracts")
    if not contracts:
        result["meta"] = {"reason": "no contract is set"}
        return result

    # (1) No matching possible.
    awards = [award for award in awards if deep_has(award, "id")]
    contracts = [contract for contract in contracts if deep_has(contract, "awardID")]

    award_id_counts = Counter(str(award["id"]) for award in awards)

    contracts_lookup = defaultdict(list)
    for contract in contracts:
        contracts_lookup[str(contract["awardID"])].append(contract)

    application_count = 0
    pass_count = 0
    for award in awards:
        award_id = str(award["id"])
        # (1) No matching award (singular).
        if award_id_counts[award_id] != 1:
            continue

        matches = contracts_lookup[award_id]
        # (1) No matching contracts.
        if not matches:
            continue

        currency = deep_get(award, "value.currency")

        currencies = {currency} | {deep_get(contract, "value.currency") for contract in matches}
        no_conversion = len(currencies) == 1
        # (3) Currency is missing.
        if None in currencies:
            continue

        unconverted_amount = deep_get(award, "value.amount", float)
        # (2) Amount is missing or non-numeric.
        if unconverted_amount is None:
            continue

        award_amount = _get_amount(award, no_conversion, unconverted_amount, currency, date)
        # (2,5) Amount is zero or unconvertable.
        if award_amount is None or award_amount == 0:
            continue

        contracts_amount_sum = 0
        for contract in matches:
            currency = deep_get(contract, "value.currency")

            unconverted_amount = deep_get(contract, "value.amount", float)
            # (2) Amount is missing or non-numeric.
            if unconverted_amount is None:
                break

            contract_amount = _get_amount(contract, no_conversion, unconverted_amount, currency, date)
            # (2,5) Amount is zero or unconvertable.
            if contract_amount is None or contract_amount == 0:
                break

            # (4) Different signs.
            if (contract_amount > 0 and award_amount < 0) or (contract_amount < 0 and award_amount > 0):
                break

            contracts_amount_sum += contract_amount
        else:
            ratio = abs(award_amount - contracts_amount_sum) / abs(award_amount)
            passed = ratio <= 0.5

            application_count += 1
            if passed:
                pass_count += 1

            if result["meta"] is None:
                result["meta"] = {"awards": []}

            result["meta"]["awards"].append(
                {"awardID": award["id"], "awards.value": award["value"], "contracts.value_sum": contracts_amount_sum}
            )

    return complete_result_resource(result, application_count, pass_count, reason="insufficient data for check")
