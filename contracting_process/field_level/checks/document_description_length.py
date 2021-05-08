from tools.checks import get_empty_result_field

max_length = 250
name = "document_description_length"


def calculate(data, key):
    result = get_empty_result_field(name)

    length = len(data[key])
    if length <= max_length:
        result["result"] = True
        return result

    result["result"] = False
    result["value"] = length
    result["reason"] = "description exceeds max length of {} characters".format(max_length)
    return result
