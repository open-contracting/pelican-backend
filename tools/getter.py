import re

regex = r"^([^[]*)\[([\d]*)\]$"


def deep_has(value, path):
    """
    Returns whether a nested value exists in nested dicts, safely.

    Use this instead of :func:`deep_get` to check for the presence of a key. For example,
    ``deep_get({"id": 0}, "id")`` is falsy.
    """
    for part in path.split("."):
        if type(value) is dict and part in value:
            value = value[part]
        else:
            return False

    return True


def deep_get(value, path, default=None):
    """
    Gets a nested value from nested dicts, safely. If a default value is provided and the nested value is not of the
    same type as the default value, returns the default value.

    :param value: the value
    :param str path: a period-separated list of keys
    :param default: a default value, if the nested value doesn't exist
    """
    for part in path.split("."):
        if type(value) is dict and part in value:
            value = value[part]
        else:
            return default

    if default is not None and type(value) is not type(default):
        return default

    return value


def get_values(item, str_path, value_only=False):
    # return whole item from root
    if not str_path or str_path == "":
        if value_only:
            return [item]
        else:
            return [{"path": str_path, "value": item}]

    # return the value for key in the item
    if "." not in str_path and str_path in item:
        if type(item[str_path]) is list:
            values = []
            for index in range(len(item[str_path])):
                if value_only:
                    values.append(item[str_path][index])
                else:
                    values.append({"path": "{}[{}]".format(str_path, index), "value": item[str_path][index]})

            return values
        else:
            if value_only:
                return [item[str_path]]
            else:
                return [{"path": str_path, "value": item[str_path]}]

    # indexing used
    field = None
    index = None
    groups = re.findall(regex, str_path)
    if len(groups) == 1:
        try:
            field = groups[0][0]
            index = int(groups[0][1])
        except (IndexError, TypeError, ValueError):
            pass

    if field is not None and index is not None and field in item:
        if type(item[field]) is list and len(item[field]) > index:
            if value_only:
                values = [item[field][index]]
            else:
                values = [{"path": "{}[{}]".format(field, index), "value": item[field][index]}]

            return values

    # get new key identifying the new item
    path = str_path.split(".")
    key = path[0]

    if key in item:
        # inner value is a dictionary { "key": {"aaa": "bbb"}}
        # lets go deeper
        if type(item[key]) is dict:
            result = get_values(item[key], ".".join(path[1:]), value_only=value_only)

            if not result:
                return []

            values = []
            if type(result) is not list:
                values.append(result)
            else:
                values = result

            for list_item in values:
                if not value_only and list_item and "path" in list_item:
                    list_item["path"] = "{}.{}".format(key, list_item["path"])
            return values

        # inner value is an array { "key" : [{"aaa":"bbb"}, {"ccc": "ddd"}]}
        # iterate over the items and read the rest of the path from the
        if type(item[key]) is list:
            index_counter = 0
            result = []
            for list_item in item[key]:
                values = get_values(list_item, ".".join(path[1:]), value_only=value_only)

                if values:
                    for list_item in values:
                        if value_only:
                            result.append(list_item)
                        else:
                            if list_item and "path" in list_item:
                                list_item["path"] = "{}[{}].{}".format(key, index_counter, list_item["path"])

                                result.append(list_item)

                index_counter += 1

            return result

        # "primitive" value, return it
        if key in item:
            if value_only:
                return [item[key]]
            else:
                return [{"path": key, "value": item[key]}]

    # indexing used
    field = None
    index = None
    groups = re.findall(regex, key)
    if len(groups) == 1:
        try:
            field = groups[0][0]
            index = int(groups[0][1])
        except (IndexError, TypeError, ValueError):
            pass

    if field is not None and index is not None and field in item:
        if type(item[field]) is list and len(item[field]) > index:
            result = []

            values = get_values(item[field][index], ".".join(path[1:]), value_only=value_only)

            if values:
                for list_item in values:
                    if value_only:
                        result.append(list_item)
                    else:
                        if list_item and "path" in list_item:
                            list_item["path"] = "{}[{}].{}".format(field, index, list_item["path"])

                            result.append(list_item)

            return result

    # nothing found
    return []
