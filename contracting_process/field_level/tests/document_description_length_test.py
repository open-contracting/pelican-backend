
from contracting_process.field_level.document_description_length import description_length


def test_passed():
    result = description_length({'description': 'short'}, 'description')
    assert result == {'result': True}

    result = description_length({'description': ''.join('_' for _ in range(0, 250))}, 'description')
    assert result == {'result': True}


def test_failed():
    data = {'description': ''.join('_' for _ in range(0, 251))}
    result = description_length(data, 'description')
    assert result == {
        'result': False,
        'value': data['description'],
        'reason': 'description exceeds max length of 250 characters'
    }
