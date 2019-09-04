
from contracting_process.field_level.checks.document_type import calculate_section
from tools.helpers import is_subset_dict


def test_passed():
    result = calculate_section(
        {'documentType': 'physicalProgressReport'},
        'documentType',
        'implementation'
    )
    assert is_subset_dict(
        {'result': True},
        result
    )


def test_failed():
    result = calculate_section(
        {'documentType': 'unknown'},
        'documentType',
        'contract'
    )
    assert is_subset_dict(
        {
            'result': False,
            'value': 'unknown',
            'reason': 'unknown documentType code'
        },
        result
    )

    result = calculate_section(
        {'documentType': 'contractNotice'},
        'documentType',
        'award'
    )
    assert is_subset_dict(
        {
            'result': False,
            'value': 'contractNotice',
            'reason': 'unsupported combination code-section for documentType'
        },
        result
    )
