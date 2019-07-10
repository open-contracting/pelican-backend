def get_values(item, str_path):
    # return whole item from root
    if not str_path or str_path == "":
        return [{"path": str_path, "value": item}]

    # return the value for key in the item
    if "." not in str_path and str_path in item:
        return [{"path": str_path, "value": item[str_path]}]

    # get new key identifying the new item
    path = str_path.split(".")
    key = path[0]

    if key in item:
        # inner value is a dictionary { "key": {"aaa": "bbb"}}
        # lets go deeper
        if type(item[key]) is dict:
            result = get_values(item[key], ".".join(path[1:]))

            values = []
            if type(result) is not list:
                values.append(result)
            else:
                values = result

            for list_item in values:
                list_item["path"] = "{}.{}".format(key, item["path"])
            return values

        # inner value is an array { "key" : [{"aaa":"bbb"}, {"ccc": "ddd"}]}
        # iterate over the items and read the rest of the path from the
        if type(item[key]) is list:
            index_counter = 0
            result = []
            for list_item in item[key]:
                values = get_values(list_item, ".".join(path[1:]))

                if values:
                    for item in values:
                        item["path"] = "{}[{}].{}".format(key, index_counter, item["path"])

                        result.append(item)

                index_counter = index_counter + 1

            return result

        # "primitive" value, return it
        if key in item:
            return [{"path": key, "value": item[key]}]

    # nothing found
    return None
