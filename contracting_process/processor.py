import sys
import time
from contracting_process.definitions import definitions
from tools.getter import get_value


def do_work(item):
    print(item)

    for path, plugins in definitions.items():
        path = path.split(".")
        value = get_value(item, path)
        for plugin in plugins:
            plugin(value)
    
    return
