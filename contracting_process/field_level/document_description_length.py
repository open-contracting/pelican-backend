
max_length = 250


def description_length(data, key):
    if len(data[key]) <= max_length:
        return {'result': True}
    else:
        return {
            'result': False,
            'value': data[key],
            'reason': 'description exceeds max length of {} characters'.format(max_length)
        }
