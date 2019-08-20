
max_length = 250


def description_length(data, key):
    length = len(data[key])

    if length <= max_length:
        return {'result': True}
    else:
        return {
            'result': False,
            'value': length,
            'reason': 'description exceeds max length of {} characters'.format(max_length)
        }
