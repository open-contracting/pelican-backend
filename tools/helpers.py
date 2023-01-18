import random
from typing import Any, List

from tools import settings


class ReservoirSampler:
    def __init__(self, samples_cap: int):
        if samples_cap < 1:
            raise ValueError("samples_cap must be a positive integer")

        self._samples_cap = samples_cap
        self._samples: List[Any] = []
        self._index = 0

    def process(self, value: Any) -> None:
        if self._index < self._samples_cap:
            self._samples.append(value)
        else:
            r = random.randint(0, self._index)
            if r < self._samples_cap:
                self._samples[r] = value

        self._index += 1

    def retrieve_samples(self) -> List[Any]:
        return self._samples


def is_step_required(*steps: str) -> bool:
    return any(step in settings.STEPS for step in steps)
