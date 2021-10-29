import functools
from pathlib import Path

import jsonref

from contracting_process.field_level.codelist import document_format, document_type, identifier_scheme, language
from contracting_process.field_level.coverage import exists, non_empty
from contracting_process.field_level.format import email, ocid, telephone
from contracting_process.field_level.range import date_time, document_description_length, number

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _descend(value, new_path, dot_path, refs):
    if hasattr(value, "__reference__"):
        refs += (value.__reference__["$ref"][14:],)  # remove #/definitions/

    yield dot_path, []
    yield from _definitions(value["properties"], path=new_path, refs=refs)


def _definitions(properties, path=None, refs=None):
    if path is None:
        path = ()
    if refs is None:
        refs = ()

    for key, value in properties.items():
        new_path = path + (key,)
        dot_path = ".".join(new_path)

        if "object" in value["type"] and "properties" in value:
            yield from _descend(value, new_path, dot_path, refs)
        elif (
            "array" in value["type"]
            and "items" in value
            and "object" in value["items"]["type"]
            and "properties" in value["items"]
        ):
            yield from _descend(value["items"], new_path, dot_path, refs)
        else:
            checks = []

            if "format" in value and value["format"] == "date-time":
                checks.append((date_time.calculate, date_time.name))

            if not refs:
                if key == "language":
                    checks.append((language.calculate, language.name))
                elif key == "ocid":
                    checks.append((ocid.calculate, ocid.name))
            elif refs[-1] == "ContactPoint":
                if key == "email":
                    checks.append((email.calculate, email.name))
                elif key in ("faxNumber", "telephone"):
                    checks.append((telephone.calculate, telephone.name))
            elif refs[-1] == "Document":
                if key == "description":
                    checks.append((document_description_length.calculate, document_description_length.name))
                elif key == "documentType":
                    if refs[1] == "Implementation":
                        index = 1
                    else:
                        index = 0
                    checks.append(
                        (
                            functools.partial(document_type.calculate_section, section=refs[index].lower()),
                            document_type.name,
                        )
                    )
                elif key == "format":
                    checks.append((document_format.calculate, document_format.name))
                elif key == "language":
                    checks.append((language.calculate, language.name))
            elif refs[-1] == "Identifier":
                if key == "scheme":
                    checks.append((identifier_scheme.calculate, identifier_scheme.name))
            elif refs[-1] == "Item":
                if key == "quantity":
                    checks.append((number.calculate, number.name))
            elif refs[-1] == "Period":
                if key == "durationInDays":
                    checks.append((number.calculate, number.name))
            elif refs[-1] == "Tender":
                if key == "numberOfTenderers":
                    checks.append((number.calculate, number.name))
            elif refs[-1] == "Value":
                if key == "amount" and new_path[-3] in ("transactions", "unit"):
                    checks.append((number.calculate, number.name))

            yield dot_path, checks


with (BASE_DIR / "pelican" / "static" / "release-schema.json").open() as f:
    schema = jsonref.load(f)

coverage_checks = [(exists.calculate, exists.name), (non_empty.calculate, non_empty.name)]

definitions = dict(_definitions(schema["properties"]))
