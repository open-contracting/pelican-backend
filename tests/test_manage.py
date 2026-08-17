from manage import CHECKS_PAGE, markdown_page


def test_updatedocs():
    assert CHECKS_PAGE.read_text() == markdown_page(), "Run: ./manage.py dev updatedocs"
