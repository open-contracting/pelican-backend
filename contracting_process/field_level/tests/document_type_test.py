
from contracting_process.field_level.document_type import document_type_coherent


def test_passed():
    result = document_type_coherent(
        {'documentType': 'physicalProgressReport'},
        'documentType',
        'implementation'
    )
    assert result == {'result': True}


def test_failed():
    result = document_type_coherent(
        {'documentType': 'unknown'},
        'documentType',
        'contract'
    )
    assert result == {
        'result': False,
        'value': 'unknown',
        'reason': 'unknown documentType code'
    }

    result = document_type_coherent(
        {'documentType': 'contractNotice'},
        'documentType',
        'award'
    )
    assert result == {
        'result': False,
        'value': 'contractNotice',
        'reason': 'unsupported combination code-section for documentType'
    }
