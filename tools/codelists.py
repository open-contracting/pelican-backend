import csv
from io import StringIO

import cachetools.func
import requests


@cachetools.func.ttl_cache(ttl=86400)  # 1 day
def _get(url, key):
    response = requests.get(url)
    response.raise_for_status()
    reader = csv.DictReader(StringIO(response.text))

    return tuple(row[key] for row in reader)


def get_identifier_scheme_codelist():
    return _get("http://org-id.guide/download.csv", "code")


def get_language_codelist():
    return _get(
        "https://raw.githubusercontent.com/open-contracting/standard/1.2-dev/schema/codelists/language.csv", "Code"
    )


def get_media_type_codelist():
    return _get(
        "https://raw.githubusercontent.com/open-contracting/standard/1.2-dev/schema/codelists/mediaType.csv", "Code"
    )


def get_ocid_prefix_codelist():
    return _get(
        "https://docs.google.com/spreadsheets/d/1Am3gq0B77xN034-8hDjhb45wOuq-8qW6kGOdp40rN4M/pub?gid=506986894&single=true&output=csv",  # noqa: E501
        "OCID",
    )
