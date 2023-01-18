from tools import settings


def is_step_required(*steps: str) -> bool:
    return any(step in settings.STEPS for step in steps)
