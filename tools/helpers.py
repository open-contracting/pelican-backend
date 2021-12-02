import random
from datetime import date, datetime
from typing import Any, List, Optional

from dateutil.parser import isoparse
from yapw.methods.blocking import ack, publish

from tools import settings
from tools.services import commit
from tools.state import set_dataset_state, state


# https://datatracker.ietf.org/doc/html/rfc3339#section-5.6
def parse_datetime(string: Optional[str]) -> Optional[datetime]:
    """
    Parse a string to a datetime.
    """
    if string is None or not isinstance(string, str):
        return None
    try:
        return isoparse(string)
    except ValueError:
        pass
    try:
        return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass


def parse_date(string: Optional[str]) -> Optional[date]:
    """
    Parse a string to a date.
    """
    if not string or not isinstance(string, str):
        return None
    try:
        return isoparse(string[:10]).date()
    except ValueError:
        pass
    try:
        return datetime.strptime(string[:10], "%Y-%m-%d").date()
    except ValueError:
        pass


class ReservoirSampler:
    def __init__(self, samples_cap: int):
        if samples_cap < 1:
            raise ValueError("samples_cap must be a positive integer")

        self._samples_cap = samples_cap
        self._samples = []  # type: List[Any]
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


def finish_worker(
    client_state, channel, method, dataset_id: int, phase: str, routing_key: Optional[str] = None
) -> None:
    """
    Update the dataset's state, publish a message if a routing key is provided, and ack the message.
    """
    set_dataset_state(dataset_id, state.OK, phase)
    commit()
    if routing_key:
        publish(client_state, channel, {"dataset_id": dataset_id}, routing_key)
    ack(client_state, channel, method.delivery_tag)
