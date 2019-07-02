def get_value(item, path, simplify=False):
    # return whole item from root
    if not path or path == [""]:
        return item

    # return the value for key in the item
    if type(path) is str and path in item:
        return item[path]

    # last item in the path - return the key value
    if len(path) == 1 and path[0] in item:
        return item[path[0]]

    # get new key identifying the new item
    key = path[0]

    if key in item:
        # inner value is a dictionary { "key": {"aaa": "bbb"}}
        # lets go deeper
        if type(item[key]) is dict:
            return get_value(item[key], path[1:], simplify)

        # inner value is an aarray { "key" : [{"aaa":"bbb"}, {"ccc": "ddd"}]}
        # iterate over the items and read the rest of the path from the
        if type(item[key]) is list:
            values = []
            for list_item in item[key]:
                result = get_value(list_item, path[1:], simplify)

                if type(result) is not list:
                    values.append(result)
                else:
                    if simplify:
                        # simplify, flatten the result
                        values = values + result
                    else:
                        values.append(result)

            return values

        # "primitive" value, return it
        if key in item:
            return item[key]

    # nothing found
    return None
