data = {}
count = 0


def add_item(item):
    global count
    count = count + 1


def get_result():
    global count
    return count
