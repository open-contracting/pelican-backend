from pelican.util.currency_converter import get_exchange_rates


def test_cache():
    exchange_rates = get_exchange_rates()

    assert get_exchange_rates() is exchange_rates

    get_exchange_rates.cache_clear()

    assert get_exchange_rates() is not exchange_rates
