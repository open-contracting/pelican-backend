import csv
import functools
import threading
from io import StringIO
from pathlib import Path

import cachetools.func
import requests
from requests.adapters import HTTPAdapter, Retry

from pelican.util import settings

CODELIST_DIR = Path(__file__).resolve().parents[1] / "static" / "codelists"

CODELIST_URLS = {
    "documentType.csv": "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/documentType.csv",
    "language.csv": "https://raw.githubusercontent.com/open-contracting/standard/1.2-dev/schema/codelists/language.csv",
    "mediaType.csv": "https://raw.githubusercontent.com/open-contracting/standard/1.2-dev/schema/codelists/mediaType.csv",
}

# Retry on connection errors, read timeouts, request timeouts (408), rate limiting (429) and server errors (5xx).
adapter = HTTPAdapter(
    max_retries=Retry(
        # total=8 and backoff_factor=1 mean at most 246s (<5min), as backoff_max caps the last delay at 120s.
        total=8,
        backoff_factor=1,
        status_forcelist=(408, 429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
)

session = requests.Session()
session.headers["User-Agent"] = settings.USER_AGENT
session.mount("https://", adapter)
session.mount("http://", adapter)

_lock = threading.Lock()


def _read(name: str) -> list[dict[str, str]]:
    with (CODELIST_DIR / name).open() as f:
        return list(csv.DictReader(f))


@cachetools.func.ttl_cache(ttl=86400)  # 1 day
def _remote(url: str) -> list[dict[str, str]]:
    response = session.get(url, timeout=10)
    response.raise_for_status()
    return list(csv.DictReader(StringIO(response.text)))


def _get(url: str) -> list[dict[str, str]]:
    # _remote() re-checks its cache inside the lock, so that a cold cache causes one request, not one per thread.
    with _lock:
        return _remote(url)


def _codes(rows: list[dict[str, str]], key: str) -> tuple[str, ...]:
    return tuple(row[key] for row in rows)


@functools.cache
def get_document_type_section_mapping() -> dict[str, list[str]]:
    return {row["Code"]: row["Section"].split(", ") for row in _read("documentType.csv")}


@cachetools.func.ttl_cache(ttl=86400)  # 1 day
def get_identifier_scheme_codelist() -> tuple[str, ...]:
    return _codes(_get("http://org-id.guide/download.csv"), "code")


@functools.cache
def get_language_codelist() -> tuple[str, ...]:
    return _codes(_read("language.csv"), "Code")


@functools.cache
def get_media_type_codelist() -> tuple[str, ...]:
    return _codes(_read("mediaType.csv"), "Code")


@cachetools.func.ttl_cache(ttl=86400)  # 1 day
def get_ocid_prefix_codelist() -> tuple[str, ...]:
    # https://docs.google.com/spreadsheets/d/1E5ZVhc8VhGOakCq4GegvkyFYT974QQb-sSjvOfaxH7s/pubhtml?gid=506986894&single=true&widget=true
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQP8EwbUhsfxN7Fx7vX3mTA6Y8CXyGi04bHUepdcfxvM6VRVP9f5BWAYEG6MPbnJjWJp-La81DgG8wx/pub?gid=506986894&single=true&output=csv"
    return _codes(_get(url), "OCID")
