
import json
import requests
from datetime import datetime, date, timedelta

from tools.db import get_cursor, commit, rollback
from settings.settings import get_param


def load():
    cursor = get_cursor()

    cursor.execute(
        """
        select valid_on, rates
        from exchange_rates;
        """
    )

    return cursor.fetchall()


def update_from_fixer_io():
    BASE = 'EUR'
    LINK = 'http://data.fixer.io/api/{date_historical}?access_key={access_key}&base={base}&symbols={symbols}'
    CURRENCIES = {
        'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF',
        'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTC', 'BTN', 'BWP', 'BYR', 'BYN', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP',
        'CNY', 'COP', 'CRC', 'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD',
        'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR',
        'ILS', 'IMP', 'INR', 'IQD', 'IRR', 'ISK', 'JEP', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW',
        'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LTL', 'LVL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK',
        'MNT', 'MOP', 'MRO', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR',
        'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG',
        'SEK', 'SGD', 'SHP', 'SLL', 'SOS', 'SRD', 'STD', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY',
        'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VEF', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XCD',
        'XDR', 'XOF', 'XPF', 'YER', 'ZAR', 'ZMK', 'ZMW', 'ZWL'
    }
    CURRENCIES_STR = ','.join(CURRENCIES)
    DATE_FORMAT = '%Y-%m-%d'

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

    if date_now <= max_date:
        return

    target_date = max_date
    while True:
        try:
            date_str = target_date.strftime(DATE_FORMAT)

            response = requests.get(
                LINK.format(
                    date_historical=date_str,
                    access_key=get_param('fixer_io_api_key'),
                    base=BASE,
                    symbols=CURRENCIES_STR
                ),
                timeout=10
            )
            if response.status_code != 200:
                break

            data = response.json()
            if not data['success'] or 'rates' not in data:
                break

            cursor.execute(
                """
                insert into exchange_rates (valid_on, rates)
                values ('{}', '{}');
                """.format(date_str, json.dumps(data['rates']))
            )

        except psycopg2.Error:
            rollback()
            break

        except:
            break

        else:
            commit()

        target_date += timedelta(days=1)


class EmptyExchangeRatesTable(Exception):
    pass
