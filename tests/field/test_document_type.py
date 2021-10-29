from contracting_process.field_level.checks import document_type
from tests import is_subset_dict


def test_passed():
    document_type.code_to_section_mapping = {"contractGuarantees": ["tender", "contract"]}

    result = document_type.calculate_section({"documentType": "contractGuarantees"}, "documentType", "tender")
    assert is_subset_dict({"result": True}, result)
    result = document_type.calculate_section({"documentType": "unknown"}, "documentType", "tender")
    assert is_subset_dict({"result": True}, result)


def test_failed():
    document_type.code_to_section_mapping = {"contractGuarantees": ["tender", "contract"]}

    result = document_type.calculate_section({"documentType": "contractGuarantees"}, "documentType", "planning")
    assert is_subset_dict(
        {
            "result": False,
            "value": "contractGuarantees",
            "reason": "unsupported combination code-section for documentType",
        },
        result,
    )
