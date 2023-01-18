import random
from typing import Any, List, Optional

from yapw.methods.blocking import ack, publish

from tools import settings
from tools.services import commit
from tools.state import set_dataset_state, state


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


# Has affinity with services.py, but would result in circular dependency due to `set_dataset_state()`.
def finish_callback(
    client_state, channel, method, dataset_id: int, phase: Optional[str] = None, routing_key: Optional[str] = None
) -> None:
    """
    Update the dataset's state, publish a message if a routing key is provided, and ack the message.
    """
    if phase:
        set_dataset_state(dataset_id, state.OK, phase)
    commit()
    if routing_key:
        publish(client_state, channel, {"dataset_id": dataset_id}, routing_key)
    ack(client_state, channel, method.delivery_tag)
