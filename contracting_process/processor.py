import sys
import time

from contracting_process.definitions import definitions


def do_work(item):
    print(item)

    for path, value in definitions.items():
        path = path.split(".")
        print(get_value(item, path))
        print("----------")

    sys.exit()
    return


def get_value(item, path):

    if type(path) is str:
        return item[path]
    if len(path) == 1:
        return item[path[0]]

    key = path[0]

    if key in item:
        if type(item[key]) is dict:
            return get_value(item[key], path[1:])
        if type(item[key]) is list:
            values = []
            for list_item in item[key]:
                values.append(get_value(list_item, path[1]))
            return values

        return item[key]

    return None
