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
                    values.append(
                        {
                            "path": "{}[{}]".format(str_path, index),
                            "value": item[str_path][index]
                        }
                    )

            return values
        else:
            if value_only:
                return [item[str_path]]
            else:
                return [{"path": str_path, "value": item[str_path]}]

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
                            if list_item is not None:
                                result.append(list_item)
                        else:
                            if list_item and "path" in list_item:
                                list_item["path"] = "{}[{}].{}".format(key, index_counter, list_item["path"])

                                result.append(list_item)

                index_counter = index_counter + 1

            return result

        # "primitive" value, return it
        if key in item:
            if value_only:
                return [item[key]]
            else:
                return [{"path": key, "value": item[key]}]

    # nothing found
    return []
