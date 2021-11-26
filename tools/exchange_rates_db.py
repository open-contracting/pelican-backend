import json
from datetime import date, timedelta

import psycopg2
import requests

from tools import settings
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger

LINK = "http://data.fixer.io/api/{date_historical}?access_key={access_key}&base={base}&symbols={symbols}"
CURRENCIES = (
    "AED,AFN,ALL,AMD,ANG,AOA,ARS,AUD,AWG,AZN,BAM,BBD,BDT,BGN,BHD,BIF,BMD,BND,BOB,BRL,BSD,BTC,BTN,BWP,BYR,BYN,BZD,CAD,"
    "CDF,CHF,CLF,CLP,CNY,COP,CRC,CUC,CUP,CVE,CZK,DJF,DKK,DOP,DZD,EGP,ERN,ETB,EUR,FJD,FKP,GBP,GEL,GGP,GHS,GIP,GMD,GNF,"
    "GTQ,GYD,HKD,HNL,HRK,HTG,HUF,IDR,ILS,IMP,INR,IQD,IRR,ISK,JEP,JMD,JOD,JPY,KES,KGS,KHR,KMF,KPW,KRW,KWD,KYD,KZT,LAK,"
    "LBP,LKR,LRD,LSL,LTL,LVL,LYD,MAD,MDL,MGA,MKD,MMK,MNT,MOP,MRO,MUR,MVR,MWK,MXN,MYR,MZN,NAD,NGN,NIO,NOK,NPR,NZD,OMR,"
    "PAB,PEN,PGK,PHP,PKR,PLN,PYG,QAR,RON,RSD,RUB,RWF,SAR,SBD,SCR,SDG,SEK,SGD,SHP,SLL,SOS,SRD,STD,SVC,SYP,SZL,THB,TJS,"
    "TMT,TND,TOP,TRY,TTD,TWD,TZS,UAH,UGX,USD,UYU,UZS,VEF,VND,VUV,WST,XAF,XAG,XAU,XCD,XDR,XOF,XPF,YER,ZAR,ZMK,ZMW,ZWL"
)


def load():
    with get_cursor() as cursor:
        cursor.execute("SELECT valid_on, rates FROM exchange_rates")
        return cursor.fetchall()


def update_from_fixer_io():
    logger = get_logger()
    logger.info("Starting currency exchange rates update.")

    with get_cursor() as cursor:
        cursor.execute("SELECT max(valid_on) FROM exchange_rates")
        query_result = cursor.fetchone()

        if query_result is None:
            raise EmptyExchangeRatesTable

        max_date = query_result[0]
        date_now = date.today()
        logger.info("Last available date is %s. %s day(s) will be updated.", max_date, (date_now - max_date).days)

        target_date = max_date
        while target_date < date_now:
            try:
                date_str = target_date.strftime("%Y-%m-%d")
                logger.info("Fetching exchange rates for %s.", date_str)

                response = requests.get(
                    LINK.format(
                        date_historical=date_str,
                        access_key=settings.FIXER_IO_API_KEY,
                        # Datlab had already downloaded the exchange rates to EUR from another project. Changing the
                        # base would require re-downloading decades of exchange rates. It makes no difference to the
                        # application's logic, as all currency operations are performed in USD.
                        base="EUR",
                        symbols=CURRENCIES,
                    ),
                    timeout=10,
                )
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error("Couldn't connect to fixer.io: %s", e)
                break

            try:
                data = response.json()
                if not data["success"] or "rates" not in data:
                    logger.error("Failed to successfully fetch exchange rates for %s.", date_str)
                    break

                cursor.execute(
                    """
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


class EmptyExchangeRatesTable(Exception):
    pass
