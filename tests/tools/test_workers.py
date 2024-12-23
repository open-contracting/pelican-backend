import pytest

from pelican.util import settings
from pelican.util.workers import is_step_required
from tests import OverrideSettings


@pytest.mark.parametrize(
    ("steps", "values", "expected"),
    [
        ([settings.Steps.FIELD_COVERAGE], (settings.Steps.FIELD_COVERAGE,), True),
        ([settings.Steps.FIELD_COVERAGE], (settings.Steps.FIELD_QUALITY,), False),
        ([settings.Steps.FIELD_COVERAGE], (settings.Steps.FIELD_COVERAGE, settings.Steps.FIELD_QUALITY), True),
    ],
)
def test_is_step_required(steps, values, expected):
    with OverrideSettings(STEPS=steps):
        assert is_step_required(*values) is expected
