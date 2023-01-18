from tools.checks import complete_result_resource, get_empty_result_resource
from tools.currency_converter import convert
from tools.getter import parse_datetime

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    contracts = item["contracts"] if "contracts" in item else None
    if not contracts:
        result["meta"] = {"reason": "there are no contracts"}
        return result

    awards = item["awards"] if "awards" in item else None
    if not awards:
        result["meta"] = {"reason": "there are no awards"}
        return result

    application_count = 0
    pass_count = 0
    non_applicable_award_ids = set()
    for contract in contracts:
        matching_awards = [
            a for a in awards if "awardID" in contract and "id" in a and str(contract["awardID"]) == str(a["id"])
        ]

        # matching award can be only one
        if len(matching_awards) != 1:
            non_applicable_award_ids.update([str(a["id"]) for a in matching_awards])
            continue

        matching_award = matching_awards[0]

        # checking whether amount or currency fields are set
        if (
            "value" not in contract
            or "value" not in matching_award
            or "currency" not in contract["value"]
            or "amount" not in contract["value"]
            or "currency" not in matching_award["value"]
            or "amount" not in matching_award["value"]
            or contract["value"]["currency"] is None
            or contract["value"]["amount"] is None
            or matching_award["value"]["currency"] is None
            or matching_award["value"]["amount"] is None
        ):
            non_applicable_award_ids.add(str(matching_award["id"]))
            continue

        # converting values if necessary
        contract_value_amount = None
        award_value_amount = None
        if contract["value"]["currency"] == matching_award["value"]["currency"]:
            contract_value_amount = contract["value"]["amount"]
            award_value_amount = matching_award["value"]["amount"]
        else:
            contract_value_amount = convert(
                contract["value"]["amount"], contract["value"]["currency"], "USD", parse_datetime(item["date"])
            )
            award_value_amount = convert(
                matching_award["value"]["amount"],
                matching_award["value"]["currency"],
                "USD",
                parse_datetime(item["date"]),
            )

        # checking for non-convertible values
        if contract_value_amount is None or award_value_amount is None:
            non_applicable_award_ids.add(str(matching_award["id"]))
            continue

        # amount is equal to zero
        if contract_value_amount == 0 or award_value_amount == 0:
            non_applicable_award_ids.add(str(matching_award["id"]))
            continue

        # different signs
        if (contract_value_amount > 0 and award_value_amount < 0) or (
            contract_value_amount < 0 and award_value_amount > 0
        ):
            non_applicable_award_ids.add(str(matching_award["id"]))
            continue

    for award in awards:
        if "id" not in award or str(award["id"]) in non_applicable_award_ids:
            continue

        matching_contracts = [
            c for c in contracts if "awardID" in c and "id" in award and str(c["awardID"]) == str(award["id"])
        ]

        # no matching contracts
        if not matching_contracts:
            continue

        award_value_amount = None
        contracts_value_amount_sum = None
        if all([award["value"]["currency"] == c["value"]["currency"] for c in matching_contracts]):
            award_value_amount = award["value"]["amount"]
            contracts_value_amount_sum = sum([c["value"]["amount"] for c in matching_contracts])
        else:
            award_value_amount = convert(
                award["value"]["amount"], award["value"]["currency"], "USD", parse_datetime(item["date"])
            )
            contracts_value_amount_sum = sum(
                [
                    convert(c["value"]["amount"], c["value"]["currency"], "USD", parse_datetime(item["date"]))
                    for c in matching_contracts
                ]
            )

        ratio = abs(award_value_amount - contracts_value_amount_sum) / abs(award_value_amount)
        passed = ratio <= 0.5

        application_count += 1
        if passed:
            pass_count += 1

        if result["meta"] is None:
            result["meta"] = {"awards": []}

        result["meta"]["awards"].append(
            {"awardID": award["id"], "awards.value": award["value"], "contracts.value_sum": contracts_value_amount_sum}
        )

    return complete_result_resource(result, application_count, pass_count, reason="insufficient data for check")
