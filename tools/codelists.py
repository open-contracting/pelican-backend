import csv
from collections import defaultdict
from io import StringIO

import cachetools.func
import requests


@cachetools.func.ttl_cache(ttl=86400)  # 1 day
def _get(url):
    response = requests.get(url)
    response.raise_for_status()
    return [row for row in csv.DictReader(StringIO(response.text))]


def _codes(url, key):
    return tuple(row[key] for row in _get(url))


def get_document_type_section_mapping():
    url = "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/documentType.csv"

    mapping = defaultdict(list)
    for row in _get(url):
        mapping[row["Code"]] = row["Section"].split(", ")
    return mapping


def get_identifier_scheme_codelist():
    return _codes("http://org-id.guide/download.csv", "code")


def get_language_codelist():
    url = "https://raw.githubusercontent.com/open-contracting/standard/1.2-dev/schema/codelists/language.csv"
    return _codes(url, "Code")


def get_media_type_codelist():
    url = "https://raw.githubusercontent.com/open-contracting/standard/1.2-dev/schema/codelists/mediaType.csv"
    return _codes(url, "Code")


def get_ocid_prefix_codelist():
    url = "https://docs.google.com/spreadsheets/d/1Am3gq0B77xN034-8hDjhb45wOuq-8qW6kGOdp40rN4M/pub?gid=506986894&single=true&output=csv"  # noqa: E501
    return _codes(url, "OCID")
