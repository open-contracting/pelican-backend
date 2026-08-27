import functools

from contracting_process.field_level.codelist import document_format, document_type, identifier_scheme, language
from contracting_process.field_level.coverage import exists, non_empty
from contracting_process.field_level.format import email, ocid, telephone
from contracting_process.field_level.range import date_time, document_description_length, number
from pelican.util.schema import fields

PAST_DATE_FIELDS = {"date", "dateMet", "dateModified", "datePublished", "dateSigned"}


def _checks(field):
    key = field.path[-1]
    refs = field.refs
    checks = []

    if field.schema.get("format") == "date-time":
        if key in PAST_DATE_FIELDS:
            checks.append((date_time.calculate_past, date_time.name))
        else:
            checks.append((date_time.calculate, date_time.name))

    if not refs:
        if key == "language":
            checks.append((language.calculate, language.name))
        elif key == "ocid":
            checks.append((ocid.calculate, ocid.name))
    elif refs[-1] == "ContactPoint":
        if key == "email":
            checks.append((email.calculate, email.name))
        elif key in {"faxNumber", "telephone"}:
            checks.append((telephone.calculate, telephone.name))
    elif refs[-1] == "Document":
        if key == "description":
            checks.append((document_description_length.calculate, document_description_length.name))
        elif key == "documentType":
            index = 1 if refs[1] == "Implementation" else 0
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
    elif refs[-1] == "Value":  # noqa: SIM102 # consistency
        # A refund reverses the payer and payee, rather than setting a negative amount.
        if key == "amount" and field.path[-3] in {"transactions", "unit"}:
            checks.append((number.calculate, number.name))

    return checks


coverage_checks = [(exists.calculate, exists.name), (non_empty.calculate, non_empty.name)]

definitions = {field.dot_path: _checks(field) for field in fields}
