from tools.checks import get_empty_result_resource
from tools.getter import get_values

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    tender_status = get_values(item, "tender.status")

    if not tender_status:
        # completely missing tender value
        result["result"] = None
        result["meta"] = {"reason": "incomplete data for check"}
        return result

    tender_status = tender_status[0]["value"]

    if tender_status in ("planning", "planned", "active", "cancelled", "unsuccessful", "withdrawn"):
        contracts = get_values(item, "contracts")
        awards = get_values(item, "awards")

        contracts_count = 0
        if contracts:
            for contract in contracts:
                if contract["value"]:
                    contracts_count = contracts_count + 1

        awards_count = 0
        if awards:
            for award in awards:
                if award["value"]:
                    awards_count = awards_count + 1

        if contracts_count > 0 or awards_count > 0:
            result["result"] = False
            result["application_count"] = 1
            result["pass_count"] = 0
            result["meta"] = {"contracts_count": contracts_count, "awards_count": awards_count}
            return result

        result["result"] = True
        result["application_count"] = 1
        result["pass_count"] = 1
        result["meta"] = None

        return result

    # unable to compare, undefined
    result["result"] = None
    result["meta"] = {"reason": "non-evaulated tender status"}
    return result
