"""
For each contract, the sum of its transaction's values is less than or equal to the contract's value, after conversion
to USD if necessary.

Since the test operates on all contract and transaction objects, the test silently ignores any missing or non-numeric
amounts and any missing or unknown currencies. If currency conversion is necessary, but the release date is invalid,
before 1999, or in the future, the test silently ignores the contract and its transactions.
"""

import datetime

from pelican.util.checks import complete_result_resource, get_empty_result_resource
from pelican.util.getter import deep_get, get_amount, get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    contracts = get_values(item, "contracts")
    if not contracts:
        result["meta"] = {"reason": "no contract is set"}
        return result

    date = deep_get(item, "date", datetime.datetime)

    application_count = 0
    pass_count = 0
    failed_paths = []
    for contract in contracts:
        transactions = get_values(contract["value"], "implementation.transactions", value_only=True)
        if not transactions:
            continue

        currency = deep_get(contract["value"], "value.currency")

        currencies = {currency} | {deep_get(transaction, "value.currency") for transaction in transactions}
        no_conversion = len(currencies) == 1
        # Currency is missing.
        if None in currencies:
            continue

        unconverted_amount = deep_get(contract["value"], "value.amount", float)
        # Amount is missing or non-numeric.
        if unconverted_amount is None:
            continue

        contract_amount = get_amount(no_conversion, unconverted_amount, currency, date)
        # Amount is unconvertable.
        if contract_amount is None:
            continue

        transactions_amount_sum = 0
        for transaction in transactions:
            currency = deep_get(transaction, "value.currency")

            unconverted_amount = deep_get(transaction, "value.amount", float)
            # Amount is missing or non-numeric.
            if unconverted_amount is None:
                break

            transaction_amount = get_amount(no_conversion, unconverted_amount, currency, date)
            # Amount is unconvertable.
            if transaction_amount is None:
                break

            transactions_amount_sum += transaction_amount
        else:
            passed = transactions_amount_sum <= contract_amount

            application_count += 1
            if passed:
                pass_count += 1
            else:
                failed_paths.append(
                    {
                        "path": contract["path"],
                        "contract_amount": contract_amount,
                        "transactions_amount_sum": transactions_amount_sum,
                        "currency": currencies.pop() if no_conversion else "USD",
                    }
                )

    return complete_result_resource(
        result, application_count, pass_count, reason="no numeric, convertable amounts", failed_paths=failed_paths
    )
