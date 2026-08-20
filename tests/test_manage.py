from pathlib import Path

import pytest

from manage import CHECKS_PAGES, markdown_page

DIRECTORY = Path(__file__).resolve().parents[1] / "docs" / "checks"


@pytest.mark.parametrize(("locale", "page"), CHECKS_PAGES.items())
def test_updatedocs(locale, page):
    assert (DIRECTORY / f"{locale}.md").read_text() == markdown_page(locale, page), "Run: ./manage.py dev updatedocs"
