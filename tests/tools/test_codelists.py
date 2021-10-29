from unittest.mock import MagicMock, patch

import pytest

from tools.codelists import (
    get_document_type_section_mapping,
    get_identifier_scheme_codelist,
    get_language_codelist,
    get_media_type_codelist,
    get_ocid_prefix_codelist,
)


@patch("requests.get")
@pytest.mark.parametrize(
    "func",
    [
        get_document_type_section_mapping,
        get_identifier_scheme_codelist,
        get_language_codelist,
        get_media_type_codelist,
        get_ocid_prefix_codelist,
    ],
)
def test_get(get, func):
    get.return_value = MagicMock()
    get.return_value.text = ""

    for i in range(10):
        func()

    assert len(get.mock_calls) <= 1
