import json
import logging
from datetime import date, timedelta
from typing import Dict, List, Tuple

import psycopg2
import requests

from tools import settings
from tools.services import commit, get_cursor, rollback

logger = logging.getLogger("pelican.tools.exchange_rates_db")

# Datlab had already downloaded the exchange rates to EUR from another project. Changing the base would require
# re-downloading decades of exchange rates. It makes no difference to the application's logic, as all currency
# operations are performed in USD.
#
# The Basic plan is required to request rates for all base currencies. The Professional plan supports the Time-Series
# Endpoint, which can request rates for multiple dates at once. https://fixer.io/documentation
#
# "The Fixer API delivers EOD / End of Day historical exchange rates, which become available at 00:05am GMT for the
# previous day and are time stamped at one second before midnight." https://fixer.io/faq
FIXER_IO_URL = "https://data.fixer.io/api/{date}?access_key={access_key}&base=EUR&symbols={symbols}"


class EmptyExchangeRatesTable(Exception):
    pass


def load() -> List[Tuple[date, Dict[str, float]]]:
    with get_cursor() as cursor:
        cursor.execute("SELECT valid_on, rates FROM exchange_rates")
        return cursor.fetchall()


def update_from_fixer_io() -> None:
    logger.info("Starting currency exchange rates update.")

    with get_cursor() as cursor:
        cursor.execute("SELECT max(valid_on) FROM exchange_rates")
        query_result = cursor.fetchone()

        if query_result is None:
            raise EmptyExchangeRatesTable

        max_date = query_result[0]
        date_now = date.today()
        length = (date_now - max_date).days

        if not length:
            logger.info("Last available date is %s. Nothing to update.", max_date)
            return

        logger.info("Last available date is %s. %s date(s) will be updated.", max_date, length)
        access_key = settings.FIXER_IO_API_KEY

        try:
            # To get the list of currencies for testing:
            # curl 'https://data.fixer.io/api/symbols?access_key=' | jq '.symbols | keys | join(",")'
            response = requests.get(f"https://data.fixer.io/api/symbols?access_key={access_key}")
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error("Couldn't retrieve currency symbols: %s", e)
            return

        data = response.json()
        if not data["success"] or "symbols" not in data:
            logger.error("API request for currency symbols did not succeed: %r", data)
            return

        symbols = ",".join(data["symbols"])

        target_date = max_date
        # Don't retrieve today's exchange rates, because the data might be incomplete.
        while target_date < date_now:
            try:
                date_str = target_date.strftime("%Y-%m-%d")
                logger.info("Fetching exchange rates for %s.", date_str)

                response = requests.get(
                    FIXER_IO_URL.format(date=date_str, access_key=access_key, symbols=symbols),
                    timeout=10,
                )
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error("Couldn't retrieve currency rates: %s", e)
                break

            try:
                data = response.json()
                if not data["success"] or "rates" not in data:
                    logger.error("API request for currency rates on %s did not succeed.", date_str)
                    break

                cursor.execute(
                    """\
                    UPDATE exchange_rates
                    SET rates = %(rates)s, modified = current_timestamp
                    WHERE valid_on = %(valid_on)s;

                    INSERT INTO exchange_rates (valid_on, rates)
                    VALUES (%(valid_on)s, %(rates)s)
                    ON CONFLICT DO NOTHING;
                    """,
                    {"valid_on": date_str, "rates": json.dumps(data["rates"])},
                )
            except psycopg2.Error as e:
                logger.error("Couldn't insert exchange rate: %s", e)
                rollback()
                break

            else:
                commit()

            target_date += timedelta(days=1)

        logger.info("Exchange rates update finished.")
