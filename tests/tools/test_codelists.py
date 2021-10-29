from unittest.mock import MagicMock, patch

import pytest

from tools.codelists import get_document_format_codelist, get_identifier_scheme_codelist, get_ocid_prefix_codelist


@patch("requests.get")
@pytest.mark.parametrize(
    "func", [get_document_format_codelist, get_identifier_scheme_codelist, get_ocid_prefix_codelist]
)
def test_get(get, func):
    get.return_value = MagicMock()
    get.return_value.text = ""

    func()
    func()
    func()

    assert len(get.mock_calls) <= 1
