import datetime
import re
from typing import Any

from dateutil.parser import isoparse

from pelican.util.currency_converter import convert

regex = re.compile(r"^([^[]*)\[([\d]*)\]$")


def get_amount(no_conversion, amount, currency, date):
    if no_conversion:
        return amount
    if date is not None:
        return convert(amount, currency, "USD", date)
    return None


# https://datatracker.ietf.org/doc/html/rfc3339#section-5.6
def parse_datetime(string: str | None) -> datetime.datetime | None:
    """
    Parse a string to a datetime.

    :param string: the value to parse
    """
    if string is None or not isinstance(string, str):
        return None
    try:
        return isoparse(string)
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return None


def parse_date(string: str | None) -> datetime.date | None:
    """
    Parse a string to a date.

    :param string: the value to parse
    """
    if not string or not isinstance(string, str):
        return None
    try:
        return isoparse(string[:10]).date()
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(string[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def deep_has(value: Any, path: str) -> bool:
    """
    Return whether a nested value exists in nested dicts, safely.

    Use this instead of :func:`deep_get` to check for the presence of a key. For example,
    ``deep_get({"id": 0}, "id")`` is falsy.

    :param value: the value to index into
    :param path: a period-separated list of keys
    """
    for part in path.split("."):
        if type(value) is dict and part in value:
            value = value[part]
        else:
            return False

    return True


def deep_get(value: Any, path: str, force: type[Any] | None = None) -> Any:
    """
    Get a nested value from nested dicts, safely.

    If ``force`` is provided and the nested value is not of that type, then if ``force`` is ...

    -  ``datetime.date``, ``datetime.datetime``: Parse the nested value as ISO 8601. On failure, return ``None``.
    -  ``dict``, ``list``: Return an empty ``dict`` or ``list``, respectively.
    -  ``float``, ``int``, ``str``: Cast the nested value to that type. On failure, return ``None``.

    If the nested value is not set, if ``force`` is provided, and ``force`` is ``dict``, ``list`` or ``str``, return an
    empty ``dict``, ``list`` or ``str``, respectively. Otherwise, if the nested value is not set, return ``None``.

    :param value: the value to index into
    :param path: a period-separated list of keys
    :param force: the type to which to coerce the nested value, if possible
    """
    for part in path.split("."):
        if type(value) is dict and part in value:
            value = value[part]
        elif force in {dict, list, str}:
            return force()
        else:
            return None

    if force and type(value) is not force:
        if force is datetime.date:
            return parse_date(value)
        if force is datetime.datetime:
            return parse_datetime(value)
        if force in {dict, list}:
            value = force()
        elif force in {float, int, str}:
            try:
                value = force(value)
            except (ValueError, TypeError):
                return None
        else:
            raise NotImplementedError

    return value


def get_values(item: Any, str_path: str, *, value_only: bool | None = False) -> list[Any]:
    index: int | None

    if item is None:
        return []

    # return whole item from root
    if not str_path or str_path == "":
        if value_only:
            return [item]
        return [{"path": str_path, "value": item}]

    # return the value for key in the item
    if "." not in str_path and str_path in item:
        if type(item[str_path]) is list:
            values = []
            for index in range(len(item[str_path])):
                if value_only:
                    values.append(item[str_path][index])
                else:
                    values.append({"path": f"{str_path}[{index}]", "value": item[str_path][index]})

            return values
        if value_only:
            return [item[str_path]]
        return [{"path": str_path, "value": item[str_path]}]

    # indexing used
    field = None
    index = None
    groups = regex.findall(str_path)
    if len(groups) == 1:
        try:
            field = groups[0][0]
            index = int(groups[0][1])
        except (IndexError, TypeError, ValueError):
            pass

    if (
        field is not None
        and index is not None
        and field in item
        and type(item[field]) is list
        and len(item[field]) > index
    ):
        return [item[field][index]] if value_only else [{"path": f"{field}[{index}]", "value": item[field][index]}]

    # get new key identifying the new item
    path = str_path.split(".")
    key = path[0]

    if key in item:
        # inner value is a dictionary { "key": {"aaa": "bbb"}}
        # lets go deeper
        if type(item[key]) is dict:
            result = get_values(item[key], ".".join(path[1:]), value_only=value_only)

            if not result:
                return []

            values = []
            if type(result) is not list:
                values.append(result)
            else:
                values = result

            for value in values:
                if not value_only and value and "path" in value:
                    value["path"] = f"{key}.{value['path']}"
            return values

        # inner value is an array { "key" : [{"aaa":"bbb"}, {"ccc": "ddd"}]}
        # iterate over the items and read the rest of the path from the
        if type(item[key]) is list:
            result = []
            for index, list_item in enumerate(item[key]):
                values = get_values(list_item, ".".join(path[1:]), value_only=value_only)

                for value in values:
                    if value_only:
                        result.append(value)
                    elif value and "path" in value:
                        value["path"] = f"{key}[{index}].{value['path']}"
                        result.append(value)

            return result

        # "primitive" value, return it
        if key in item:
            if key != path[-1]:
                return []
            if value_only:
                return [item[key]]
            return [{"path": key, "value": item[key]}]

    # indexing used
    field = None
    index = None
    groups = regex.findall(key)
    if len(groups) == 1:
        try:
            field = groups[0][0]
            index = int(groups[0][1])
        except (IndexError, TypeError, ValueError):
            pass

    if (
        field is not None
        and index is not None
        and field in item
        and type(item[field]) is list
        and len(item[field]) > index
    ):
        result = []

        values = get_values(item[field][index], ".".join(path[1:]), value_only=value_only)

        for value in values:
            if value_only:
                result.append(value)
            elif value and "path" in value:
                value["path"] = f"{field}[{index}].{value['path']}"
                result.append(value)

        return result

    # nothing found
    return []
