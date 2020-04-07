
import contracting_process.field_level.checks.identifier_scheme as identifier_scheme
from tools.helpers import is_subset_dict


def test_passed():
    identifier_scheme.identifier_scheme_codelist = ['a']

    assert is_subset_dict(
        {'result': True},
        identifier_scheme.calculate({'scheme': 'a'}, 'scheme')
    )


def test_failed():
    identifier_scheme.identifier_scheme_codelist = ['a']

    assert is_subset_dict(
        {
            'result': False,
            'value': 'b',
            'reason': 'wrong identifier scheme'
        },
        identifier_scheme.calculate({'scheme': 'b'}, 'scheme')
    )
    assert is_subset_dict(
        {
            'result': False,
            'value': None,
            'reason': 'wrong identifier scheme'
        },
        identifier_scheme.calculate({'scheme': None}, 'scheme')
    )
