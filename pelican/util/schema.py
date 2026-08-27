import functools
from pathlib import Path
from typing import Any, NamedTuple

import jsonref


class Field(NamedTuple):
    """
    A field in the release schema.

    ``refs`` is the chain of definitions containing the field, outermost first, ending with ``ref`` if it is set.
    ``ref`` is set only if the field is itself a reference.
    """

    path: tuple[str, ...]
    refs: tuple[str, ...]
    ref: str | None
    deprecated: bool
    schema: dict[str, Any]

    @property
    def dot_path(self) -> str:
        return ".".join(self.path)


def _walk(properties, path=(), refs=(), *, deprecated=False):
    for key, value in properties.items():
        new_path = (*path, key)
        new_deprecated = deprecated or "deprecated" in value

        if "properties" in value:
            subschema = value
        elif "properties" in value.get("items", {}):
            subschema = value["items"]
        else:
            yield Field(new_path, refs, None, new_deprecated, value)
            continue

        ref = None
        if hasattr(subschema, "__reference__"):
            ref = subschema.__reference__["$ref"].removeprefix("#/definitions/")
        new_refs = (*refs, ref) if ref else refs

        yield Field(new_path, new_refs, ref, new_deprecated, value)
        yield from _walk(subschema["properties"], new_path, new_refs, deprecated=new_deprecated)


# merge_props retains a reference's sibling keywords, notably "deprecated".
with (Path(__file__).resolve().parents[1] / "static" / "release-schema.json").open() as f:
    _schema = jsonref.load(f, merge_props=True)

# Every field in the release schema, in schema order, parents before children.
fields = tuple(_walk(_schema["properties"]))


@functools.cache
def get_paths(definition: str) -> tuple[str, ...]:
    """
    Return the path of each non-deprecated field that references the ``definition``, in schema order.

    :param definition: the name of a definition in the release schema, like "Period"
    """
    return tuple(field.dot_path for field in fields if field.ref == definition and not field.deprecated)
