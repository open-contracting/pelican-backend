import json
from datetime import date, timedelta

import psycopg2
import requests

from tools import settings
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger


def load():
    cursor = get_cursor()

    cursor.execute(
        """
        select valid_on, rates
        from exchange_rates;
        """
    )

    all_rates = cursor.fetchall()
    cursor.close()
    return all_rates


def update_from_fixer_io():
    logger = get_logger()

    BASE = "EUR"
    LINK = "http://data.fixer.io/api/{date_historical}?access_key={access_key}&base={base}&symbols={symbols}"
    CURRENCIES = {
        "AED",
        "AFN",
        "ALL",
        "AMD",
        "ANG",
        "AOA",
        "ARS",
        "AUD",
        "AWG",
        "AZN",
        "BAM",
        "BBD",
        "BDT",
        "BGN",
        "BHD",
        "BIF",
        "BMD",
        "BND",
        "BOB",
        "BRL",
        "BSD",
        "BTC",
        "BTN",
        "BWP",
        "BYR",
        "BYN",
        "BZD",
        "CAD",
        "CDF",
        "CHF",
        "CLF",
        "CLP",
        "CNY",
        "COP",
        "CRC",
        "CUC",
        "CUP",
        "CVE",
        "CZK",
        "DJF",
        "DKK",
        "DOP",
        "DZD",
        "EGP",
        "ERN",
        "ETB",
        "EUR",
        "FJD",
        "FKP",
        "GBP",
        "GEL",
        "GGP",
        "GHS",
        "GIP",
        "GMD",
        "GNF",
        "GTQ",
        "GYD",
        "HKD",
        "HNL",
        "HRK",
        "HTG",
        "HUF",
        "IDR",
        "ILS",
        "IMP",
        "INR",
        "IQD",
        "IRR",
        "ISK",
        "JEP",
        "JMD",
        "JOD",
        "JPY",
        "KES",
        "KGS",
        "KHR",
        "KMF",
        "KPW",
        "KRW",
        "KWD",
        "KYD",
        "KZT",
        "LAK",
        "LBP",
        "LKR",
        "LRD",
        "LSL",
        "LTL",
        "LVL",
        "LYD",
        "MAD",
        "MDL",
        "MGA",
        "MKD",
        "MMK",
        "MNT",
        "MOP",
        "MRO",
        "MUR",
        "MVR",
        "MWK",
        "MXN",
        "MYR",
        "MZN",
        "NAD",
        "NGN",
        "NIO",
        "NOK",
        "NPR",
        "NZD",
        "OMR",
        "PAB",
        "PEN",
        "PGK",
        "PHP",
        "PKR",
        "PLN",
        "PYG",
        "QAR",
        "RON",
        "RSD",
        "RUB",
        "RWF",
        "SAR",
        "SBD",
        "SCR",
        "SDG",
        "SEK",
        "SGD",
        "SHP",
        "SLL",
        "SOS",
        "SRD",
        "STD",
        "SVC",
        "SYP",
        "SZL",
        "THB",
        "TJS",
        "TMT",
        "TND",
        "TOP",
        "TRY",
        "TTD",
        "TWD",
        "TZS",
        "UAH",
        "UGX",
        "USD",
        "UYU",
        "UZS",
        "VEF",
        "VND",
        "VUV",
        "WST",
        "XAF",
        "XAG",
        "XAU",
        "XCD",
        "XDR",
        "XOF",
        "XPF",
        "YER",
        "ZAR",
        "ZMK",
        "ZMW",
        "ZWL",
    }
    CURRENCIES_STR = ",".join(CURRENCIES)
    DATE_FORMAT = "%Y-%m-%d"

    logger.info("Starting currency exchange rates update.")
    cursor = get_cursor()
    cursor.execute(
        """
        select max(valid_on)
        from exchange_rates;
        """
    )
    query_result = cursor.fetchone()

    if query_result is None:
        raise EmptyExchangeRatesTable()

    max_date = query_result[0]

    date_now = date.today()
    logger.info(
        "Last available date is %s. Total of %s day(s) will be updated." % (max_date, (date_now - max_date).days)
    )

    target_date = max_date
    while target_date < date_now:
        try:
            date_str = target_date.strftime(DATE_FORMAT)
            logger.info("Fetching exchange rates for %s.", date_str)

            response = requests.get(
                LINK.format(
                    date_historical=date_str,
                    access_key=settings.FIXER_IO_API_KEY,
                    base=BASE,
                    symbols=CURRENCIES_STR,
                ),
                timeout=10,
            )
            if response.status_code != 200:
                break

        except Exception:
            break

        try:
            data = response.json()
            if not data["success"] or "rates" not in data:
                logger.warning("Failed to successfully fetch exchange rates for %s.", date_str)
                break

            cursor.execute(
                """
                update exchange_rates
                set rates = %(rates)s,
                    modified = current_timestamp
                where valid_on = %(valid_on)s;

                insert into exchange_rates
                (valid_on, rates)
                values
                (%(valid_on)s, %(rates)s)
                on conflict do nothing;
                """,
                {
                    "valid_on": date_str,
                    "rates": json.dumps(data["rates"]),
                },
            )

        except psycopg2.Error:
            rollback()
            break

        else:
            commit()

        target_date += timedelta(days=1)

    cursor.close()
    logger.info("Exchange rates update finished.")


class EmptyExchangeRatesTable(Exception):
    pass
