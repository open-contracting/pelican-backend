from pelican.util.checks import field_quality_check
from pelican.util.codelists import get_document_type_section_mapping

name = "document_type"


def test(value, section):
    mapping = get_document_type_section_mapping()

    # Inclusion tests for coherence.
    return value not in mapping or section in mapping[value], f"not expected in {section} section"


calculate_section = field_quality_check(name, test)
