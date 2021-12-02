import random
import re
from datetime import date, datetime
from typing import Any, List, Optional

from yapw.methods.blocking import ack, publish

from tools import settings
from tools.services import commit
from tools.state import set_dataset_state, state


def parse_datetime(str_datetime: Optional[str]) -> Optional[datetime]:
    """
    the following are valid dates according to ocds:

    ‘2014-10-21T09:30:00Z’ - 9:30 am on the 21st October 2014, UTC
    ‘2014-11-18T18:00:00-06:00’ - 6pm on 18th November 2014 CST (Central Standard Time)
    """
    if str_datetime is None or not isinstance(str_datetime, str):
        return None

    # limit to microseconds
    str_datetime = re.sub(r"(?<=T\d\d:\d\d:\d\d\.)(\d+)", lambda m: m.group(1)[:6], str_datetime)

    str_datetime = str_datetime.replace("Z", "+00:00")

    try:
        return datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass

    try:
        return datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        pass

    if len(str_datetime) < 25:
        return None

    str_timezone = str_datetime[-6:].replace(":", "")
    str_datetime = str_datetime[:-6] + str_timezone

    try:
        return datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass

    try:
        return datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        pass


def parse_date(str_date: Optional[str]) -> Optional[date]:
    """
    Parse string to valid date.
    """
    if str_date is None or not isinstance(str_date, str):
        return None

    try:
        return datetime.strptime(str_date[:10], "%Y-%m-%d").date()
    except ValueError:
        pass


class ReservoirSampler:
    def __init__(self, samples_cap: int):
        if samples_cap < 1:
            raise ValueError("samples_cap must be a positive integer")

        self._samples_cap = samples_cap
        self._samples = []  # type: list
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
