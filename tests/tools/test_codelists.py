import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pytest

# Avoid test_fixtures.py validating CODELIST_URLS as OCDS data, by importing the module.
from pelican.util import codelists
from pelican.util.codelists import (
    _remote,
    get_document_type_section_mapping,
    get_identifier_scheme_codelist,
    get_language_codelist,
    get_media_type_codelist,
    get_ocid_prefix_codelist,
)

CACHED = (_remote, get_identifier_scheme_codelist, get_ocid_prefix_codelist)


@pytest.fixture
def clear_caches():
    """
    Clear the caches, so that a warm cache doesn't reduce the number of requests, and so that other tests
    (like tests/field/checks/test_ocid.py) don't read the empty codelists from the mocked responses.
    """
    for func in CACHED:
        func.cache_clear()
    yield
    for func in CACHED:
        func.cache_clear()


@pytest.mark.usefixtures("clear_caches")
@patch("requests.Session.get")
@pytest.mark.parametrize(
    ("func", "requests_made"),
    [
        (get_document_type_section_mapping, 0),
        (get_language_codelist, 0),
        (get_media_type_codelist, 0),
        (get_identifier_scheme_codelist, 1),
        (get_ocid_prefix_codelist, 1),
    ],
)
def test_get(get, func, requests_made):
    get.return_value = MagicMock(text="")

    for _ in range(10):
        func()

    assert get.call_count == requests_made


@pytest.mark.usefixtures("clear_caches")
@patch("requests.Session.get")
@pytest.mark.parametrize("func", [get_identifier_scheme_codelist, get_ocid_prefix_codelist])
def test_get_concurrently(get, func):
    def slow_get(*args, **kwargs):
        time.sleep(0.1)  # long enough for every thread to miss the cache
        return MagicMock(text="")

    get.side_effect = slow_get

    with ThreadPoolExecutor(max_workers=8) as executor:
        # map() calls the function concurrently, passing each number as an argument, which func() doesn't accept.
        list(executor.map(lambda _: func(), range(8)))

    assert get.call_count == 1


@pytest.mark.parametrize(("name", "url"), codelists.CODELIST_URLS.items())
def test_up_to_date(name, url):
    response = codelists.session.get(url, timeout=10)
    response.raise_for_status()

    assert (codelists.CODELIST_DIR / name).read_bytes() == response.content, (
        f"{name} is out of date. Run: ./manage.py dev updatecodelists"
    )
