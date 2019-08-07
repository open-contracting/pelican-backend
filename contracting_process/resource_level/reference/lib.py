from tools.checks import get_empty_result_resource
from tools.getter import get_values


def calculate_reference_in_parties(item, values, version):
    result = get_empty_result_resource(version)

    if not values:
        result["meta"] = {"reason": "no values available"}
        return result

    application_count = 0
    pass_count = 0

    # get all ids from partied array
    parties_ids = []
    if "parties" in item:
        for party in item["parties"]:
            if "id" in party and party["id"]:
                parties_ids.append(party["id"])

    failed_paths = []
    for value in values:
        if value["value"]:
                application_count = application_count + 1

                current_path = value["path"]

                if "parties" not in item or not item["parties"]:
                    failed_paths.append(current_path)
                    continue
                if "id" not in value["value"]:
                    failed_paths.append(current_path)
                    continue
                if value["value"]["id"] not in parties_ids:
                    failed_paths.append(current_path)
                    continue

                pass_count = pass_count + 1

    if application_count > 0:
        if application_count == pass_count:
            result["result"] = True
            result["meta"] = {}
        else:
            result["result"] = False
            result["meta"] = {"failed_paths": failed_paths}

        result["application_count"] = application_count
        result["pass_count"] = pass_count
        return result
    else:
        result["result"] = None
        result["meta"] = {"reason": "missing data"}
        return result
